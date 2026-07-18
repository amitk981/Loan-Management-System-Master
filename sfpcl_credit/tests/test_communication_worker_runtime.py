from unittest.mock import patch
from unittest import skipUnless
from datetime import timedelta
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Lock
import uuid

from django.db import (
    close_old_connections,
    connection,
    connections,
    transaction,
)
from django.test import (
    SimpleTestCase,
    TestCase,
    TransactionTestCase,
    override_settings,
)
from django.utils import timezone

from sfpcl_credit.communications.models import (
    Communication,
    CommunicationDeliveryJob,
    CommunicationDeliveryOutbox,
    CommunicationException,
    Notification,
)
from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
    CommunicationDispatchConflict,
    CommunicationExceptionAccessDenied,
)
from sfpcl_credit.communications.adapters import FakeEmailDeliveryAdapter
from sfpcl_credit.identity.models import AuditLog, Permission, RolePermission
from sfpcl_credit.processes.communication_delivery import execute_communication_job
from sfpcl_credit.processes.tasks import (
    dispatch_due_communication_jobs,
    execute_communication_delivery_job,
)
from sfpcl_credit.processes.disbursement_advice_delivery import (
    send_disbursement_advice_now,
)
from sfpcl_credit.disbursements.modules.disbursement_advice import (
    DisbursementAdviceConflict,
)
from sfpcl_credit.workflows.models import WorkflowEvent
from sfpcl_credit.tests import test_communications_api as communication_fixtures
from sfpcl_credit.tests import test_disbursement_advice_api as advice_fixtures


class CommunicationWorkerRuntimeTests(SimpleTestCase):
    def test_configured_celery_app_discovers_worker_and_periodic_tasks(self):
        from sfpcl_credit.config.celery import app

        app.loader.import_default_modules()

        self.assertIn("communications.execute_job", app.tasks)
        self.assertIn("communications.dispatch_due_jobs", app.tasks)
        self.assertEqual(
            app.conf.beat_schedule["communications-dispatch-due-jobs"]["task"],
            "communications.dispatch_due_jobs",
        )

    def test_celery_entries_delegate_only_to_public_communications_interfaces(self):
        job_id = uuid.uuid4()
        task_result = {"communication_job_id": str(job_id), "delivery_status": "sent"}
        due_result = [task_result]
        with (
            patch.object(
                CommunicationDispatcher,
                "execute_task",
                return_value=task_result,
                create=True,
            ) as execute_owner,
            patch.object(
                CommunicationDispatcher,
                "run_due_jobs",
                return_value=due_result,
                create=True,
            ) as due_owner,
        ):
            executed = execute_communication_delivery_job(job_id)
            due = dispatch_due_communication_jobs()

        self.assertEqual(executed, task_result)
        self.assertEqual(due, due_result)
        execute_owner.assert_called_once()
        due_owner.assert_called_once()
        self.assertTrue(callable(execute_owner.call_args.kwargs["executor"]))
        self.assertTrue(callable(due_owner.call_args.kwargs["executor"]))


