from unittest.mock import patch
from unittest import skipUnless
from datetime import timedelta
import ast
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from types import SimpleNamespace

from sfpcl_credit.communications.adapters import (
    FakeEmailDeliveryAdapter,
    FakeSmsDeliveryAdapter,
    FutureEmailDeliveryAdapter,
)
from sfpcl_credit.communications.models import (
    Communication,
    CommunicationDeliveryJob,
    CommunicationProviderEvidence,
    CommunicationProviderAttempt,
    DisbursementAdviceDeliveryReceipt,
    Notification,
)
from sfpcl_credit.communications import services as communication_services
from django.utils import timezone
from django.db import close_old_connections, connection, connections, transaction
from django.test import TestCase, TransactionTestCase
from sfpcl_credit.tests import test_disbursement_advice_api as advice_fixtures
from sfpcl_credit.tests import test_communications_api as communication_fixtures
from sfpcl_credit.processes.disbursement_advice_delivery import (
    execute_disbursement_advice_job,
    queue_disbursement_advice,
)
from sfpcl_credit.processes.communication_delivery import execute_communication_job
from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
    CommunicationDispatchConflict,
)
from sfpcl_credit.identity.models import User
from sfpcl_credit.processes.tasks import dispatch_due_communication_jobs


class CommunicationDispatcherJobTests(TestCase):
    def setUp(self):
        advice_fixtures.DisbursementAdviceApiTests.setUp(self)
        self.client.defaults["HTTP_IDEMPOTENCY_KEY"] = "advice-job-default"

    setUp_template = advice_fixtures.DisbursementAdviceApiTests.setUp_template

    def test_send_advice_request_queues_without_calling_provider(self):
        with patch(
            "sfpcl_credit.communications.adapters.ManualEmailDeliveryAdapter.send_email"
        ) as provider:
            response = self.client.post(
                f"/api/v1/disbursements/{self.row.pk}/send-advice/",
                {
                    "channel": "email",
                    "recipient_email": "borrower.advice@example.com",
                },
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="advice-send-001",
                **self.owner.owner.fixture._auth(self.actor),
            )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["disbursement_id"], str(self.row.pk))
        self.assertEqual(data["delivery_status"], "queued")
        job = CommunicationDeliveryJob.objects.get(
            advice_intent_id=self.row.advice_intent.pk
        )
        self.assertEqual(data["communication_job_id"], str(job.pk))
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_QUEUED)
        self.assertEqual(job.idempotency_key, "advice-send-001")
        self.assertEqual(job.attempts, 0)
        provider.assert_not_called()
        self.assertIsNone(self.row.disbursement_advice_communication_id)

    def test_send_advice_requires_explicit_idempotency_key_before_writes(self):
        response = self.client.post(
            f"/api/v1/disbursements/{self.row.pk}/send-advice/",
            {
                "channel": "email",
                "recipient_email": "borrower.advice@example.com",
            },
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="",
            **self.owner.owner.fixture._auth(self.actor),
        )

        self.assertEqual(response.status_code, 400, response.content)
        self.assertIn("idempotency_key", response.json()["error"]["field_errors"])
        self.assertEqual(CommunicationDeliveryJob.objects.count(), 0)
        self.assertEqual(CommunicationProviderAttempt.objects.count(), 0)

    def test_queue_exact_replay_returns_same_job_and_changed_replay_conflicts(self):
        communication_count = Communication.objects.count()
        first = self.client.post(
            f"/api/v1/disbursements/{self.row.pk}/send-advice/",
            {"channel": "email", "recipient_email": "borrower.advice@example.com"},
            content_type="application/json",
            **self.owner.owner.fixture._auth(self.actor),
        )
        replay = self.client.post(
            f"/api/v1/disbursements/{self.row.pk}/send-advice/",
            {
                "channel": "email",
                "recipient_email": "  Borrower.Advice@Example.com ",
            },
            content_type="application/json",
            **self.owner.owner.fixture._auth(self.actor),
        )
        changed = self.client.post(
            f"/api/v1/disbursements/{self.row.pk}/send-advice/",
            {"channel": "email", "recipient_email": "changed@example.com"},
            content_type="application/json",
            **self.owner.owner.fixture._auth(self.actor),
        )

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(
            replay.json()["data"],
            {
                "idempotency_replayed": True,
                "original_response": first.json()["data"],
            },
        )
        self.assertEqual(changed.status_code, 409, changed.content)
        self.assertEqual(CommunicationDeliveryJob.objects.count(), 1)
        self.assertEqual(Communication.objects.count(), communication_count)
        self.assertEqual(CommunicationProviderAttempt.objects.count(), 0)
        self.assertEqual(DisbursementAdviceDeliveryReceipt.objects.count(), 0)

    def test_forged_terminal_job_cannot_move_provider_call_back_into_request(self):
        queued = self.client.post(
            f"/api/v1/disbursements/{self.row.pk}/send-advice/",
            {"channel": "email", "recipient_email": "borrower.advice@example.com"},
            content_type="application/json",
            **self.owner.owner.fixture._auth(self.actor),
        )
        CommunicationDeliveryJob.objects.filter(
            pk=queued.json()["data"]["communication_job_id"]
        ).update(status="sent", attempts=1, completed_at=timezone.now())

        with patch(
            "sfpcl_credit.communications.adapters.ManualEmailDeliveryAdapter.send_email"
        ) as provider:
            replay = self.client.post(
                f"/api/v1/disbursements/{self.row.pk}/send-advice/",
                {"channel": "email", "recipient_email": "borrower.advice@example.com"},
                content_type="application/json",
                **self.owner.owner.fixture._auth(self.actor),
            )

        self.assertEqual(replay.status_code, 409, replay.content)
        provider.assert_not_called()
        self.assertEqual(CommunicationProviderAttempt.objects.count(), 0)

    def test_worker_acceptance_finalizes_job_and_advice_once(self):
        queued = self.client.post(
            f"/api/v1/disbursements/{self.row.pk}/send-advice/",
            {"channel": "email", "recipient_email": "borrower.advice@example.com"},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-queue-advice",
            HTTP_USER_AGENT="job-contract-test",
            **self.owner.owner.fixture._auth(self.actor),
        )
        self.assertEqual(queued.status_code, 200, queued.content)

        result = execute_disbursement_advice_job(
            queued.json()["data"]["communication_job_id"],
            adapter=FakeEmailDeliveryAdapter(),
        )

        self.assertEqual(result["delivery_status"], "sent")
        job = CommunicationDeliveryJob.objects.get(pk=result["communication_job_id"])
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_SENT)
        self.assertEqual(job.attempts, 1)
        self.assertIsNotNone(job.completed_at)
        self.row.refresh_from_db()
        self.assertIsNotNone(self.row.disbursement_advice_communication_id)
        self.assertEqual(DisbursementAdviceDeliveryReceipt.objects.count(), 1)
        self.assertEqual(CommunicationProviderAttempt.objects.count(), 1)

    def test_default_manual_mode_cannot_fabricate_provider_acceptance(self):
        queued = self.client.post(
            f"/api/v1/disbursements/{self.row.pk}/send-advice/",
            {"channel": "email", "recipient_email": "borrower.advice@example.com"},
            content_type="application/json",
            **self.owner.owner.fixture._auth(self.actor),
        )

        results = dispatch_due_communication_jobs()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["delivery_status"], "retrying")
        self.assertEqual(
            results[0]["communication_job_id"],
            queued.json()["data"]["communication_job_id"],
        )
        self.assertEqual(CommunicationProviderAttempt.objects.count(), 1)
        self.assertFalse(
            CommunicationProviderAttempt.objects.filter(outcome="accepted").exists()
        )
        self.assertEqual(DisbursementAdviceDeliveryReceipt.objects.count(), 0)
        self.assertFalse(Communication.objects.filter(delivery_status="sent").exists())

    def test_future_adapter_uses_the_same_worker_contract(self):
        queued = self.client.post(
            f"/api/v1/disbursements/{self.row.pk}/send-advice/",
            {"channel": "email", "recipient_email": "borrower.advice@example.com"},
            content_type="application/json",
            **self.owner.owner.fixture._auth(self.actor),
        )
        result = execute_disbursement_advice_job(
            queued.json()["data"]["communication_job_id"],
            adapter=FutureEmailDeliveryAdapter(transport=FakeEmailDeliveryAdapter()),
        )

        self.assertEqual(result["delivery_status"], "sent")
        self.assertEqual(CommunicationProviderAttempt.objects.count(), 1)

    def test_provider_timeout_retries_with_backoff_then_fails_safely(self):
        class TimeoutAdapter:
            def send_email(self, payload, idempotency_key):
                raise TimeoutError(
                    "provider-secret borrower.advice@example.com RBL-ADVICE-9876"
                )

        queued = self.client.post(
            f"/api/v1/disbursements/{self.row.pk}/send-advice/",
            {"channel": "email", "recipient_email": "borrower.advice@example.com"},
            content_type="application/json",
            **self.owner.owner.fixture._auth(self.actor),
        )
        job_id = queued.json()["data"]["communication_job_id"]

        first = execute_disbursement_advice_job(job_id, adapter=TimeoutAdapter())
        self.assertEqual(first["delivery_status"], "retrying")
        for hours in (1, 2):
            with patch(
                "sfpcl_credit.communications.modules.communication_dispatcher.timezone.now",
                return_value=timezone.now() + timedelta(hours=hours),
            ):
                result = execute_disbursement_advice_job(
                    job_id, adapter=TimeoutAdapter()
                )

        self.assertEqual(result["delivery_status"], "failed")
        job = CommunicationDeliveryJob.objects.get(pk=job_id)
        self.assertEqual(job.attempts, 3)
        self.assertEqual(job.last_failure_code, "provider_timeout")
        self.assertNotIn("provider-secret", str(job.__dict__))
        self.assertNotIn("borrower.advice@example.com", str(job.__dict__))
        self.assertEqual(DisbursementAdviceDeliveryReceipt.objects.count(), 0)
        task = Notification.objects.get(notification_type="communication_job_failed")
        self.assertEqual(task.recipient_user_id, self.actor.pk)
        self.assertNotIn("provider-secret", task.message)
        self.assertNotIn("borrower.advice@example.com", task.message)

    def test_advice_runtime_dependency_is_composed_only_in_processes(self):
        project = Path(__file__).resolve().parents[1]
        forbidden = {
            "communications": "sfpcl_credit.disbursements",
            "disbursements": "sfpcl_credit.communications",
        }
        violations = []
        for app, target in forbidden.items():
            for source in (project / app).rglob("*.py"):
                tree = ast.parse(source.read_text())
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.extend(alias.name for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.append(node.module)
                if any(name == target or name.startswith(f"{target}.") for name in imports):
                    violations.append(str(source.relative_to(project)))
        self.assertEqual(violations, [])

    def test_disbursement_owner_does_not_import_or_register_process_coordinator(self):
        project = Path(__file__).resolve().parents[1]
        owner_sources = [
            project / "disbursements" / "modules" / "disbursement_advice.py",
            project / "disbursements" / "modules" / "disbursement_workflow.py",
        ]
        violations = []
        for source in owner_sources:
            tree = ast.parse(source.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module]
                else:
                    continue
                if any(
                    name == "sfpcl_credit.processes"
                    or name.startswith("sfpcl_credit.processes.")
                    for name in names
                ):
                    violations.append(str(source.relative_to(project)))
        self.assertEqual(violations, [])
        workflow_source = owner_sources[1].read_text()
        self.assertNotIn("queue_advice =", workflow_source)
        self.assertNotIn("send_advice =", workflow_source)


@skipUnless(connection.vendor == "postgresql", "PostgreSQL five-race acceptance")
class CommunicationDispatcherJobRaceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = advice_fixtures.DisbursementAdviceApiTests(
            "test_public_success_sends_exact_advice_without_financial_side_effects"
        )
        fixture.setUp()
        self.actor_id = fixture.actor.pk
        self.disbursement_id = fixture.row.pk

    def test_five_queue_callers_retain_one_job_run_one(self):
        self._run_queue_race()

    def test_five_queue_callers_retain_one_job_run_two(self):
        self._run_queue_race()

    def test_five_workers_retain_one_terminal_chain_run_one(self):
        self._run_worker_race()

    def test_five_workers_retain_one_terminal_chain_run_two(self):
        self._run_worker_race()

    def _run_queue_race(self):
        gate = Barrier(5)

        def contender(_index):
            close_old_connections()
            try:
                actor = User.objects.get(pk=self.actor_id)
                gate.wait(timeout=15)
                result = queue_disbursement_advice(
                    actor=actor,
                    disbursement_id=self.disbursement_id,
                    payload={
                        "channel": "email",
                        "recipient_email": "borrower.advice@example.com",
                    },
                    idempotency_key="advice-queue-race",
                )
                return result
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=5) as pool:
            responses = list(pool.map(contender, range(5)))
        originals = [item for item in responses if not item.get("idempotency_replayed")]
        replays = [item for item in responses if item.get("idempotency_replayed")]
        self.assertEqual(len(originals), 1)
        self.assertEqual(len(replays), 4)
        self.assertTrue(
            all(item["original_response"] == originals[0] for item in replays)
        )
        self.assertEqual(CommunicationDeliveryJob.objects.count(), 1)

    def _run_worker_race(self):
        actor = User.objects.get(pk=self.actor_id)
        job_id = queue_disbursement_advice(
            actor=actor,
            disbursement_id=self.disbursement_id,
            payload={
                "channel": "email",
                "recipient_email": "borrower.advice@example.com",
            },
            idempotency_key="advice-worker-race",
        )["communication_job_id"]
        gate = Barrier(5)

        class CountingAdapter(FakeEmailDeliveryAdapter):
            calls = 0

            def send_email(self, payload, idempotency_key):
                self.calls += 1
                return super().send_email(payload, idempotency_key)

        adapter = CountingAdapter()

        def contender(_index):
            close_old_connections()
            try:
                gate.wait(timeout=15)
                try:
                    return execute_disbursement_advice_job(job_id, adapter=adapter)[
                        "delivery_status"
                    ]
                except CommunicationDispatchConflict:
                    return "clean_loser"
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=5) as pool:
            outcomes = list(pool.map(contender, range(5)))
        self.assertIn("sent", outcomes)
        self.assertEqual(adapter.calls, 1)
        self.assertEqual(CommunicationDeliveryJob.objects.get().status, "sent")
        self.assertEqual(CommunicationProviderAttempt.objects.count(), 1)
        self.assertEqual(DisbursementAdviceDeliveryReceipt.objects.count(), 1)


