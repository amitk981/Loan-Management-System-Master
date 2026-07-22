import json
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from threading import Barrier
from unittest import skipUnless

from django.db import close_old_connections, connection
from django.test import Client, TransactionTestCase


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class DefaultCaseOpeningPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.tests.test_default_case_opening_api import (
            DefaultCaseOpeningApiTests,
        )

        fixture = DefaultCaseOpeningApiTests(
            "test_missed_scheduled_principal_opens_one_audited_case"
        )
        fixture.setUp()
        self.account = fixture.account
        self.auth = fixture.auth
        self.due_date = date(2026, 6, 22)
        RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=self.due_date,
            principal_due="1000.00",
            interest_due="0.00",
            charges_due="0.00",
            total_due="1000.00",
            schedule_status="pending",
        )

    def test_concurrent_open_attempts_create_one_case_and_transition_chain(self):
        from sfpcl_credit.defaults.models import DefaultCase
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.workflows.models import WorkflowEvent

        barrier = Barrier(2)
        payload = {
            "trigger_event": "missed_principal_repayment",
            "scheduled_due_date": self.due_date.isoformat(),
            "reason": "Concurrent missed principal detection.",
        }

        def submit(_):
            close_old_connections()
            try:
                barrier.wait(timeout=15)
                return Client().post(
                    f"/api/v1/loan-accounts/{self.account.pk}/default-cases/open/",
                    data=json.dumps(payload),
                    content_type="application/json",
                    **self.auth,
                )
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(pool.map(submit, range(2)))

        self.assertEqual([response.status_code for response in responses], [200, 200])
        self.assertEqual(
            responses[0].json()["data"]["default_case_id"],
            responses[1].json()["data"]["default_case_id"],
        )
        self.assertEqual(DefaultCase.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="default.case_opened").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="default_case").count(), 1
        )
