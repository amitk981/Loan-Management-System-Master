from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.utils import timezone
import uuid

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

    def test_existing_generic_acceptance_gains_immutable_provider_evidence(self):
        old_apps = self._migrate(
            [("communications", "0011_communication_exception_queue")]
        )
        Communication = old_apps.get_model("communications", "Communication")
        Job = old_apps.get_model("communications", "CommunicationDeliveryJob")
        communication = Communication.objects.create(
            related_entity_type="loan_application",
            related_entity_id=uuid.uuid4(),
            recipient_party_type="borrower",
            recipient_address="migration@example.com",
            channel="email",
            subject_snapshot="Migration acceptance",
            body_snapshot="Retained generic provider acceptance",
            delivery_status="sent",
            sent_at=timezone.now(),
            external_message_id="fake:migration-provider-evidence",
        )
        accepted_at = communication.sent_at
        job = Job.objects.create(
            communication_id=communication.pk,
            job_kind="generic",
            idempotency_key="migration-provider-evidence",
            actor_id=uuid.uuid4(),
            actor_role_code="credit_manager",
            actor_team_codes=["credit"],
            request_id="migration-provider-evidence",
            request_payload_digest="a" * 64,
            status="sent",
            attempts=1,
            provider_external_message_id="fake:migration-provider-evidence",
            provider_delivery_status="sent",
            provider_accepted_at=accepted_at,
            completed_at=accepted_at,
        )

        new_apps = self._migrate(
            [("communications", "0012_generic_provider_evidence")]
        )
        Evidence = new_apps.get_model(
            "communications", "CommunicationProviderEvidence"
        )
        evidence = Evidence.objects.get(job_id=job.pk)
        self.assertEqual(evidence.communication_id, communication.pk)
        self.assertEqual(evidence.channel, "email")
        self.assertEqual(evidence.payload_digest, "a" * 64)
        self.assertEqual(evidence.idempotency_key, "migration-provider-evidence")
        self.assertEqual(evidence.actor_id, job.actor_id)
        self.assertEqual(
            evidence.adapter_kind, "legacy:retained-generic-acceptance"
        )
        self.assertEqual(
            evidence.provider_external_message_id,
            "fake:migration-provider-evidence",
        )
        self.assertEqual(len(evidence.evidence_digest), 64)

    def test_retained_exception_normalizes_source_channel_without_losing_truth(self):
        old_apps = self._migrate(
            [("communications", "0012_generic_provider_evidence")]
        )
        Role = old_apps.get_model("identity", "Role")
        User = old_apps.get_model("identity", "User")
        Communication = old_apps.get_model("communications", "Communication")
        Job = old_apps.get_model("communications", "CommunicationDeliveryJob")
        Exception = old_apps.get_model("communications", "CommunicationException")
        role = Role.objects.create(
            role_code="legacy-exception-owner",
            role_name="Legacy exception owner",
            status="active",
        )
        actor = User.objects.create(
            full_name="Legacy Exception Owner",
            email="legacy.exception.owner@sfpcl.example",
            primary_role=role,
            password_hash="not-a-real-password",
        )
        communication = Communication.objects.create(
            related_entity_type="loan_application",
            related_entity_id=uuid.uuid4(),
            recipient_party_type="borrower",
            recipient_address="legacy@example.com",
            channel="sms",
            subject_snapshot="SMS",
            body_snapshot="Retained message",
            delivery_status="pending",
        )
        job = Job.objects.create(
            communication_id=communication.pk,
            job_kind="generic",
            idempotency_key="legacy-exception-provider",
            actor_id=actor.pk,
            actor_role_code=role.role_code,
            actor_team_codes=[],
            request_id="legacy-exception-provider",
            request_payload_digest="b" * 64,
            status="failed",
            attempts=3,
            max_attempts=3,
            last_failure_code="provider_rejected",
            completed_at=timezone.now(),
        )
        retained = Exception.objects.create(
            job=job,
            provider_code=(
                "sfpcl_credit.communications.adapters.ManualSmsDeliveryAdapter"
            ),
            job_type="generic",
            related_entity_type=communication.related_entity_type,
            related_entity_id=communication.related_entity_id,
            last_error_code=job.last_failure_code,
            retry_count=job.attempts,
            assigned_owner=actor,
        )
        before = Exception.objects.filter(pk=retained.pk).values().get()

        new_apps = self._migrate(
            [("communications", "0013_exception_provider_vocabulary")]
        )
        migrated = new_apps.get_model(
            "communications", "CommunicationException"
        ).objects.filter(pk=retained.pk).values().get()

        self.assertEqual(migrated.pop("provider_code"), "sms")
        before.pop("provider_code")
        self.assertEqual(migrated, before)

    @staticmethod
    def _migrate(targets):
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps
