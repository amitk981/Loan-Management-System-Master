from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.utils import timezone

from sfpcl_credit.communications.models import CommunicationDeliveryJob
from sfpcl_credit.tests import test_disbursement_advice_api as advice_fixtures


class GenericCommunicationJobMigrationTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        super().setUp()
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_existing_advice_job_identity_and_attempt_history_are_preserved(self):
        fixture = advice_fixtures.DisbursementAdviceApiTests(
            "test_public_success_sends_exact_advice_without_financial_side_effects"
        )
        fixture.setUp()
        response = fixture.client.post(
            f"/api/v1/disbursements/{fixture.row.pk}/send-advice/",
            {"channel": "email", "recipient_email": "borrower.advice@example.com"},
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="migration-preserved-advice-key",
            **fixture.owner.owner.fixture._auth(fixture.actor),
        )
        self.assertEqual(response.status_code, 200, response.content)
        job_id = response.json()["data"]["communication_job_id"]
        CommunicationDeliveryJob.objects.filter(pk=job_id).update(
            status="retrying",
            attempts=2,
            next_attempt_at=timezone.now(),
            last_failure_code="provider_timeout",
        )

        old_apps = self._migrate(
            [("communications", "0008_legacy_template_provenance_closure")]
        )
        old_job = old_apps.get_model(
            "communications", "CommunicationDeliveryJob"
        ).objects.get(pk=job_id)
        retained = {
            "pk": old_job.pk,
            "outbox_id": old_job.outbox_id,
            "advice_intent_id": old_job.advice_intent_id,
            "status": old_job.status,
            "attempts": old_job.attempts,
            "next_attempt_at": old_job.next_attempt_at,
            "last_failure_code": old_job.last_failure_code,
            "created_at": old_job.created_at,
        }

        new_apps = self._migrate(
            [("communications", "0009_generic_delivery_job_identity")]
        )
        job = new_apps.get_model(
            "communications", "CommunicationDeliveryJob"
        ).objects.get(pk=job_id)
        for field, value in retained.items():
            self.assertEqual(getattr(job, field), value)
        self.assertEqual(job.job_kind, "advice")
        self.assertEqual(job.communication_id, fixture.row.advice_intent.pk)
        self.assertEqual(job.idempotency_key, "migration-preserved-advice-key")

    def test_existing_running_job_receives_an_expired_recoverable_lease(self):
        fixture = advice_fixtures.DisbursementAdviceApiTests(
            "test_public_success_sends_exact_advice_without_financial_side_effects"
        )
        fixture.setUp()
        response = fixture.client.post(
            f"/api/v1/disbursements/{fixture.row.pk}/send-advice/",
            {"channel": "email", "recipient_email": "borrower.advice@example.com"},
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="migration-running-job-key",
            **fixture.owner.owner.fixture._auth(fixture.actor),
        )
        self.assertEqual(response.status_code, 200, response.content)
        job_id = response.json()["data"]["communication_job_id"]

        old_apps = self._migrate(
            [("communications", "0009_generic_delivery_job_identity")]
        )
        OldJob = old_apps.get_model("communications", "CommunicationDeliveryJob")
        started_at = timezone.now()
        OldJob.objects.filter(pk=job_id).update(
            status="running", attempts=1, started_at=started_at
        )

        new_apps = self._migrate(
            [("communications", "0010_worker_claim_lease_and_recovery")]
        )
        job = new_apps.get_model(
            "communications", "CommunicationDeliveryJob"
        ).objects.get(pk=job_id)
        self.assertEqual(job.status, "running")
        self.assertEqual(job.attempts, 1)
        self.assertEqual(job.started_at, started_at)
        self.assertIsNotNone(job.claim_token)
        self.assertLess(job.lease_expires_at, timezone.now())
        self.assertEqual(job.recovery_count, 0)
        self.assertIsNone(job.last_recovered_at)

    @staticmethod
    def _migrate(targets):
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps
