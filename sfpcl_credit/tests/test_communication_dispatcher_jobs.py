from unittest.mock import patch
from unittest import skipUnless
from datetime import timedelta
import ast
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from sfpcl_credit.communications.adapters import (
    FakeEmailDeliveryAdapter,
    FutureEmailDeliveryAdapter,
)
from sfpcl_credit.communications.models import (
    Communication,
    CommunicationDeliveryJob,
    CommunicationProviderAttempt,
    DisbursementAdviceDeliveryReceipt,
    Notification,
)
from django.utils import timezone
from django.db import close_old_connections, connection, connections
from django.test import TestCase, TransactionTestCase
from sfpcl_credit.tests import test_disbursement_advice_api as advice_fixtures
from sfpcl_credit.processes.disbursement_advice_delivery import (
    execute_disbursement_advice_job,
    queue_disbursement_advice,
)
from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatchConflict,
)
from sfpcl_credit.identity.models import User
from sfpcl_credit.processes.tasks import dispatch_due_communication_jobs


class CommunicationDispatcherJobTests(TestCase):
    setUp = advice_fixtures.DisbursementAdviceApiTests.setUp
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
        self.assertEqual(job.attempts, 0)
        provider.assert_not_called()
        self.assertIsNone(self.row.disbursement_advice_communication_id)

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
            replay.json()["data"]["communication_job_id"],
            first.json()["data"]["communication_job_id"],
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

    def test_pinned_task_contract_runs_manual_adapter_job(self):
        queued = self.client.post(
            f"/api/v1/disbursements/{self.row.pk}/send-advice/",
            {"channel": "email", "recipient_email": "borrower.advice@example.com"},
            content_type="application/json",
            **self.owner.owner.fixture._auth(self.actor),
        )

        results = dispatch_due_communication_jobs()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["delivery_status"], "sent")
        self.assertEqual(
            results[0]["communication_job_id"],
            queued.json()["data"]["communication_job_id"],
        )

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
                )
                return result["communication_job_id"]
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=5) as pool:
            job_ids = list(pool.map(contender, range(5)))
        self.assertEqual(len(set(job_ids)), 1)
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
