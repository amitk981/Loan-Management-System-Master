"""Independent failing probes for the 2026-07-18 architecture review."""

from __future__ import annotations

import os
from pathlib import Path
import sys
import unittest
import uuid
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sfpcl_credit.config.settings")

import django

django.setup()

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test.runner import DiscoverRunner
from django.utils import timezone

from sfpcl_credit.communications.adapters import EmailDeliveryResult
from sfpcl_credit.communications.models import CommunicationDeliveryJob, Notification
from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
)
from sfpcl_credit.processes.communication_delivery import execute_communication_job
from sfpcl_credit.tests import test_communications_api as communication_fixtures
from sfpcl_credit.tests import test_communication_worker_runtime as worker_fixtures
from sfpcl_credit.tests.test_communication_receipt_owner_migration import (
    LegacyAdviceTemplateProvenanceMigrationTests,
)


class QueuedJobMigrationProbe(LegacyAdviceTemplateProvenanceMigrationTests):
    """A genuine H5 queued job must survive 0007 -> 0008 -> 0009."""

    def test_queued_frozen_job_migrates_without_becoming_legacy(self):
        old_apps = self._migrate(self.migrate_from)
        Template = old_apps.get_model("communications", "ContentTemplate")
        Job = old_apps.get_model("communications", "CommunicationDeliveryJob")
        template = Template.objects.create(
            template_code="review_queued_advice_v1",
            template_name="Review queued advice",
            template_type="email",
            language_code="en",
            audience="borrower",
            subject_template="Advice {{ borrower_name }}",
            body_template="Queued for {{ borrower_name }}",
            variables_json=["borrower_name"],
            approval_status="approved",
            template_version="v1",
            effective_from=timezone.localdate(),
        )
        outbox = self._make_pending_without_attempt(
            old_apps,
            self._accepted_outbox(
                old_apps,
                template=template,
                outbox_id=uuid.uuid4(),
                adapter_kind=(
                    "sfpcl_credit.communications.adapters.FakeEmailDeliveryAdapter"
                ),
            ),
        )
        job = Job.objects.create(
            outbox=outbox,
            advice_intent_id=outbox.advice_intent,
            actor_id=uuid.uuid4(),
            actor_role_code="credit_manager",
            actor_team_codes=["credit"],
            request_id="review-queued-job",
            request_payload_digest=outbox.payload_digest,
            status="queued",
        )

        self._migrate([("communications", "0008_legacy_template_provenance_closure")])
        current_apps = self._migrate(
            [("communications", "0009_generic_delivery_job_identity")]
        )
        CurrentJob = current_apps.get_model(
            "communications", "CommunicationDeliveryJob"
        )
        CurrentOutbox = current_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        )
        migrated_job = CurrentJob.objects.get(pk=job.pk)
        migrated_outbox = CurrentOutbox.objects.get(pk=outbox.pk)
        self.assertEqual(migrated_job.status, "queued")
        self.assertEqual(migrated_outbox.template_provenance_status, "verified")
        self.assertEqual(
            migrated_outbox.template_provenance_origin, "frozen_before_dispatch"
        )


class FinalAttemptRecoveryProbe(worker_fixtures.CommunicationWorkerQueueTests):
    """An expired final claim must exhaust safely, not exceed max_attempts."""

    def test_final_attempt_crash_becomes_failed_with_operator_task(self):
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key="review-final-crash"),
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

        job.refresh_from_db()
        self.assertEqual(due, [])
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_FAILED)
        self.assertEqual(job.attempts, job.max_attempts)
        self.assertTrue(
            Notification.objects.filter(
                notification_type="communication_job_failed",
                related_entity_type="communication_job",
                related_entity_id=job.pk,
            ).exists()
        )


class SmsChannelProbe(communication_fixtures.CommunicationApiTests):
    """An SMS job must not cross the email provider seam."""

    def test_sms_job_never_calls_email_adapter(self):
        self.template.template_type = "sms"
        self.template.subject_template = "SMS {{ application_reference_number }}"
        self.template.save(update_fields=["template_type", "subject_template"])
        with patch(
            "sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"
        ):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(channel="sms"),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key="review-sms-channel"),
            )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()

        class RecordingEmailAdapter:
            calls = 0

            def send_email(self, payload, idempotency_key):
                self.calls += 1
                return EmailDeliveryResult(
                    external_message_id="fake:review-sms-routed-as-email",
                    delivery_status="sent",
                    accepted_at=timezone.now(),
                )

        adapter = RecordingEmailAdapter()
        execute_communication_job(job.pk, adapter=adapter)

        self.assertEqual(adapter.calls, 0, "SMS was routed through send_email().")


def main() -> int:
    runner = DiscoverRunner(verbosity=2, interactive=False)
    runner.setup_test_environment()
    old_config = runner.setup_databases()
    try:
        suite = unittest.TestSuite(
            [
                SmsChannelProbe("test_sms_job_never_calls_email_adapter"),
                FinalAttemptRecoveryProbe(
                    "test_final_attempt_crash_becomes_failed_with_operator_task"
                ),
                QueuedJobMigrationProbe(
                    "test_queued_frozen_job_migrates_without_becoming_legacy"
                ),
            ]
        )
        result = runner.run_suite(suite)
        return len(result.failures) + len(result.errors)
    finally:
        runner.teardown_databases(old_config)
        runner.teardown_test_environment()


if __name__ == "__main__":
    raise SystemExit(main())