@skipUnless(connection.vendor == "postgresql", "PostgreSQL five-race acceptance")
class GenericCommunicationJobRaceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        communication_fixtures.CommunicationApiTests.setUp(self)
        self.actor_id = self.user.pk
        self.template_id = self.template.pk

    def test_five_generic_callers_retain_one_job_run_one(self):
        self._run_generic_race("email")

    def test_five_generic_callers_retain_one_job_run_two(self):
        self._run_generic_race("email")

    def test_five_sms_callers_retain_one_job_run_one(self):
        self._run_generic_race("sms")

    def test_five_sms_callers_retain_one_job_run_two(self):
        self._run_generic_race("sms")

    def test_five_email_workers_retain_one_acceptance_run_one(self):
        self._run_generic_worker_race("email")

    def test_five_email_workers_retain_one_acceptance_run_two(self):
        self._run_generic_worker_race("email")

    def test_five_sms_workers_retain_one_acceptance_run_one(self):
        self._run_generic_worker_race("sms")

    def test_five_sms_workers_retain_one_acceptance_run_two(self):
        self._run_generic_worker_race("sms")

    def _run_generic_race(self, channel):
        if channel == "sms":
            self.template.template_type = "sms"
            self.template.save(update_fields=["template_type"])
        recipient = (
            "+919876543210" if channel == "sms" else "race.borrower@example.com"
        )
        gate = Barrier(5)

        def contender(index):
            close_old_connections()
            try:
                actor = User.objects.get(pk=self.actor_id)
                request = SimpleNamespace(
                    headers={"X-Request-ID": f"req-generic-race-{index}"},
                    META={"REMOTE_ADDR": "127.0.0.1", "HTTP_USER_AGENT": "race"},
                )
                gate.wait(timeout=15)
                request.headers["Idempotency-Key"] = f"generic-{channel}-five-race"
                return communication_services.send_communication(
                    actor,
                    request,
                    {
                        "related_entity_type": "loan_application",
                        "related_entity_id": str(self.related_entity_id),
                        "recipient_party_type": "borrower",
                        "recipient_party_id": str(self.recipient_party_id),
                        "recipient_address": recipient,
                        "channel": channel,
                        "content_template_id": str(self.template_id),
                        "merge_data": {
                            "application_reference_number": "LA-RACE-001",
                            "borrower_name": "Race Borrower",
                        },
                    },
                )
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=5) as pool:
            responses = list(pool.map(contender, range(5)))
        originals = [item for item in responses if not item.get("idempotency_replayed")]
        replays = [item for item in responses if item.get("idempotency_replayed")]
        self.assertEqual(len(originals), 1)
        self.assertEqual(len(replays), 4)
        self.assertTrue(
            all(item["original_response"] == originals[0] for item in replays)
        )
        self.assertEqual(Communication.objects.count(), 1)
        self.assertEqual(CommunicationDeliveryJob.objects.count(), 1)

    def _run_generic_worker_race(self, channel):
        self._run_generic_race(channel)
        job_id = CommunicationDeliveryJob.objects.get().pk
        gate = Barrier(5)
        base = FakeSmsDeliveryAdapter if channel == "sms" else FakeEmailDeliveryAdapter

        class CountingAdapter(base):
            calls = 0

            def send_email(self, payload, idempotency_key):
                self.calls += 1
                return super().send_email(payload, idempotency_key)

            def send_sms(self, payload, idempotency_key):
                self.calls += 1
                return super().send_sms(payload, idempotency_key)

        adapter = CountingAdapter()

        def contender(_index):
            close_old_connections()
            try:
                gate.wait(timeout=15)
                try:
                    return execute_communication_job(job_id, adapter=adapter)[
                        "delivery_status"
                    ]
                except CommunicationDispatchConflict:
                    return "clean_loser"
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=5) as pool:
            outcomes = list(pool.map(contender, range(5)))
        self.assertIn("sent", outcomes)
        self.assertEqual(adapter.calls, 1)
        self.assertEqual(CommunicationDeliveryJob.objects.get().status, "sent")
        evidence = CommunicationProviderEvidence.objects.get()
        self.assertEqual(evidence.channel, channel)
