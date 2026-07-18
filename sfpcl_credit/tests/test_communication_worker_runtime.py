from unittest.mock import patch
from unittest import skipUnless
from datetime import timedelta
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Lock

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
)
from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
    CommunicationDispatchConflict,
)
from sfpcl_credit.communications.adapters import FakeEmailDeliveryAdapter
from sfpcl_credit.processes.communication_delivery import execute_communication_job
from sfpcl_credit.processes.disbursement_advice_delivery import (
    send_disbursement_advice_now,
)
from sfpcl_credit.disbursements.modules.disbursement_advice import (
    DisbursementAdviceConflict,
)
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


class CommunicationWorkerQueueTests(TestCase):
    def setUp(self):
        communication_fixtures.CommunicationApiTests.setUp(self)

    _auth_headers = communication_fixtures.CommunicationApiTests._auth_headers
    _access_token = communication_fixtures.CommunicationApiTests._access_token
    _send_payload = communication_fixtures.CommunicationApiTests._send_payload

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
                            request=request,
                            content_template_id=self.template.pk,
                            merge_data={
                                "application_reference_number": "LA-ROLLBACK",
                                "borrower_name": "Rollback Borrower",
                            },
                            related_entity_type="loan_application",
                            related_entity_id=self.related_entity_id,
                            recipient_party_type="borrower",
                            recipient_party_id=self.recipient_party_id,
                            recipient_address="rollback@example.com",
                            channel="email",
                            idempotency_key="worker-rollback",
                        )
                        CommunicationDispatcher.send(
                            communication_id=row.pk,
                            idempotency_key="worker-rollback",
                            actor=self.user,
                            request=request,
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
