import uuid

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from sfpcl_credit.communications.models import Notification
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.scheduler import services
from sfpcl_credit.scheduler.models import ScheduledJob


class SchedulerServiceTests(TestCase):
    """003J: local scheduled-job metadata shell for later async work."""

    def test_enqueue_job_is_idempotent_for_same_key(self):
        due_at = timezone.now()
        related_entity_id = uuid.uuid4()

        first, first_created = services.enqueue_scheduled_job(
            job_type="report_export",
            due_at=due_at,
            idempotency_key="report-export:loan_portfolio:fy2026-q1",
            related_entity_type="quarterly_mis_report",
            related_entity_id=related_entity_id,
        )
        second, second_created = services.enqueue_scheduled_job(
            job_type="report_export",
            due_at=due_at,
            idempotency_key="report-export:loan_portfolio:fy2026-q1",
            related_entity_type="quarterly_mis_report",
            related_entity_id=related_entity_id,
        )

        self.assertTrue(first_created)
        self.assertFalse(second_created)
        self.assertEqual(first.job_id, second.job_id)
        self.assertEqual(ScheduledJob.objects.count(), 1)
        self.assertEqual(second.status, ScheduledJob.STATUS_QUEUED)
        self.assertEqual(second.attempts, 0)

    def test_enqueue_duplicate_race_returns_existing_runnable_job(self):
        due_at = timezone.now()
        existing = ScheduledJob.objects.create(
            job_type="notification_generation",
            status=ScheduledJob.STATUS_QUEUED,
            due_at=due_at,
            idempotency_key="notification:approval-assignment:123",
        )

        row, created = services.enqueue_scheduled_job(
            job_type="notification_generation",
            due_at=due_at,
            idempotency_key="notification:approval-assignment:123",
        )

        self.assertFalse(created)
        self.assertEqual(row.job_id, existing.job_id)
        self.assertEqual(ScheduledJob.objects.count(), 1)

    def test_job_status_transitions_are_validated(self):
        row, _ = services.enqueue_scheduled_job(
            job_type="reminder_generation",
            due_at=timezone.now(),
            idempotency_key="reminder:loan-account:123",
        )

        running = services.mark_job_running(row.job_id)
        self.assertEqual(running.status, ScheduledJob.STATUS_RUNNING)
        self.assertEqual(running.attempts, 1)
        succeeded = services.mark_job_succeeded(row.job_id)
        self.assertEqual(succeeded.status, ScheduledJob.STATUS_SUCCEEDED)
        self.assertIsNotNone(succeeded.completed_at)

        with self.assertRaises(ValidationError):
            services.mark_job_failed(row.job_id, "late provider response")

    def test_illegal_transition_from_queued_to_succeeded_is_rejected(self):
        row, _ = services.enqueue_scheduled_job(
            job_type="report_export",
            due_at=timezone.now(),
            idempotency_key="report-export:queued-only",
        )

        with self.assertRaises(ValidationError):
            services.mark_job_succeeded(row.job_id)

        row.refresh_from_db()
        self.assertEqual(row.status, ScheduledJob.STATUS_QUEUED)
        self.assertEqual(row.attempts, 0)

    def test_scheduler_shell_does_not_generate_notifications_or_audit_read_state(self):
        services.enqueue_scheduled_job(
            job_type="notification_generation",
            due_at=timezone.now(),
            idempotency_key="notification:shell-only",
            related_entity_type="loan_application",
            related_entity_id=uuid.uuid4(),
        )

        self.assertEqual(Notification.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(
                action="communications.notification.marked_read"
            ).count(),
            0,
        )