class CommunicationWorkerQueueTests(TestCase):
    def setUp(self):
        communication_fixtures.CommunicationApiTests.setUp(self)

    _auth_headers = communication_fixtures.CommunicationApiTests._auth_headers
    _access_token = communication_fixtures.CommunicationApiTests._access_token
    _send_payload = communication_fixtures.CommunicationApiTests._send_payload

    def _generic_exception_with_advice_only_permission(self, idempotency_key):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key=idempotency_key),
            )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(attempts=2)
        CommunicationDispatcher.start_job(job.pk)
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            lease_expires_at=timezone.now()
        )
        CommunicationDispatcher.retry_failed(limit=1)
        RolePermission.objects.filter(
            role=self.role,
            permission__permission_code="communications.communication.send",
        ).delete()
        advice_permission, _ = Permission.objects.get_or_create(
            permission_code="finance.disbursement.send_advice",
            defaults={
                "permission_name": "Send disbursement advice",
                "module_name": "finance",
                "risk_level": "high",
            },
        )
        RolePermission.objects.get_or_create(
            role=self.role, permission=advice_permission
        )
        return job.delivery_exception

    def test_generic_exception_rejects_advice_only_permission_on_read(self):
        exception = self._generic_exception_with_advice_only_permission(
            "generic-exception-read-authority"
        )

        response = self.client.get(
            f"/api/v1/communication-exceptions/{exception.pk}/",
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 403, response.content)

    def test_generic_exception_rejects_advice_only_permission_on_resolution(self):
        exception = self._generic_exception_with_advice_only_permission(
            "generic-exception-resolution-authority"
        )

        response = self.client.post(
            f"/api/v1/communication-exceptions/{exception.pk}/resolve/",
            {"resolution_action": "manual_closed", "resolution_version": 1},
            content_type="application/json",
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 403, response.content)

    def test_revoked_and_inactive_generic_owner_are_zero_write(self):
        exception = self._generic_exception_with_advice_only_permission(
            "generic-exception-revoked-inactive"
        )
        request = SimpleNamespace(headers={}, META={})

        self.assertEqual(
            CommunicationDispatcher.exception_evidence(actor=self.user), []
        )
        with self.assertRaises(CommunicationExceptionAccessDenied):
            CommunicationDispatcher.resolve_exception(
                actor=self.user,
                exception_id=exception.pk,
                expected_version=1,
                resolution_action="manual_closed",
                request=request,
            )

        generic_permission = Permission.objects.get(
            permission_code="communications.communication.send"
        )
        RolePermission.objects.get_or_create(
            role=self.role, permission=generic_permission
        )
        self.user.status = "inactive"
        self.user.save(update_fields=["status"])
        self.assertEqual(
            CommunicationDispatcher.exception_evidence(actor=self.user), []
        )
        with self.assertRaises(CommunicationExceptionAccessDenied):
            CommunicationDispatcher.resolve_exception(
                actor=self.user,
                exception_id=exception.pk,
                expected_version=1,
                resolution_action="manual_closed",
                request=request,
            )
        exception.refresh_from_db()
        self.assertIsNone(exception.resolved_at)
        self.assertFalse(
            AuditLog.objects.filter(
                action="communications.exception.resolved", entity_id=exception.pk
            ).exists()
        )

    def test_committed_queue_publishes_one_job_signature(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ) as signature:
            with self.captureOnCommitCallbacks(execute=True) as callbacks:
                response = self.client.post(
                    communication_fixtures.COMMUNICATION_SEND_URL,
                    data=self._send_payload(),
                    content_type="application/json",
                    headers=self._auth_headers(idempotency_key="worker-on-commit"),
                )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(len(callbacks), 1)
        job = CommunicationDeliveryJob.objects.get()
        signature.assert_called_once_with(args=[str(job.pk)])
        signature.return_value.apply_async.assert_called_once_with()

    def test_stale_running_job_recovers_without_resetting_attempts(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key="worker-stale-recovery"),
            )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        stale_at = timezone.now() - timedelta(minutes=1)
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            status=CommunicationDeliveryJob.STATUS_RUNNING,
            attempts=1,
            started_at=stale_at - timedelta(minutes=5),
            claim_token="62ae79db-542c-4b6f-909e-5aeef69ec854",
            lease_expires_at=stale_at,
        )

        due = CommunicationDispatcher.retry_failed(limit=10)

        job.refresh_from_db()
        self.assertEqual(due, [job.pk])
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_RETRYING)
        self.assertEqual(job.attempts, 1)
        self.assertEqual(job.recovery_count, 1)
        self.assertIsNotNone(job.last_recovered_at)
        self.assertIsNone(job.claim_token)
        self.assertIsNone(job.lease_expires_at)

    def test_final_attempt_crash_becomes_failed_with_operator_task(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key="worker-final-crash"),
            )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(attempts=2)
        claim = CommunicationDispatcher.start_job(job.pk)
        self.assertEqual(claim.attempts, 3)
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            lease_expires_at=timezone.now()
        )

        due = CommunicationDispatcher.retry_failed(limit=1)
        repeated_due = CommunicationDispatcher.retry_failed(limit=1)

        job.refresh_from_db()
        self.assertEqual(due, [])
        self.assertEqual(repeated_due, [])
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_FAILED)
        self.assertEqual(job.attempts, job.max_attempts)
        self.assertEqual(job.recovery_count, 1)
        exception = CommunicationException.objects.get(job=job)
        self.assertEqual(exception.retry_count, job.max_attempts)
        self.assertEqual(exception.last_error_code, "worker_crash")
        self.assertEqual(exception.assigned_owner_id, job.actor_id)
        self.assertIsNone(exception.resolved_at)
        self.assertTrue(
            Notification.objects.filter(
                notification_type="communication_job_failed",
                related_entity_type="communication_exception",
                related_entity_id=exception.pk,
            ).exists()
        )
        self.assertEqual(CommunicationException.objects.filter(job=job).count(), 1)
        self.assertEqual(
            Notification.objects.filter(
                notification_type="communication_job_failed",
                related_entity_type="communication_exception",
                related_entity_id=exception.pk,
            ).count(),
            1,
        )
        self.assertEqual(
            AuditLog.objects.filter(
                action="communications.exception.created",
                entity_type="communication_exception",
                entity_id=exception.pk,
            ).count(),
            1,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="CommunicationExceptionResolution",
                entity_type="communication_exception",
                entity_id=exception.pk,
                to_state="open",
            ).count(),
            1,
        )
        task = Notification.objects.get(
            notification_type="communication_job_failed",
            related_entity_type="communication_exception",
            related_entity_id=exception.pk,
        )
        detail = self.client.get(task.action_url, headers=self._auth_headers())
        self.assertEqual(detail.status_code, 200, detail.content)
        self.assertEqual(
            detail.json()["data"]["communication_exception_id"], str(exception.pk)
        )

    def test_already_exhausted_retrying_job_is_terminalised_once(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key="already-exhausted"),
            )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            status=CommunicationDeliveryJob.STATUS_RETRYING,
            attempts=job.max_attempts,
            last_failure_code="worker_crash",
            recovery_count=1,
            last_recovered_at=timezone.now(),
            next_attempt_at=timezone.now(),
        )

        first = CommunicationDispatcher.retry_failed(limit=1)
        second = CommunicationDispatcher.retry_failed(limit=1)

        job.refresh_from_db()
        self.assertEqual(first, [])
        self.assertEqual(second, [])
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_FAILED)
        self.assertEqual(job.attempts, job.max_attempts)
        self.assertEqual(job.recovery_count, 1)
        self.assertEqual(CommunicationException.objects.filter(job=job).count(), 1)

    def test_recovered_job_rejects_the_expired_worker_claim(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key="worker-fenced-recovery"),
            )
        job = CommunicationDeliveryJob.objects.get()
        expired_worker = CommunicationDispatcher.start_job(job.pk)
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            lease_expires_at=timezone.now() - timedelta(seconds=1)
        )
        CommunicationDispatcher.retry_failed(limit=1)
        replacement_worker = CommunicationDispatcher.start_job(job.pk)

        with self.assertRaises(CommunicationDispatchConflict):
            CommunicationDispatcher.defer_job(
                job.pk,
                "worker_crash",
                claim_token=expired_worker.claim_token,
            )

        job.refresh_from_db()
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_RUNNING)
        self.assertEqual(job.claim_token, replacement_worker.claim_token)
        self.assertNotEqual(expired_worker.claim_token, replacement_worker.claim_token)

    def test_rolled_back_queue_never_publishes_a_signature(self):
        request = SimpleNamespace(
            headers={"X-Request-ID": "rollback-request"},
            META={"REMOTE_ADDR": "127.0.0.1", "HTTP_USER_AGENT": "test"},
        )
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ) as signature:
            with self.captureOnCommitCallbacks(execute=True) as callbacks:
                with self.assertRaises(RuntimeError):
                    with transaction.atomic():
                        row = CommunicationDispatcher.create_from_template(
                            actor=self.user,
                            template_code=self.template.template_code,
                            recipient={
                                "party_type": "borrower",
                                "party_id": self.recipient_party_id,
                                "address": "rollback@example.com",
                                "channel": "email",
                            },
                            context={
                                "merge_data": {
                                    "application_reference_number": "LA-ROLLBACK",
                                    "borrower_name": "Rollback Borrower",
                                },
                                "idempotency_key": "worker-rollback",
                                "request": request,
                            },
                            related_entity={
                                "type": "loan_application",
                                "id": self.related_entity_id,
                            },
                        )
                        CommunicationDispatcher.send(
                            communication_id=row.pk,
                            idempotency_key="worker-rollback",
                        )
                        raise RuntimeError("force rollback")

        self.assertEqual(callbacks, [])
        signature.assert_not_called()
        self.assertEqual(CommunicationDeliveryJob.objects.count(), 0)

    def test_publish_crash_leaves_committed_job_reachable_by_periodic_recovery(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ) as signature:
            signature.return_value.apply_async.side_effect = RuntimeError(
                "simulated broker publish crash"
            )
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(
                    communication_fixtures.COMMUNICATION_SEND_URL,
                    data=self._send_payload(),
                    content_type="application/json",
                    headers=self._auth_headers(
                        idempotency_key="worker-publish-crash"
                    ),
                )

        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_QUEUED)
        self.assertEqual(CommunicationDispatcher.retry_failed(limit=1), [job.pk])

    @override_settings(
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_TASK_EAGER_PROPAGATES=True,
        COMMUNICATION_EMAIL_ADAPTER=(
            "sfpcl_credit.communications.adapters.FakeEmailDeliveryAdapter"
        )
    )
    def test_eager_worker_executes_committed_generic_job_without_network(self):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key="worker-eager-generic"),
            )

        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_SENT)
        self.assertEqual(job.attempts, 1)
        self.assertTrue(job.provider_external_message_id.startswith("fake:"))

    def test_operator_job_evidence_exposes_only_safe_runtime_facts(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key="operator-safe-evidence"),
            )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        CommunicationDispatcher.start_job(job.pk)

        evidence = CommunicationDispatcher.job_evidence(limit=10)

        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["status"], "running")
        self.assertFalse(evidence[0]["recovered"])
        self.assertEqual(
            set(evidence[0]),
            {
                "communication_job_id",
                "job_kind",
                "status",
                "attempts",
                "max_attempts",
                "next_attempt_at",
                "started_at",
                "completed_at",
                "lease_expires_at",
                "recovery_count",
                "last_recovered_at",
                "last_failure_code",
                "recovered",
                "operator_attention_required",
            },
        )
        safe_text = str(evidence)
        for secret in (
            "borrower@sfpcl.example",
            "Sanction LA-2026-0001",
            "operator-safe-evidence",
            str(self.user.pk),
            str(self.related_entity_id),
        ):
            self.assertNotIn(secret, safe_text)

    def test_exception_evidence_exposes_only_safe_review_facts(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key="exception-safe-evidence"),
            )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(attempts=2)
        CommunicationDispatcher.start_job(job.pk)
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            lease_expires_at=timezone.now()
        )
        CommunicationDispatcher.retry_failed(limit=1)

        evidence = CommunicationDispatcher.exception_evidence(
            actor=self.user, limit=10
        )

        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["provider_code"], "email")
        self.assertEqual(
            set(evidence[0]),
            {
                "communication_exception_id",
                "provider_code",
                "job_type",
                "related_entity_type",
                "related_entity_id",
                "last_error_code",
                "retry_count",
                "assigned_owner",
                "resolution_action",
                "resolved_by",
                "resolved_at",
                "resolution_version",
            },
        )
        self.assertEqual(evidence[0]["assigned_owner"], "current_user")
        safe_text = str(evidence)
        for secret in (
            "borrower@sfpcl.example",
            "Sanction LA-2026-0001",
            "exception-safe-evidence",
            str(self.user.pk),
            "127.0.0.1",
        ):
            self.assertNotIn(secret, safe_text)

    def test_assigned_owner_can_manually_resolve_without_fabricating_delivery(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key="exception-manual-close"),
            )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(attempts=2)
        CommunicationDispatcher.start_job(job.pk)
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            lease_expires_at=timezone.now()
        )
        CommunicationDispatcher.retry_failed(limit=1)
        exception = CommunicationException.objects.get(job=job)
        request = SimpleNamespace(
            headers={},
            META={"REMOTE_ADDR": "127.0.0.1", "HTTP_USER_AGENT": "test"},
        )

        result = CommunicationDispatcher.resolve_exception(
            actor=self.user,
            exception_id=exception.pk,
            expected_version=1,
            resolution_action="manual_closed",
            request=request,
        )

        exception.refresh_from_db()
        job.refresh_from_db()
        communication = Communication.objects.get(pk=job.communication_id)
        self.assertEqual(result["resolution_action"], "manual_closed")
        self.assertEqual(exception.resolved_by, self.user)
        self.assertIsNotNone(exception.resolved_at)
        self.assertEqual(exception.resolution_version, 2)
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_FAILED)
        self.assertEqual(job.attempts, job.max_attempts)
        self.assertEqual(communication.delivery_status, Communication.DELIVERY_PENDING)
        self.assertTrue(
            AuditLog.objects.filter(
                action="communications.exception.resolved",
                entity_type="communication_exception",
                entity_id=exception.pk,
            ).exists()
        )
        self.assertTrue(
            WorkflowEvent.objects.filter(
                workflow_name="CommunicationExceptionResolution",
                entity_type="communication_exception",
                entity_id=exception.pk,
                from_state="open",
                to_state="resolved",
            ).exists()
        )

    def test_assigned_owner_can_reach_redacted_exception_queue_over_http(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key="exception-http-list"),
            )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(attempts=2)
        CommunicationDispatcher.start_job(job.pk)
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            lease_expires_at=timezone.now()
        )
        CommunicationDispatcher.retry_failed(limit=1)

        response = self.client.get(
            "/api/v1/communication-exceptions/", headers=self._auth_headers()
        )

        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        self.assertEqual(len(payload["data"]), 1)
        self.assertEqual(payload["data"][0]["retry_count"], 3)
        self.assertNotIn("borrower@sfpcl.example", str(payload))
        self.assertNotIn("exception-http-list", str(payload))

    def test_exception_collection_is_strict_stable_and_truthfully_paginated(self):
        created = timezone.now() - timedelta(days=1)
        jobs = []
        for index in range(105):
            jobs.append(
                CommunicationDeliveryJob(
                    communication_job_id=uuid.uuid4(),
                    communication_id=uuid.uuid4(),
                    job_kind=CommunicationDeliveryJob.KIND_GENERIC,
                    idempotency_key=f"exception-page-{index}",
                    actor_id=self.user.pk,
                    actor_role_code=self.role.role_code,
                    actor_team_codes=[],
                    request_id=f"exception-page-request-{index}",
                    request_payload_digest=f"{index:064x}",
                    status=CommunicationDeliveryJob.STATUS_FAILED,
                    attempts=3,
                    max_attempts=3,
                    last_failure_code="provider_rejected",
                    next_attempt_at=created,
                    completed_at=created,
                    created_at=created + timedelta(seconds=index),
                )
            )
        CommunicationDeliveryJob.objects.bulk_create(jobs)
        exceptions = [
            CommunicationException(
                communication_exception_id=uuid.uuid4(),
                job=job,
                provider_code="email",
                job_type=job.job_kind,
                related_entity_type="loan_application",
                related_entity_id=uuid.uuid4(),
                last_error_code=job.last_failure_code,
                retry_count=job.attempts,
                assigned_owner=self.user,
                created_at=job.created_at,
            )
            for job in jobs
        ]
        CommunicationException.objects.bulk_create(exceptions)
        expected_second_page = [
            str(row.pk)
            for row in sorted(
                exceptions,
                key=lambda row: (row.created_at, row.pk),
                reverse=True,
            )[100:]
        ]

        response = self.client.get(
            "/api/v1/communication-exceptions/?page=2&page_size=100",
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        self.assertEqual(
            [row["communication_exception_id"] for row in payload["data"]],
            expected_second_page,
        )
        self.assertEqual(
            payload["pagination"],
            {
                "page": 2,
                "page_size": 100,
                "total_count": 105,
                "total_pages": 2,
                "has_next": False,
                "has_previous": True,
            },
        )
        self.assertNotIn("exception-page-", str(payload))
        for query in ("page=0", "page_size=101", "ordering=created_at"):
            with self.subTest(query=query):
                invalid = self.client.get(
                    f"/api/v1/communication-exceptions/?{query}",
                    headers=self._auth_headers(),
                )
                self.assertEqual(invalid.status_code, 400, invalid.content)
                self.assertEqual(invalid.json()["error"]["code"], "VALIDATION_ERROR")

    def test_exception_resolution_http_is_authorised_policy_bound_and_stale_safe(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key="exception-http-resolve"),
            )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(attempts=2)
        CommunicationDispatcher.start_job(job.pk)
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            lease_expires_at=timezone.now()
        )
        CommunicationDispatcher.retry_failed(limit=1)
        exception = CommunicationException.objects.get(job=job)
        url = f"/api/v1/communication-exceptions/{exception.pk}/resolve/"

        denied = self.client.post(
            url,
            {"resolution_action": "manual_closed", "resolution_version": 1},
            content_type="application/json",
            headers=self._auth_headers(
                email="priya.communications@sfpcl.example",
                password="PlainPass123!",
            ),
        )
        retry = self.client.post(
            url,
            {"resolution_action": "retry", "resolution_version": 1},
            content_type="application/json",
            headers=self._auth_headers(),
        )
        resolved = self.client.post(
            url,
            {"resolution_action": "manual_closed", "resolution_version": 1},
            content_type="application/json",
            headers=self._auth_headers(),
        )
        stale = self.client.post(
            url,
            {"resolution_action": "manual_closed", "resolution_version": 1},
            content_type="application/json",
            headers=self._auth_headers(),
        )

        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(retry.status_code, 409, retry.content)
        self.assertEqual(resolved.status_code, 200, resolved.content)
        self.assertEqual(resolved.json()["data"]["resolution_version"], 2)
        self.assertEqual(stale.status_code, 409, stale.content)
        self.assertEqual(
            AuditLog.objects.filter(
                action="communications.exception.resolved", entity_id=exception.pk
            ).count(),
            1,
        )

    def test_cross_owner_with_exact_permission_is_nondisclosing_and_zero_write(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key="exception-cross-owner"),
            )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(attempts=2)
        CommunicationDispatcher.start_job(job.pk)
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            lease_expires_at=timezone.now()
        )
        CommunicationDispatcher.retry_failed(limit=1)
        exception = CommunicationException.objects.get(job=job)
        permission = Permission.objects.get(
            permission_code="communications.communication.send"
        )
        RolePermission.objects.get_or_create(
            role=self.read_only_role, permission=permission
        )
        headers = self._auth_headers(
            email="ravi.communications@sfpcl.example",
            password="ReaderPass123!",
        )

        collection = self.client.get(
            "/api/v1/communication-exceptions/", headers=headers
        )
        detail = self.client.get(
            f"/api/v1/communication-exceptions/{exception.pk}/", headers=headers
        )
        resolution = self.client.post(
            f"/api/v1/communication-exceptions/{exception.pk}/resolve/",
            {"resolution_action": "manual_closed", "resolution_version": 1},
            content_type="application/json",
            headers=headers,
        )

        self.assertEqual(collection.status_code, 200, collection.content)
        self.assertEqual(collection.json()["data"], [])
        self.assertEqual(detail.status_code, 404, detail.content)
        self.assertEqual(resolution.status_code, 403, resolution.content)
        exception.refresh_from_db()
        self.assertIsNone(exception.resolved_at)
        self.assertFalse(
            AuditLog.objects.filter(
                action="communications.exception.resolved", entity_id=exception.pk
            ).exists()
        )

    def test_recovery_reuses_retained_provider_acceptance_without_redispatch(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key="accepted-crash-recovery"),
            )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        original_digest = CommunicationDispatcher._generic_payload_digest_from_row(
            Communication.objects.get(pk=job.communication_id)
        )
        with patch.object(
            CommunicationDispatcher,
            "_generic_payload_digest_from_row",
            side_effect=RuntimeError("simulated crash after provider acceptance"),
        ):
            with self.assertRaises(RuntimeError):
                execute_communication_job(job.pk, adapter=FakeEmailDeliveryAdapter())
        job.refresh_from_db()
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_RUNNING)
        self.assertIsNotNone(job.provider_external_message_id)
        self.assertEqual(job.request_payload_digest, original_digest)
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            lease_expires_at=timezone.now() - timedelta(seconds=1)
        )
        CommunicationDispatcher.retry_failed(limit=1)

        class NoRedispatchAdapter:
            def send_email(self, payload, idempotency_key):
                raise AssertionError("accepted evidence must not be sent again")

        recovered = execute_communication_job(job.pk, adapter=NoRedispatchAdapter())

        self.assertEqual(recovered["delivery_status"], "sent")
        job.refresh_from_db()
        self.assertEqual(job.attempts, 2)
        self.assertEqual(job.recovery_count, 1)

    def test_final_accepted_crash_closes_exception_without_redispatch(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key="accepted-final-crash"),
            )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(attempts=2)
        with patch.object(
            CommunicationDispatcher,
            "_generic_payload_digest_from_row",
            side_effect=RuntimeError("simulated final crash after provider acceptance"),
        ):
            with self.assertRaises(RuntimeError):
                execute_communication_job(job.pk, adapter=FakeEmailDeliveryAdapter())
        job.refresh_from_db()
        self.assertIsNotNone(job.provider_external_message_id)
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            lease_expires_at=timezone.now() - timedelta(seconds=1)
        )
        self.assertEqual(CommunicationDispatcher.retry_failed(limit=1), [])
        exception = CommunicationException.objects.get(job=job)

        class NoRedispatchAdapter:
            calls = 0

            def send_email(self, payload, idempotency_key):
                self.calls += 1
                raise AssertionError("accepted evidence must not be sent again")

        adapter = NoRedispatchAdapter()
        with self.assertRaises(CommunicationDispatchConflict):
            execute_communication_job(job.pk, adapter=adapter)
        CommunicationDispatcher.resolve_exception(
            actor=self.user,
            exception_id=exception.pk,
            expected_version=1,
            resolution_action="manual_closed",
            request=SimpleNamespace(headers={}, META={}),
        )

        job.refresh_from_db()
        exception.refresh_from_db()
        communication = Communication.objects.get(pk=job.communication_id)
        self.assertEqual(adapter.calls, 0)
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_FAILED)
        self.assertEqual(job.attempts, job.max_attempts)
        self.assertEqual(communication.delivery_status, Communication.DELIVERY_PENDING)
        self.assertEqual(exception.resolution_action, "manual_closed")

    def test_worker_crash_before_provider_is_recovered_for_one_safe_send(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key="pre-provider-crash"),
            )
        job = CommunicationDeliveryJob.objects.get()

        class CrashedWorkerAdapter:
            def send_email(self, payload, idempotency_key):
                raise RuntimeError("simulated process death before provider acceptance")

        with self.assertRaises(RuntimeError):
            execute_communication_job(job.pk, adapter=CrashedWorkerAdapter())
        job.refresh_from_db()
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_RUNNING)
        self.assertIsNone(job.provider_external_message_id)
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            lease_expires_at=timezone.now() - timedelta(seconds=1)
        )
        CommunicationDispatcher.retry_failed(limit=1)

        recovered = execute_communication_job(
            job.pk, adapter=FakeEmailDeliveryAdapter()
        )

        self.assertEqual(recovered["delivery_status"], "sent")
        job.refresh_from_db()
        self.assertEqual(job.attempts, 2)
        self.assertEqual(job.recovery_count, 1)

    def test_exhausted_provider_failure_uses_same_exception_owner(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key="provider-exhausted"),
            )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(attempts=2)
        claim = CommunicationDispatcher.start_job(job.pk)

        CommunicationDispatcher.defer_job(
            job.pk, "provider_rejected", claim_token=claim.claim_token
        )

        job.refresh_from_db()
        exception = CommunicationException.objects.get(job=job)
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_FAILED)
        self.assertEqual(exception.last_error_code, "provider_rejected")
        self.assertEqual(exception.job_type, CommunicationDeliveryJob.KIND_GENERIC)

    def test_resolution_rejects_changed_exhausted_job_evidence(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key="exception-stale-job"),
            )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(attempts=2)
        claim = CommunicationDispatcher.start_job(job.pk)
        CommunicationDispatcher.defer_job(
            job.pk, "provider_malformed", claim_token=claim.claim_token
        )
        exception = CommunicationException.objects.get(job=job)
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(status="retrying")

        self.assertEqual(
            CommunicationDispatcher.exception_evidence(actor=self.user), []
        )

        with self.assertRaises(CommunicationDispatchConflict):
            CommunicationDispatcher.resolve_exception(
                actor=self.user,
                exception_id=exception.pk,
                expected_version=1,
                resolution_action="manual_closed",
                request=SimpleNamespace(headers={}, META={}),
            )

        exception.refresh_from_db()
        self.assertIsNone(exception.resolved_at)
        self.assertFalse(
            AuditLog.objects.filter(
                action="communications.exception.resolved", entity_id=exception.pk
            ).exists()
        )


