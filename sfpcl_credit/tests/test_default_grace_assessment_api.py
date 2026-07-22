import json
from datetime import date
from uuid import uuid4
from unittest.mock import patch

from django.test import Client, TestCase


class DefaultGraceAssessmentApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_default_case_opening_api import (
            DefaultCaseOpeningApiTests,
        )

        fixture = DefaultCaseOpeningApiTests(
            "test_missed_scheduled_principal_opens_one_audited_case"
        )
        fixture.setUp()
        self.fixture = fixture
        self.account = fixture.account
        self.actor = fixture.actor
        self.auth = fixture.auth
        self.client = Client()

    def _open_case(self, due_date):
        from sfpcl_credit.loans.models import RepaymentSchedule

        RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=due_date,
            principal_due="1000.00",
            interest_due="0.00",
            charges_due="0.00",
            total_due="1000.00",
            schedule_status="pending",
        )
        response = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/default-cases/open/",
            data=json.dumps(
                {
                    "trigger_event": "missed_principal_repayment",
                    "scheduled_due_date": due_date.isoformat(),
                    "reason": "Missed principal.",
                }
            ),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()["data"]["default_case_id"]

    def _make_assessor(self):
        from sfpcl_credit.identity.models import Team, UserTeamMembership

        user_fixture = self.fixture.fixture.fixture.fixture.owner.fixture.fixture
        assessor = user_fixture._user("deputy_manager_finance", "Grace Assessor")
        user_fixture._grant(
            assessor, "defaults.case.read", "defaults.assessment.create"
        )
        team, _ = Team.objects.get_or_create(
            team_code="credit_assessment",
            defaults={"team_name": "Credit Assessment Team"},
        )
        UserTeamMembership.objects.create(user=assessor, team=team, status="active")
        auth_fixture = self.fixture.fixture.fixture.fixture.owner.fixture
        return assessor, auth_fixture._auth(assessor)

    def _evidence_document(self, *, account=None, suffix="current"):
        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.legal_documents.models import LoanDocument

        account = account or self.account
        document = DocumentFile.objects.create(
            file_name=f"default-evidence-{suffix}.pdf",
            storage_provider="local",
            storage_key=f"defaults/{suffix}.pdf",
            sensitivity_level="confidential",
        )
        LoanDocument.objects.create(
            loan_application=account.loan_application,
            document_type="default_assessment_evidence",
            document_category="recovery",
            document=document,
            output_format="pdf",
            generation_status="generated",
            execution_status="pending",
            verification_status="pending",
        )
        return document

    @staticmethod
    def _assessment_payload(evidence_id):
        return {
            "assessment_type": "post_grace",
            "payment_failure_classification": "non_intentional",
            "reason_summary": "Crop loss and delayed produce payment.",
            "evidence_document_ids": [str(evidence_id)],
            "borrower_interaction_summary": "Borrower explained the seasonal delay.",
            "recommended_action": "grant_extension",
        }

    def test_detail_derives_month_end_grace_boundary_from_server_date(self):
        case_id = self._open_case(date(2026, 1, 31))

        for server_date, expected_state in (
            (date(2026, 4, 29), "active"),
            (date(2026, 4, 30), "active"),
            (date(2026, 5, 1), "expired"),
        ):
            with self.subTest(server_date=server_date), patch(
                "sfpcl_credit.defaults.modules.default_workflow.timezone.localdate",
                return_value=server_date,
            ):
                response = self.client.get(
                    f"/api/v1/default-cases/{case_id}/", **self.auth
                )

            self.assertEqual(response.status_code, 200, response.content)
            self.assertEqual(
                response.json()["data"]["grace_period_end_date"], "2026-04-30"
            )
            self.assertEqual(response.json()["data"]["grace_state"], expected_state)

    def test_allocated_full_principal_during_grace_cures_and_retains_case(self):
        from sfpcl_credit.defaults.models import DefaultCase
        from sfpcl_credit.defaults.modules.default_workflow import DefaultWorkflow
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.workflows.models import WorkflowEvent

        user_fixture = self.fixture.fixture.fixture.fixture.owner.fixture.fixture
        user_fixture._grant(
            self.actor,
            "finance.repayment.create",
            "finance.repayment.mark_sap_posted",
            "finance.repayment.allocate",
        )
        type(self.account).objects.filter(pk=self.account.pk).update(
            principal_outstanding="1000.00",
            interest_outstanding="0.00",
            charges_outstanding="0.00",
            total_outstanding="1000.00",
        )
        case_id = self._open_case(date(2026, 1, 31))
        captured = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/repayments/",
            data=json.dumps(
                {
                    "repayment_source": "direct_farmer",
                    "amount_received": "1000.00",
                    "received_date": "2026-04-15",
                    "payment_method": "neft",
                    "bank_reference_number": "UTR-GRACE-CURE-001",
                    "remarks": "Full principal received during grace.",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="grace-cure-capture",
            **self.auth,
        )
        self.assertEqual(captured.status_code, 200, captured.content)
        repayment_id = captured.json()["data"]["repayment_id"]
        posted = self.client.post(
            f"/api/v1/repayments/{repayment_id}/mark-sap-posted/",
            data=json.dumps(
                {
                    "sap_entry_reference": "SAP-GRACE-CURE-001",
                    "sap_posted_at": "2026-04-15T10:00:00Z",
                    "remarks": "Posting confirmed.",
                }
            ),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(posted.status_code, 200, posted.content)
        allocated = self.client.post(
            f"/api/v1/repayments/{repayment_id}/allocate/",
            data=json.dumps(
                {
                    "allocation_rule": "principal_first",
                    "remarks": "Apply full principal during grace.",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="grace-cure-allocation",
            **self.auth,
        )
        self.assertEqual(allocated.status_code, 200, allocated.content)

        with patch(
            "sfpcl_credit.defaults.modules.default_workflow.timezone.localdate",
            return_value=date(2026, 4, 15),
        ):
            derived = self.client.get(
                f"/api/v1/default-cases/{case_id}/", **self.auth
            )
        self.assertEqual(derived.status_code, 200, derived.content)
        self.assertEqual(derived.json()["data"]["grace_state"], "cured")

        outcome = DefaultWorkflow.process_grace_expiries(
            as_of_date=date(2026, 4, 15), actor=self.actor
        )

        self.assertEqual(
            outcome,
            {
                "processed_count": 1,
                "cured_count": 1,
                "expired_count": 0,
                "assessment_tasks_created_count": 0,
                "failure_count": 0,
            },
        )
        case = DefaultCase.objects.get(pk=case_id)
        self.assertEqual(case.default_case_status, "resolved_by_repayment")
        self.assertIsNotNone(case.closed_at)
        self.assertEqual(DefaultCase.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="default.grace_cured").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="default_case", to_state="resolved_by_repayment"
            ).count(),
            1,
        )

    def test_unpaid_expiry_creates_one_assessment_task_under_replay(self):
        from sfpcl_credit.defaults.models import DefaultCase
        from sfpcl_credit.defaults.modules.default_workflow import DefaultWorkflow
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.scheduler.models import ScheduledJob
        from sfpcl_credit.workflows.models import WorkflowEvent

        case_id = self._open_case(date(2023, 11, 30))

        first = DefaultWorkflow.process_grace_expiries(
            as_of_date=date(2024, 3, 1), actor=self.actor
        )
        replay = DefaultWorkflow.process_grace_expiries(
            as_of_date=date(2024, 3, 1), actor=self.actor
        )

        self.assertEqual(
            first,
            {
                "processed_count": 1,
                "cured_count": 0,
                "expired_count": 1,
                "assessment_tasks_created_count": 1,
                "failure_count": 0,
            },
        )
        self.assertEqual(replay["processed_count"], 0)
        case = DefaultCase.objects.get(pk=case_id)
        self.assertEqual(case.grace_period_end_date, date(2024, 2, 29))
        self.assertEqual(case.default_case_status, "grace_period_expired")
        task = ScheduledJob.objects.get()
        self.assertEqual(task.job_type, "default_assessment")
        self.assertEqual(task.related_entity_type, "default_case")
        self.assertEqual(task.related_entity_id, case.pk)
        self.assertEqual(task.idempotency_key, f"default-assessment:{case.pk}")
        self.assertEqual(
            AuditLog.objects.filter(action="default.grace_expired").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="default_case", to_state="grace_period_expired"
            ).count(),
            1,
        )

    def test_credit_assessment_team_stores_expired_case_assessment_and_projects_it(self):
        from sfpcl_credit.defaults.models import DefaultAssessment
        from sfpcl_credit.defaults.modules.default_workflow import DefaultWorkflow
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.workflows.models import WorkflowEvent

        case_id = self._open_case(date(2023, 11, 30))
        DefaultWorkflow.process_grace_expiries(
            as_of_date=date(2024, 3, 1), actor=self.actor
        )
        assessor, assessor_auth = self._make_assessor()
        evidence = self._evidence_document()
        payload = self._assessment_payload(evidence.pk)

        actionable = self.client.get(
            f"/api/v1/default-cases/{case_id}/", **assessor_auth
        )
        self.assertEqual(actionable.status_code, 200, actionable.content)
        self.assertEqual(actionable.json()["data"]["available_actions"], ["assess"])

        response = self.client.post(
            f"/api/v1/default-cases/{case_id}/assess/",
            data=json.dumps(payload),
            content_type="application/json",
            **assessor_auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        assessment = DefaultAssessment.objects.get()
        expected = {
            "default_assessment_id": str(assessment.pk),
            "default_case_id": case_id,
            **payload,
            "assessed_by_user_id": str(assessor.pk),
            "assessed_at": assessment.assessed_at.isoformat().replace("+00:00", "Z"),
        }
        self.assertEqual(response.json()["data"], expected)
        detail = self.client.get(
            f"/api/v1/default-cases/{case_id}/", **assessor_auth
        )
        self.assertEqual(detail.status_code, 200, detail.content)
        self.assertEqual(detail.json()["data"]["current_assessment"], expected)
        self.assertEqual(
            detail.json()["data"]["default_case_status"], "assessment_in_progress"
        )
        listing = self.client.get(
            "/api/v1/default-cases/?default_case_status=assessment_in_progress",
            **assessor_auth,
        )
        self.assertEqual(listing.status_code, 200, listing.content)
        self.assertEqual(listing.json()["data"][0]["current_assessment"], expected)
        self.assertEqual(
            AuditLog.objects.filter(action="default.assessed").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="default_case", to_state="assessment_in_progress"
            ).count(),
            1,
        )

    def test_invalid_or_missing_assessment_facts_are_zero_write(self):
        from sfpcl_credit.applications.models import LoanApplication
        from sfpcl_credit.defaults.models import DefaultAssessment
        from sfpcl_credit.defaults.modules.default_workflow import DefaultWorkflow
        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.legal_documents.models import LoanDocument
        from sfpcl_credit.workflows.models import WorkflowEvent

        case_id = self._open_case(date(2023, 11, 30))
        DefaultWorkflow.process_grace_expiries(
            as_of_date=date(2024, 3, 1), actor=self.actor
        )
        _, assessor_auth = self._make_assessor()
        evidence = self._evidence_document()
        foreign_application = LoanApplication.objects.create(
            member=self.account.member,
            borrower_type=self.account.loan_application.borrower_type,
            received_by_user=self.actor,
        )
        foreign_evidence = DocumentFile.objects.create(
            file_name="foreign-default-evidence.pdf",
            storage_provider="local",
            storage_key="defaults/foreign.pdf",
            sensitivity_level="confidential",
        )
        LoanDocument.objects.create(
            loan_application=foreign_application,
            document_type="default_assessment_evidence",
            document_category="recovery",
            document=foreign_evidence,
            output_format="pdf",
            generation_status="generated",
            execution_status="pending",
            verification_status="pending",
        )
        valid = self._assessment_payload(evidence.pk)
        invalid_payloads = (
            {**valid, "payment_failure_classification": "accidental"},
            {**valid, "reason_summary": ""},
            {**valid, "evidence_document_ids": []},
            {**valid, "evidence_document_ids": [str(uuid4())]},
            {**valid, "evidence_document_ids": [str(foreign_evidence.pk)]},
            {**valid, "caller_says_paid": False},
        )
        assessed_events_before = WorkflowEvent.objects.filter(
            workflow_name="default_case", to_state="assessment_in_progress"
        ).count()

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.client.post(
                    f"/api/v1/default-cases/{case_id}/assess/",
                    data=json.dumps(payload),
                    content_type="application/json",
                    **assessor_auth,
                )

                self.assertEqual(response.status_code, 400, response.content)
                self.assertEqual(DefaultAssessment.objects.count(), 0)
                self.assertEqual(
                    AuditLog.objects.filter(action="default.assessed").count(), 0
                )
                self.assertEqual(
                    WorkflowEvent.objects.filter(
                        workflow_name="default_case",
                        to_state="assessment_in_progress",
                    ).count(),
                    assessed_events_before,
                )

    def test_early_paid_closed_foreign_and_unauthorised_assessments_are_rejected(self):
        from django.utils import timezone

        from sfpcl_credit.defaults.models import DefaultAssessment, DefaultCase
        from sfpcl_credit.defaults.modules.default_workflow import DefaultWorkflow
        from sfpcl_credit.identity.models import AuditLog

        case_id = self._open_case(date(2023, 11, 30))
        _, assessor_auth = self._make_assessor()
        evidence = self._evidence_document()
        payload = self._assessment_payload(evidence.pk)
        url = f"/api/v1/default-cases/{case_id}/assess/"

        early = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            **assessor_auth,
        )
        self.assertEqual(early.status_code, 409, early.content)
        DefaultWorkflow.process_grace_expiries(
            as_of_date=date(2024, 3, 1), actor=self.actor
        )

        type(self.account).objects.filter(pk=self.account.pk).update(
            principal_outstanding="0.00", total_outstanding="0.00"
        )
        paid = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            **assessor_auth,
        )
        self.assertEqual(paid.status_code, 409, paid.content)
        type(self.account).objects.filter(pk=self.account.pk).update(
            principal_outstanding="400000.00",
            total_outstanding="400000.00",
            loan_account_status="sanctioned",
        )
        foreign_scope = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            **assessor_auth,
        )
        self.assertEqual(foreign_scope.status_code, 404, foreign_scope.content)
        type(self.account).objects.filter(pk=self.account.pk).update(
            loan_account_status="active"
        )
        denied = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth,
        )
        guessed = self.client.post(
            f"/api/v1/default-cases/{uuid4()}/assess/",
            data=json.dumps(payload),
            content_type="application/json",
            **assessor_auth,
        )

        type(self.account).objects.filter(pk=self.account.pk).update(
            closed_at=timezone.now()
        )
        closed = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            **assessor_auth,
        )

        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(guessed.status_code, 404, guessed.content)
        self.assertEqual(closed.status_code, 409, closed.content)
        self.assertEqual(DefaultAssessment.objects.count(), 0)
        self.assertEqual(AuditLog.objects.filter(action="default.assessed").count(), 0)
        case = DefaultCase.objects.get(pk=case_id)
        self.assertEqual(case.default_case_status, "grace_period_expired")

    def test_duplicate_current_assessment_is_zero_write(self):
        from sfpcl_credit.defaults.models import DefaultAssessment
        from sfpcl_credit.defaults.modules.default_workflow import DefaultWorkflow
        from sfpcl_credit.identity.models import AuditLog

        case_id = self._open_case(date(2023, 11, 30))
        DefaultWorkflow.process_grace_expiries(
            as_of_date=date(2024, 3, 1), actor=self.actor
        )
        _, assessor_auth = self._make_assessor()
        evidence = self._evidence_document()
        payload = self._assessment_payload(evidence.pk)
        url = f"/api/v1/default-cases/{case_id}/assess/"
        first = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            **assessor_auth,
        )
        replay = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            **assessor_auth,
        )

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 409, replay.content)
        self.assertEqual(DefaultAssessment.objects.count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="default.assessed").count(), 1)

    def test_expiry_processor_records_bounded_failure_without_partial_transition(self):
        from django.utils import timezone

        from sfpcl_credit.defaults.models import DefaultCase
        from sfpcl_credit.defaults.modules.default_workflow import DefaultWorkflow
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.scheduler import services

        case_id = self._open_case(date(2023, 11, 30))
        task, _ = services.enqueue_scheduled_job(
            job_type="default_assessment",
            due_at=timezone.now(),
            idempotency_key=f"default-assessment:{case_id}",
            related_entity_type="default_case",
            related_entity_id=case_id,
        )
        services.mark_job_running(task.pk)
        services.mark_job_succeeded(task.pk)

        outcome = DefaultWorkflow.process_grace_expiries(
            as_of_date=date(2024, 3, 1), actor=self.actor
        )

        self.assertEqual(
            outcome,
            {
                "processed_count": 1,
                "cured_count": 0,
                "expired_count": 0,
                "assessment_tasks_created_count": 0,
                "failure_count": 1,
            },
        )
        case = DefaultCase.objects.get(pk=case_id)
        self.assertEqual(case.default_case_status, "grace_period_active")
        self.assertEqual(
            AuditLog.objects.filter(action="default.grace_expired").count(), 0
        )

    def test_unallocated_and_partial_payment_do_not_falsely_cure(self):
        from sfpcl_credit.defaults.models import DefaultCase
        from sfpcl_credit.defaults.modules.default_workflow import DefaultWorkflow
        from sfpcl_credit.identity.models import AuditLog

        user_fixture = self.fixture.fixture.fixture.fixture.owner.fixture.fixture
        user_fixture._grant(
            self.actor,
            "finance.repayment.create",
            "finance.repayment.mark_sap_posted",
            "finance.repayment.allocate",
        )
        type(self.account).objects.filter(pk=self.account.pk).update(
            principal_outstanding="1000.00",
            interest_outstanding="0.00",
            charges_outstanding="0.00",
            total_outstanding="1000.00",
        )
        case_id = self._open_case(date(2026, 1, 31))
        captured = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/repayments/",
            data=json.dumps(
                {
                    "repayment_source": "direct_farmer",
                    "amount_received": "500.00",
                    "received_date": "2026-04-10",
                    "payment_method": "neft",
                    "bank_reference_number": "UTR-GRACE-PARTIAL-001",
                    "remarks": "Partial amount received during grace.",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="grace-partial-capture",
            **self.auth,
        )
        self.assertEqual(captured.status_code, 200, captured.content)
        repayment_id = captured.json()["data"]["repayment_id"]

        unallocated = DefaultWorkflow.process_grace_expiries(
            as_of_date=date(2026, 4, 10), actor=self.actor
        )
        self.assertEqual(unallocated["cured_count"], 0)
        posted = self.client.post(
            f"/api/v1/repayments/{repayment_id}/mark-sap-posted/",
            data=json.dumps(
                {
                    "sap_entry_reference": "SAP-GRACE-PARTIAL-001",
                    "sap_posted_at": "2026-04-10T10:00:00Z",
                    "remarks": "Posting confirmed.",
                }
            ),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(posted.status_code, 200, posted.content)
        allocated = self.client.post(
            f"/api/v1/repayments/{repayment_id}/allocate/",
            data=json.dumps(
                {
                    "allocation_rule": "principal_first",
                    "remarks": "Apply partial principal during grace.",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="grace-partial-allocation",
            **self.auth,
        )
        self.assertEqual(allocated.status_code, 200, allocated.content)

        partial = DefaultWorkflow.process_grace_expiries(
            as_of_date=date(2026, 4, 11), actor=self.actor
        )

        self.assertEqual(partial["cured_count"], 0)
        self.assertEqual(
            DefaultCase.objects.get(pk=case_id).default_case_status,
            "grace_period_active",
        )
        self.assertEqual(
            AuditLog.objects.filter(action="default.grace_cured").count(), 0
        )

    def test_scheduled_expiry_entrypoint_returns_only_bounded_counts(self):
        from sfpcl_credit.processes.tasks import dispatch_default_grace_expiries

        self._open_case(date(2023, 11, 30))

        with patch(
            "sfpcl_credit.processes.tasks.timezone.localdate",
            return_value=date(2024, 3, 1),
        ):
            outcome = dispatch_default_grace_expiries()

        self.assertEqual(
            outcome,
            {
                "processed_count": 1,
                "cured_count": 0,
                "expired_count": 1,
                "assessment_tasks_created_count": 1,
                "failure_count": 0,
            },
        )
