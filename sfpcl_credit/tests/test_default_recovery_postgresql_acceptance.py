import json
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from threading import Barrier
from unittest import skipUnless
from unittest.mock import patch

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


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class NonPaymentNotePostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        from sfpcl_credit.tests.test_non_payment_note_workflow_api import (
            NonPaymentNoteWorkflowApiTests,
        )

        fixture = NonPaymentNoteWorkflowApiTests(
            "test_expired_unpaid_extension_creates_one_frozen_source_derived_draft"
        )
        fixture.setUp()
        self.fixture = fixture

    def test_five_concurrent_exact_creates_converge_on_one_note(self):
        from sfpcl_credit.defaults.models import NonPaymentNote
        from sfpcl_credit.identity.models import AuditLog

        case_id = self.fixture._expired_case()
        _, auth = self.fixture._creator()
        payload = {
            "reason_for_non_payment": "Concurrent extension failure narrative.",
            "intentionality_assessment": "unclear",
            "outstanding_principal_amount": "300000.00",
            "outstanding_interest_amount": "45000.00",
            "recommended_recovery_action": "present_to_sanction_committee",
        }
        barrier = Barrier(5)

        def create(_):
            close_old_connections()
            try:
                barrier.wait(timeout=15)
                return Client().post(
                    f"/api/v1/default-cases/{case_id}/non-payment-note/",
                    data=json.dumps(payload),
                    content_type="application/json",
                    **auth,
                )
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            responses = list(pool.map(create, range(5)))

        self.assertEqual([response.status_code for response in responses], [200] * 5)
        self.assertEqual(
            len(
                {
                    response.json()["data"]["non_payment_note_id"]
                    for response in responses
                }
            ),
            1,
        )
        self.assertEqual(NonPaymentNote.objects.count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="non_payment_note.created").count(), 1)

    def test_five_concurrent_exact_submits_converge_on_one_approval_chain(self):
        from sfpcl_credit.approvals.models import ApprovalCase
        from sfpcl_credit.defaults.models import NonPaymentNote
        from sfpcl_credit.identity.models import AuditLog, Permission, RolePermission

        created, _ = self.fixture._create_note()
        self.fixture._configure_committee()
        permission, _ = Permission.objects.get_or_create(
            permission_code="defaults.non_payment_note.submit",
            defaults={
                "permission_name": "Submit Non-Payment Note",
                "module_name": "defaults",
                "risk_level": "high",
            },
        )
        RolePermission.objects.get_or_create(
            role=self.fixture.fixture.actor.primary_role,
            permission=permission,
        )
        barrier = Barrier(5)

        def submit(_):
            close_old_connections()
            try:
                barrier.wait(timeout=15)
                return Client().post(
                    f"/api/v1/non-payment-notes/{created['non_payment_note_id']}"
                    "/submit-to-sanction-committee/",
                    data=json.dumps({}),
                    content_type="application/json",
                    **self.fixture.fixture.auth,
                )
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            responses = list(pool.map(submit, range(5)))

        self.assertEqual([response.status_code for response in responses], [200] * 5)
        self.assertEqual(
            len({response.json()["data"]["approval_case_id"] for response in responses}),
            1,
        )
        self.assertEqual(
            ApprovalCase.objects.filter(approval_type=ApprovalCase.TYPE_RECOVERY).count(), 1
        )
        self.assertEqual(NonPaymentNote.objects.get().status, NonPaymentNote.STATUS_SUBMITTED)
        self.assertEqual(AuditLog.objects.filter(action="non_payment_note.submitted").count(), 1)


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class RecoveryDecisionPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        from sfpcl_credit.tests.test_recovery_decision_api import (
            RecoveryDecisionApiTests,
        )

        fixture = RecoveryDecisionApiTests(
            "test_matching_terminal_approval_creates_one_frozen_decision"
        )
        fixture.setUp()
        self.fixture = fixture

    def test_five_concurrent_exact_decisions_retain_one_record_and_event_chain(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.recovery.models import RecoveryDecision
        from sfpcl_credit.workflows.models import WorkflowEvent

        created, case, approvers, _ = self.fixture._submitted_case()
        self.fixture._force_terminal_approval(case, approvers)
        auth = self.fixture._grant_decider(approvers[0])
        payload = self.fixture._decision_payload(case)
        barrier = Barrier(5)

        def decide(_):
            close_old_connections()
            try:
                barrier.wait(timeout=15)
                return Client().post(
                    f"/api/v1/default-cases/{created['default_case_id']}"
                    "/recovery-decision/",
                    data=json.dumps(payload),
                    content_type="application/json",
                    **auth,
                )
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            responses = list(pool.map(decide, range(5)))

        self.assertEqual([response.status_code for response in responses], [200] * 5)
        self.assertEqual(
            len(
                {
                    response.json()["data"]["recovery_decision_id"]
                    for response in responses
                }
            ),
            1,
        )
        self.assertEqual(RecoveryDecision.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="recovery_decision.created").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="recovery_decision").count(),
            1,
        )


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class RecoveryActionPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        from sfpcl_credit.tests.test_recovery_action_api import RecoveryActionApiTests

        fixture = RecoveryActionApiTests(
            "test_company_secretary_initiates_exact_approved_sh4_with_governed_evidence"
        )
        fixture.setUp()
        self.fixture = fixture
        self.decision, _ = fixture._approved_decision()
        self.actor, self.auth = fixture._executor()
        fixture._held_sh4(self.actor)
        self.evidence = fixture._recovery_evidence(self.actor)

    def _initiate(self):
        return Client().post(
            f"/api/v1/recovery-decisions/{self.decision['recovery_decision_id']}/actions/",
            data=json.dumps(self.fixture._initiation_payload(self.evidence)),
            content_type="application/json",
            **self.auth,
        )

    def _race(self, submit):
        barrier = Barrier(5)

        def run(_):
            close_old_connections()
            try:
                barrier.wait(timeout=15)
                return submit()
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            return list(pool.map(run, range(5)))

    def test_five_initiations_retain_one_action_and_handoff_event(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.recovery.models import RecoveryAction
        from sfpcl_credit.workflows.models import WorkflowEvent

        responses = self._race(self._initiate)
        self.assertEqual([row.status_code for row in responses], [200] * 5)
        self.assertEqual(RecoveryAction.objects.count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="recovery.action.initiated").count(), 1)
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="recovery_action", to_state="pending").count(),
            1,
        )

    def test_five_completions_post_one_balance_movement(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import LoanAccount
        from sfpcl_credit.recovery.models import RecoveryAction

        initiated = self._initiate()
        action_id = initiated.json()["data"]["recovery_action_id"]
        before = LoanAccount.objects.get(pk=self.fixture.account.pk).principal_outstanding
        payload = {
            "completed_at": "2028-10-15T10:00:00Z",
            "amount_recovered": "1000.00",
            "evidence_document_ids": [str(self.evidence.pk)],
            "remarks": "Concurrent verified recovery completion.",
        }

        def complete():
            return Client().post(
                f"/api/v1/recovery-actions/{action_id}/complete/",
                data=json.dumps(payload),
                content_type="application/json",
                **self.auth,
            )

        responses = self._race(complete)
        self.assertEqual([row.status_code for row in responses], [200] * 5)
        self.assertEqual(RecoveryAction.objects.get().action_status, "completed")
        self.assertEqual(
            LoanAccount.objects.get(pk=self.fixture.account.pk).principal_outstanding,
            before - 1000,
        )
        self.assertEqual(AuditLog.objects.filter(action="recovery.proceeds_posted").count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="recovery.action.completed").count(), 1)

    def test_failed_loan_owner_call_rolls_back_terminal_state(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import LoanAccount
        from sfpcl_credit.loans.modules.recovery_proceeds import RecoveryProceedsConflict
        from sfpcl_credit.recovery.models import RecoveryAction

        initiated = self._initiate()
        action_id = initiated.json()["data"]["recovery_action_id"]
        before = LoanAccount.objects.values("principal_outstanding", "total_outstanding").get(
            pk=self.fixture.account.pk
        )
        with patch(
            "sfpcl_credit.recovery.modules.recovery_workflow.post_verified_recovery_proceeds",
            side_effect=RecoveryProceedsConflict("Injected owner failure."),
        ):
            response = Client().post(
                f"/api/v1/recovery-actions/{action_id}/complete/",
                data=json.dumps(
                    {
                        "completed_at": "2028-10-15T10:00:00Z",
                        "amount_recovered": "1000.00",
                        "evidence_document_ids": [str(self.evidence.pk)],
                        "remarks": "Verified recovery completion.",
                    }
                ),
                content_type="application/json",
                **self.auth,
            )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(RecoveryAction.objects.get().action_status, "pending")
        self.assertEqual(
            LoanAccount.objects.values("principal_outstanding", "total_outstanding").get(
                pk=self.fixture.account.pk
            ),
            before,
        )
        self.assertEqual(AuditLog.objects.filter(action="recovery.proceeds_posted").count(), 0)
        self.assertEqual(AuditLog.objects.filter(action="recovery.action.completed").count(), 0)


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class ClosureReadinessPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.close_payload = {
            "closure_type": "full_repayment",
            "closure_notes": "Concurrent fresh full-repayment financial close.",
        }
        if self._testMethodName == "test_close_vs_recovery_completion_never_closes_a_pending_action":
            return
        from sfpcl_credit.tests.test_closure_api import LoanClosureApiTests

        fixture = LoanClosureApiTests(
            "test_full_repayment_close_freezes_fresh_facts_and_creates_controlled_requirements"
        )
        fixture.setUp()
        self.fixture = fixture
        self.account = fixture.account
        self.actor = fixture.actor
        self.auth = fixture.auth

    def _close(self, key="postgres-close-001"):
        return Client().post(
            f"/api/v1/loan-accounts/{self.account.pk}/closure/",
            data=json.dumps(self.close_payload),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=key,
            **self.auth,
        )

    @staticmethod
    def _race(*operations):
        barrier = Barrier(len(operations))

        def run(operation):
            close_old_connections()
            try:
                barrier.wait(timeout=15)
                return operation()
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=len(operations)) as pool:
            return list(pool.map(run, operations))

    def test_five_duplicate_close_attempts_converge_on_one_financial_close(self):
        from sfpcl_credit.closure.models import ClosureRequirement, LoanClosure
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import LoanStatusHistory

        responses = self._race(*(lambda: self._close() for _ in range(5)))

        self.assertEqual([row.status_code for row in responses], [200] * 5)
        self.assertEqual(
            len({row.json()["data"]["loan_closure_id"] for row in responses}), 1
        )
        self.assertEqual(LoanClosure.objects.count(), 1)
        self.assertEqual(ClosureRequirement.objects.count(), 3)
        self.assertEqual(
            AuditLog.objects.filter(action="closure.loan.financially_closed").count(), 1
        )
        self.assertEqual(
            LoanStatusHistory.objects.filter(to_status="closed").count(), 1
        )

    def test_close_vs_repayment_serializes_to_one_admitted_mutation(self):
        from sfpcl_credit.closure.models import LoanClosure
        from sfpcl_credit.identity.models import Permission, RolePermission
        from sfpcl_credit.loans.models import LoanAccount, Repayment

        permission, _ = Permission.objects.get_or_create(
            permission_code="finance.repayment.create",
            defaults={
                "permission_name": "Capture repayment",
                "module_name": "finance",
                "risk_level": "high",
            },
        )
        RolePermission.objects.get_or_create(
            role=self.actor.primary_role, permission=permission
        )
        LoanAccount.objects.filter(pk=self.account.pk).update(disbursed_amount="100.00")

        def repay():
            return Client().post(
                f"/api/v1/loan-accounts/{self.account.pk}/repayments/",
                data=json.dumps(
                    {
                        "repayment_source": "direct_farmer",
                        "amount_received": "1.00",
                        "received_date": "2026-07-22",
                        "payment_method": "neft",
                        "bank_reference_number": "CLOSE-RACE-REPAY-001",
                        "remarks": "Concurrent repayment capture versus closure.",
                    }
                ),
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="close-race-repayment-001",
                **self.auth,
            )

        close_response, repayment_response = self._race(self._close, repay)

        self.assertEqual(
            sorted((close_response.status_code, repayment_response.status_code)),
            [200, 409],
        )
        self.assertEqual(LoanClosure.objects.count() + Repayment.objects.count(), 1)
        account = LoanAccount.objects.get(pk=self.account.pk)
        if LoanClosure.objects.exists():
            self.assertEqual(account.loan_account_status, "closed")
        else:
            self.assertNotEqual(account.loan_account_status, "closed")

    def test_close_vs_recovery_completion_never_closes_a_pending_action(self):
        from sfpcl_credit.closure.models import LoanClosure
        from sfpcl_credit.identity.models import Permission, RolePermission
        from sfpcl_credit.loans.models import LoanAccount
        from sfpcl_credit.recovery.models import RecoveryAction
        from sfpcl_credit.tests.test_recovery_action_api import RecoveryActionApiTests

        recovery_fixture = RecoveryActionApiTests(
            "test_company_secretary_initiates_exact_approved_sh4_with_governed_evidence"
        )
        recovery_fixture.setUp()
        decision, _ = recovery_fixture._approved_decision()
        recovery_actor, recovery_auth = recovery_fixture._executor()
        evidence = recovery_fixture._recovery_evidence(recovery_actor)
        initiated = Client().post(
            f"/api/v1/recovery-decisions/{decision['recovery_decision_id']}/actions/",
            data=json.dumps(recovery_fixture._initiation_payload(evidence)),
            content_type="application/json",
            **recovery_auth,
        )
        self.assertEqual(initiated.status_code, 200, initiated.content)
        action_id = initiated.json()["data"]["recovery_action_id"]
        self.account = recovery_fixture.account
        LoanAccount.objects.filter(pk=self.account.pk).update(
            principal_outstanding="0.00",
            interest_outstanding="0.00",
            charges_outstanding="0.00",
            total_outstanding="0.00",
            loan_account_status="under_recovery",
        )
        for code in ("closure.readiness.read", "closure.loan.close"):
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "closure",
                    "risk_level": "critical",
                },
            )
            RolePermission.objects.get_or_create(
                role=recovery_actor.primary_role, permission=permission
            )
        self.auth = recovery_auth

        def complete():
            return Client().post(
                f"/api/v1/recovery-actions/{action_id}/complete/",
                data=json.dumps(
                    {
                        "completed_at": "2028-10-15T10:00:00Z",
                        "amount_recovered": "0.00",
                        "evidence_document_ids": [str(evidence.pk)],
                        "remarks": "Concurrent zero residual recovery completion.",
                    }
                ),
                content_type="application/json",
                **recovery_auth,
            )

        close_response, completion_response = self._race(self._close, complete)

        self.assertEqual(completion_response.status_code, 200, completion_response.content)
        self.assertIn(close_response.status_code, {200, 409})
        self.assertEqual(RecoveryAction.objects.get(pk=action_id).action_status, "completed")
        if close_response.status_code == 200:
            self.assertEqual(LoanClosure.objects.filter(loan_account=self.account).count(), 1)
        else:
            self.assertEqual(LoanClosure.objects.filter(loan_account=self.account).count(), 0)


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class NocIssuancePostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        from sfpcl_credit.tests.test_noc_api import NocIssuanceApiTests

        fixture = NocIssuanceApiTests(
            "test_eligible_full_repayment_closure_issues_one_noc_and_queues_delivery"
        )
        fixture.setUp()
        self.fixture = fixture
        self.closure = fixture.closure
        self.document = fixture.document
        self.issuer = fixture.issuer
        self.auth = fixture.auth
        self.payload = {
            "document_id": str(self.document.pk),
            "delivery_mode": "email",
            "recipient_email": fixture.account.member.email,
            "signatory_user_id": str(self.issuer.pk),
        }

    def test_five_concurrent_issue_attempts_create_one_noc_document_and_delivery_chain(self):
        from sfpcl_credit.closure.models import NocRecord
        from sfpcl_credit.communications.models import Communication, CommunicationDeliveryJob
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.legal_documents.models import LoanDocument

        barrier = Barrier(5)

        def issue(_):
            close_old_connections()
            try:
                barrier.wait(timeout=15)
                return Client().post(
                    f"/api/v1/loan-closures/{self.closure.pk}/noc/",
                    data=json.dumps(self.payload),
                    content_type="application/json",
                    HTTP_IDEMPOTENCY_KEY="postgres-noc-issue-001",
                    **self.auth,
                )
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            responses = list(pool.map(issue, range(5)))

        self.assertEqual([response.status_code for response in responses], [200] * 5)
        self.assertEqual(len({row.json()["data"]["noc_id"] for row in responses}), 1)
        self.assertEqual(NocRecord.objects.count(), 1)
        self.assertEqual(LoanDocument.objects.filter(document_type="noc").count(), 1)
        self.assertEqual(Communication.objects.filter(related_entity_type="noc").count(), 1)
        self.assertEqual(CommunicationDeliveryJob.objects.count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="closure.noc.issued").count(), 1)


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class SecurityReturnPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        from sfpcl_credit.tests.test_security_return_api import SecurityReturnApiTests

        fixture = SecurityReturnApiTests(
            "test_no_security_closure_derives_not_applicable_items_and_completes"
        )
        fixture.setUp()
        self.closure = fixture.closure
        self.auth = fixture.auth

    @staticmethod
    def _race(*operations):
        barrier = Barrier(len(operations))

        def run(operation):
            close_old_connections()
            try:
                barrier.wait(timeout=15)
                return operation()
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=len(operations)) as pool:
            return list(pool.map(run, operations))

    def _record(self, key):
        return Client().post(
            f"/api/v1/loan-closures/{self.closure.pk}/security-return/",
            data=json.dumps({}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=key,
            **self.auth,
        )

    def test_five_exact_replays_create_one_return_and_one_item_set(self):
        from sfpcl_credit.closure.models import (
            SecurityReturn,
            SecurityReturnItem,
            SecurityReturnRequest,
        )
        from sfpcl_credit.identity.models import AuditLog

        responses = self._race(
            *(lambda: self._record("postgres-security-return-same") for _ in range(5))
        )

        self.assertEqual([response.status_code for response in responses], [200] * 5)
        self.assertEqual(SecurityReturn.objects.count(), 1)
        self.assertEqual(SecurityReturnItem.objects.count(), 4)
        self.assertEqual(SecurityReturnRequest.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(
                action="closure.security_return.item_transitioned"
            ).count(),
            4,
        )

    def test_five_changed_requests_admit_only_one_completed_return(self):
        from sfpcl_credit.closure.models import SecurityReturn, SecurityReturnRequest

        responses = self._race(
            *(
                lambda index=index: self._record(f"postgres-security-return-{index}")
                for index in range(5)
            )
        )

        self.assertEqual(
            sorted(response.status_code for response in responses),
            [200, 409, 409, 409, 409],
        )
        self.assertEqual(SecurityReturn.objects.count(), 1)
        self.assertEqual(SecurityReturnRequest.objects.count(), 1)
        self.assertEqual(SecurityReturn.objects.get().return_status, "completed")