class AdviceWorkerQueueTests(TestCase):
    def setUp(self):
        advice_fixtures.DisbursementAdviceApiTests.setUp(self)

    setUp_template = advice_fixtures.DisbursementAdviceApiTests.setUp_template

    @override_settings(
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_TASK_EAGER_PROPAGATES=True,
        COMMUNICATION_EMAIL_ADAPTER=(
            "sfpcl_credit.communications.adapters.FakeEmailDeliveryAdapter"
        )
    )
    def test_eager_worker_executes_committed_advice_job_without_network(self):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                f"/api/v1/disbursements/{self.row.pk}/send-advice/",
                {
                    "channel": "email",
                    "recipient_email": "borrower.advice@example.com",
                },
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="worker-eager-advice",
                **self.owner.owner.fixture._auth(self.actor),
            )

        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_SENT)
        self.assertEqual(job.attempts, 1)
        self.row.refresh_from_db()
        self.assertIsNotNone(self.row.disbursement_advice_communication_id)

    def test_stale_legacy_advice_job_is_operator_blocked_without_mutation(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                f"/api/v1/disbursements/{self.row.pk}/send-advice/",
                {
                    "channel": "email",
                    "recipient_email": "borrower.advice@example.com",
                },
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="worker-legacy-blocked",
                **self.owner.owner.fixture._auth(self.actor),
            )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        outbox = job.outbox
        CommunicationDeliveryOutbox.objects.filter(pk=outbox.pk).update(
            template_provenance_status="legacy_partial",
            template_provenance_origin="legacy_0005",
            content_template=None,
            template_code_snapshot=None,
            template_name_snapshot=None,
            template_type_snapshot=None,
            template_language_code_snapshot=None,
            template_audience_snapshot=None,
            template_version_snapshot=None,
            template_approval_status_snapshot=None,
            template_effective_from_snapshot=None,
            template_effective_to_snapshot=None,
            template_variables_snapshot=None,
            subject_template_snapshot=None,
            body_template_snapshot=None,
            template_checksum_sha256=None,
        )
        stale_at = timezone.now() - timedelta(minutes=1)
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            status=CommunicationDeliveryJob.STATUS_RUNNING,
            attempts=1,
            started_at=stale_at - timedelta(minutes=5),
            claim_token="126cc29c-f7bf-4f88-88ab-eb395356c327",
            lease_expires_at=stale_at,
        )
        before = CommunicationDeliveryJob.objects.values().get(pk=job.pk)

        due = CommunicationDispatcher.retry_failed(limit=10)
        evidence = CommunicationDispatcher.job_evidence(limit=10)

        self.assertEqual(due, [])
        self.assertEqual(
            CommunicationDeliveryJob.objects.values().get(pk=job.pk), before
        )
        self.assertEqual(evidence[0]["status"], "operator_blocked")
        self.assertEqual(
            evidence[0]["last_failure_code"], "legacy_provenance_blocked"
        )
        self.assertTrue(evidence[0]["operator_attention_required"])
        self.assertNotIn("borrower.advice@example.com", str(evidence))

    def test_expired_advice_worker_cannot_enter_provider_seam(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                f"/api/v1/disbursements/{self.row.pk}/send-advice/",
                {
                    "channel": "email",
                    "recipient_email": "borrower.advice@example.com",
                },
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="advice-expired-claim",
                **self.owner.owner.fixture._auth(self.actor),
            )
        job = CommunicationDeliveryJob.objects.get()
        expired = CommunicationDispatcher.start_job(job.pk)
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            lease_expires_at=timezone.now() - timedelta(seconds=1)
        )
        CommunicationDispatcher.retry_failed(limit=1)
        CommunicationDispatcher.start_job(job.pk)

        class NoProviderAdapter:
            def send_email(self, payload, idempotency_key):
                raise AssertionError("expired claim reached provider")

        with self.assertRaises(DisbursementAdviceConflict):
            send_disbursement_advice_now(
                actor=self.actor,
                disbursement_id=self.row.pk,
                payload={
                    "channel": "email",
                    "recipient_email": "borrower.advice@example.com",
                },
                adapter=NoProviderAdapter(),
                _job_id=expired.job_id,
                _claim_token=expired.claim_token,
            )

    def test_final_attempt_advice_crash_creates_one_advice_exception(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                f"/api/v1/disbursements/{self.row.pk}/send-advice/",
                {
                    "channel": "email",
                    "recipient_email": "borrower.advice@example.com",
                },
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="advice-final-attempt",
                **self.owner.owner.fixture._auth(self.actor),
            )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(attempts=2)
        CommunicationDispatcher.start_job(job.pk)
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            lease_expires_at=timezone.now()
        )

        self.assertEqual(CommunicationDispatcher.retry_failed(limit=1), [])

        exception = CommunicationException.objects.get(job=job)
        self.assertEqual(exception.job_type, CommunicationDeliveryJob.KIND_ADVICE)
        self.assertEqual(exception.related_entity_type, job.outbox.related_entity_type)
        self.assertEqual(exception.related_entity_id, job.outbox.related_entity_id)
        self.assertEqual(exception.last_error_code, "worker_crash")
        task = Notification.objects.get(
            notification_type="communication_job_failed",
            related_entity_id=exception.pk,
        )
        detail = self.client.get(
            task.action_url, **self.owner.owner.fixture._auth(self.actor)
        )
        self.assertEqual(detail.status_code, 200, detail.content)

    def test_advice_exception_rejects_generic_only_permission_for_every_action(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                f"/api/v1/disbursements/{self.row.pk}/send-advice/",
                {
                    "channel": "email",
                    "recipient_email": "borrower.advice@example.com",
                },
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="advice-exception-authority",
                **self.owner.owner.fixture._auth(self.actor),
            )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(attempts=2)
        CommunicationDispatcher.start_job(job.pk)
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            lease_expires_at=timezone.now()
        )
        CommunicationDispatcher.retry_failed(limit=1)
        exception = CommunicationException.objects.get(job=job)
        RolePermission.objects.filter(
            role=self.actor.primary_role,
            permission__permission_code="finance.disbursement.send_advice",
        ).delete()
        generic_permission, _ = Permission.objects.get_or_create(
            permission_code="communications.communication.send",
            defaults={
                "permission_name": "Send communications",
                "module_name": "communications",
                "risk_level": "medium",
            },
        )
        RolePermission.objects.get_or_create(
            role=self.actor.primary_role, permission=generic_permission
        )
        auth = self.owner.owner.fixture._auth(self.actor)

        collection = self.client.get("/api/v1/communication-exceptions/", **auth)
        detail = self.client.get(
            f"/api/v1/communication-exceptions/{exception.pk}/", **auth
        )
        resolution = self.client.post(
            f"/api/v1/communication-exceptions/{exception.pk}/resolve/",
            {"resolution_action": "manual_closed", "resolution_version": 1},
            content_type="application/json",
            **auth,
        )

        self.assertEqual(collection.status_code, 200, collection.content)
        self.assertEqual(collection.json()["data"], [])
        self.assertEqual(detail.status_code, 403, detail.content)
        self.assertEqual(resolution.status_code, 403, resolution.content)
        exception.refresh_from_db()
        self.assertIsNone(exception.resolved_at)
        self.assertFalse(
            AuditLog.objects.filter(
                action="communications.exception.resolved", entity_id=exception.pk
            ).exists()
        )


