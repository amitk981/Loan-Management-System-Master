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


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class GracePeriodPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        from sfpcl_credit.tests.test_default_grace_assessment_api import (
            DefaultGraceAssessmentApiTests,
        )

        fixture = DefaultGraceAssessmentApiTests(
            "test_unpaid_expiry_creates_one_assessment_task_under_replay"
        )
        fixture.setUp()
        self.fixture = fixture
        self.actor = fixture.actor
        self.case_id = fixture._open_case(date(2023, 11, 30))

    def test_five_concurrent_expiry_and_assessment_runs_converge(self):
        from sfpcl_credit.defaults.models import DefaultAssessment, DefaultCase
        from sfpcl_credit.defaults.modules.default_workflow import DefaultWorkflow
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.scheduler.models import ScheduledJob
        from sfpcl_credit.workflows.models import WorkflowEvent

        barrier = Barrier(5)

        def process(_):
            close_old_connections()
            try:
                barrier.wait(timeout=15)
                return DefaultWorkflow.process_grace_expiries(
                    as_of_date=date(2024, 3, 1), actor=self.actor
                )
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            outcomes = list(pool.map(process, range(5)))

        self.assertEqual(sum(row["expired_count"] for row in outcomes), 1)
        self.assertEqual(
            sum(row["assessment_tasks_created_count"] for row in outcomes), 1
        )
        self.assertEqual(sum(row["failure_count"] for row in outcomes), 0)
        case = DefaultCase.objects.get(pk=self.case_id)
        self.assertEqual(case.default_case_status, "grace_period_expired")
        self.assertEqual(ScheduledJob.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="default.grace_expired").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="default_case", to_state="grace_period_expired"
            ).count(),
            1,
        )

        _, assessor_auth = self.fixture._make_assessor()
        evidence = self.fixture._evidence_document()
        payload = self.fixture._assessment_payload(evidence.pk)
        assessment_barrier = Barrier(5)

        def assess(_):
            close_old_connections()
            try:
                assessment_barrier.wait(timeout=15)
                return Client().post(
                    f"/api/v1/default-cases/{self.case_id}/assess/",
                    data=json.dumps(payload),
                    content_type="application/json",
                    **assessor_auth,
                )
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            responses = list(pool.map(assess, range(5)))

        self.assertEqual(
            sorted(response.status_code for response in responses),
            [200, 409, 409, 409, 409],
        )
        self.assertEqual(DefaultAssessment.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="default.assessed").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="default_case", to_state="assessment_in_progress"
            ).count(),
            1,
        )


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class ExtensionNotePostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        from sfpcl_credit.tests.test_extension_note_workflow_api import (
            ExtensionNoteWorkflowApiTests,
        )

        fixture = ExtensionNoteWorkflowApiTests(
            "test_eligible_case_grants_one_audited_extension_with_exact_loan_file_note"
        )
        fixture.setUp()
        self.fixture = fixture

    def test_five_concurrent_exact_grants_converge_on_one_note_and_transition(self):
        from sfpcl_credit.defaults.models import ExtensionNote
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.workflows.models import WorkflowEvent

        case_id, _ = self.fixture._eligible_case()
        document = self.fixture._extension_document()
        payload = {
            "extension_reason": "Concurrent documented hardship.",
            "extension_start_date": "2026-07-01",
            "extension_end_date": "2027-06-30",
            "document_id": str(document.pk),
        }
        barrier = Barrier(5)

        def submit(_):
            close_old_connections()
            try:
                barrier.wait(timeout=15)
                return Client().post(
                    f"/api/v1/default-cases/{case_id}/grant-extension/",
                    data=json.dumps(payload),
                    content_type="application/json",
                    **self.fixture.auth,
                )
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            responses = list(pool.map(submit, range(5)))

        self.assertEqual([row.status_code for row in responses], [200] * 5)
        self.assertEqual(len({row.json()["data"]["extension_note_id"] for row in responses}), 1)
        self.assertEqual(ExtensionNote.objects.count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="extension.granted").count(), 1)
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="default_case", to_state="extension_granted"
            ).count(),
            1,
        )

    def test_five_concurrent_expiry_runs_create_one_review_transition(self):
        from sfpcl_credit.defaults.models import ExtensionNote
        from sfpcl_credit.defaults.modules.default_workflow import DefaultWorkflow
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.scheduler.models import ScheduledJob

        self.fixture._grant_extension()
        barrier = Barrier(5)

        def process(_):
            close_old_connections()
            try:
                barrier.wait(timeout=15)
                return DefaultWorkflow.process_extension_expiries(
                    as_of_date=date(2027, 7, 1), actor=self.fixture.actor
                )
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            outcomes = list(pool.map(process, range(5)))

        self.assertEqual(sum(row["expired_count"] for row in outcomes), 1)
        self.assertEqual(sum(row["review_tasks_created_count"] for row in outcomes), 1)
        self.assertEqual(sum(row["failure_count"] for row in outcomes), 0)
        self.assertEqual(ExtensionNote.objects.get().status, "expired")
        self.assertEqual(ScheduledJob.objects.filter(job_type="default_assessment").count(), 2)
        self.assertEqual(AuditLog.objects.filter(action="extension.expired").count(), 1)
