from concurrent.futures import ThreadPoolExecutor
from datetime import date
from unittest import skipUnless

from django.db import close_old_connections, connection
from django.test import TransactionTestCase

from sfpcl_credit.communications.models import Notification
from sfpcl_credit.compliance.models import ComplianceControl, ComplianceTask
from sfpcl_credit.identity.models import Role, User


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class ComplianceControlSchedulerPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def test_concurrent_scheduler_runs_create_one_task_and_notification(self):
        owner_role = Role.objects.create(role_code="company_secretary", role_name="CS")
        reviewer_role = Role.objects.create(role_code="cfo", role_name="CFO")
        owner = User.objects.create(full_name="Owner", email="pg-owner@example.test", primary_role=owner_role)
        reviewer = User.objects.create(full_name="Reviewer", email="pg-reviewer@example.test", primary_role=reviewer_role)
        ComplianceControl.objects.create(
            control_code="PG_RACE", control_name="PostgreSQL race", control_area="compliance",
            legal_basis="Acceptance fixture", control_type="detective", frequency="annual",
            owner_role_code=owner_role.role_code, owner_user=owner, reviewer_user=reviewer,
            first_due_date=date(2026, 3, 31), evidence_required="Governed evidence",
            risk_if_missed="Escalate", status="active",
        )

        def run():
            close_old_connections()
            from sfpcl_credit.compliance.modules.compliance_task_engine import ComplianceTaskEngine
            try:
                return ComplianceTaskEngine.generate_due_tasks(as_of_date=date(2026, 4, 1))
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            list(executor.map(lambda _value: run(), range(2)))

        self.assertEqual(ComplianceTask.objects.count(), 1)
        self.assertEqual(Notification.objects.filter(notification_type="compliance_overdue").count(), 1)