@skipUnless(connection.vendor == "postgresql", "PostgreSQL five-race acceptance")
class CommunicationWorkerClaimRaceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        communication_fixtures.CommunicationApiTests.setUp(self)
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=communication_fixtures.CommunicationApiTests._send_payload(self),
                content_type="application/json",
                headers=communication_fixtures.CommunicationApiTests._auth_headers(
                    self, idempotency_key=f"worker-race-{self._testMethodName}"
                ),
            )
        self.assertEqual(response.status_code, 200, response.content)
        self.job_id = CommunicationDeliveryJob.objects.get().pk

    _access_token = communication_fixtures.CommunicationApiTests._access_token

    def test_five_workers_claim_once_run_one(self):
        self._run_claim_race()

    def test_five_workers_claim_once_run_two(self):
        self._run_claim_race()

    def test_five_workers_recover_one_stale_claim_run_one(self):
        self._run_stale_recovery_race()

    def test_five_workers_recover_one_stale_claim_run_two(self):
        self._run_stale_recovery_race()

    def test_five_scanners_and_workers_terminalise_final_claim_run_one(self):
        self._run_final_terminal_race()

    def test_five_scanners_and_workers_terminalise_final_claim_run_two(self):
        self._run_final_terminal_race()

    def _adapter(self):
        owner = self

        class CountingAdapter(FakeEmailDeliveryAdapter):
            def send_email(self, payload, idempotency_key):
                with owner.call_lock:
                    owner.provider_calls += 1
                return super().send_email(payload, idempotency_key)

        return CountingAdapter()

    def _run_claim_race(self):
        self.provider_calls = 0
        self.call_lock = Lock()
        adapter = self._adapter()
        gate = Barrier(5)

        def contender(_index):
            close_old_connections()
            try:
                gate.wait(timeout=15)
                try:
                    return execute_communication_job(
                        self.job_id, adapter=adapter
                    )["delivery_status"]
                except CommunicationDispatchConflict:
                    return "clean_loser"
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=5) as pool:
            outcomes = list(pool.map(contender, range(5)))
        self.assertIn("sent", outcomes)
        self.assertEqual(self.provider_calls, 1)
        job = CommunicationDeliveryJob.objects.get(pk=self.job_id)
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_SENT)
        self.assertEqual(job.attempts, 1)

    def _run_stale_recovery_race(self):
        CommunicationDispatcher.start_job(self.job_id)
        CommunicationDeliveryJob.objects.filter(pk=self.job_id).update(
            lease_expires_at=timezone.now() - timedelta(seconds=1)
        )
        self.provider_calls = 0
        self.call_lock = Lock()
        adapter = self._adapter()
        gate = Barrier(5)

        def contender(_index):
            close_old_connections()
            try:
                gate.wait(timeout=15)
                due = CommunicationDispatcher.retry_failed(limit=1)
                if self.job_id not in due:
                    return "not_due"
                try:
                    return execute_communication_job(
                        self.job_id, adapter=adapter
                    )["delivery_status"]
                except CommunicationDispatchConflict:
                    return "clean_loser"
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=5) as pool:
            outcomes = list(pool.map(contender, range(5)))
        self.assertIn("sent", outcomes)
        self.assertEqual(self.provider_calls, 1)
        job = CommunicationDeliveryJob.objects.get(pk=self.job_id)
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_SENT)
        self.assertEqual(job.attempts, 2)
        self.assertEqual(job.recovery_count, 1)

    def _run_final_terminal_race(self):
        CommunicationDeliveryJob.objects.filter(pk=self.job_id).update(attempts=2)
        CommunicationDispatcher.start_job(self.job_id)
        CommunicationDeliveryJob.objects.filter(pk=self.job_id).update(
            lease_expires_at=timezone.now() - timedelta(seconds=1)
        )
        self.provider_calls = 0
        self.call_lock = Lock()
        adapter = self._adapter()
        gate = Barrier(10)

        def scanner(_index):
            close_old_connections()
            try:
                gate.wait(timeout=15)
                return CommunicationDispatcher.retry_failed(limit=1)
            finally:
                connections["default"].close()

        def worker(_index):
            close_old_connections()
            try:
                gate.wait(timeout=15)
                try:
                    execute_communication_job(self.job_id, adapter=adapter)
                    return "unexpected_execution"
                except CommunicationDispatchConflict:
                    return "clean_loser"
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = [pool.submit(scanner, index) for index in range(5)]
            futures += [pool.submit(worker, index) for index in range(5)]
            outcomes = [future.result() for future in futures]

        self.assertNotIn("unexpected_execution", outcomes)
        self.assertEqual(self.provider_calls, 0)
        job = CommunicationDeliveryJob.objects.get(pk=self.job_id)
        exception = CommunicationException.objects.get(job=job)
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_FAILED)
        self.assertEqual(job.attempts, job.max_attempts)
        self.assertEqual(job.recovery_count, 1)
        self.assertEqual(CommunicationException.objects.filter(job=job).count(), 1)
        self.assertEqual(
            Notification.objects.filter(
                notification_type="communication_job_failed",
                related_entity_id=exception.pk,
            ).count(),
            1,
        )
        self.assertEqual(
            AuditLog.objects.filter(
                action="communications.exception.created", entity_id=exception.pk
            ).count(),
            1,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="CommunicationExceptionResolution",
                entity_id=exception.pk,
                to_state="open",
            ).count(),
            1,
        )
