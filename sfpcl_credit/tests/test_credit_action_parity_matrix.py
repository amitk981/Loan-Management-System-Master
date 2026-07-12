"""Executable public credit action/write parity matrix for slice 006X5."""

from django.apps import apps
from django.test import TestCase

from sfpcl_credit.approvals.modules.sanction_handoff import SanctionHandoffModule
from sfpcl_credit.credit.models import LoanAppraisalNote
from sfpcl_credit.credit.modules.appraisal_workflow import AppraisalWorkflow
from sfpcl_credit.credit.modules.common import (
    CreditModuleInvalidStateError,
    CreditModulePermissionDenied,
)
from sfpcl_credit.credit.modules.eligibility_assessment import EligibilityAssessmentModule
from sfpcl_credit.credit.modules.loan_limit_calculator import LoanLimitCalculator
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.tests import test_appraisal_api as appraisal_fixtures
from sfpcl_credit.tests import test_credit_modules as credit_fixtures
from sfpcl_credit.tests import test_sanction_submission_api as sanction_fixtures
from sfpcl_credit.workflows.models import WorkflowEvent


ACTION_FIELDS = {
    "action_code",
    "label",
    "enabled",
    "disabled_reason",
    "required_permission",
    "required_role",
}
ACTION_MATRIX = (
    "credit.eligibility.run",
    "credit.loan_limit.calculate",
    "credit.appraisal.create",
    "credit.appraisal.update",
    "revalidate_appraisal_prerequisites",
    "credit.appraisal.submit_review",
    "credit.appraisal.review:reviewed",
    "credit.appraisal.review:returned",
    "credit.appraisal.review:rejected",
    "credit.appraisal.submit_sanction",
)


def action(snapshot, code):
    projected = {item["action_code"]: item for item in snapshot["available_actions"]}[code]
    assert set(projected) == ACTION_FIELDS
    return projected


class MatrixInventoryTests(TestCase):
    def test_matrix_enumerates_every_required_public_write_once(self):
        self.assertEqual(len(ACTION_MATRIX), len(set(ACTION_MATRIX)))
        self.assertEqual(
            set(ACTION_MATRIX),
            {
                "credit.eligibility.run",
                "credit.loan_limit.calculate",
                "credit.appraisal.create",
                "credit.appraisal.update",
                "revalidate_appraisal_prerequisites",
                "credit.appraisal.submit_review",
                "credit.appraisal.review:reviewed",
                "credit.appraisal.review:returned",
                "credit.appraisal.review:rejected",
                "credit.appraisal.submit_sanction",
            },
        )


class EligibilityActionWriteMatrixTests(TestCase):
    setUp = credit_fixtures.CreditEligibilityModuleTests.setUp
    _permission = staticmethod(credit_fixtures.CreditEligibilityModuleTests._permission)
    _user = staticmethod(credit_fixtures.CreditEligibilityModuleTests._user)
    _verified_required_documents = credit_fixtures.CreditEligibilityModuleTests._verified_required_documents

    def test_enabled_run_succeeds_and_disabled_run_has_exact_reason_and_no_evidence(self):
        module = EligibilityAssessmentModule()
        first = module.run(actor=self.actor, application_id=self.application.pk)
        enabled = action(first.snapshot, "credit.eligibility.run")
        self.assertTrue(enabled["enabled"])
        self.assertIsNone(enabled["disabled_reason"])
        second = module.run(actor=self.actor, application_id=self.application.pk)
        self.assertEqual(second.snapshot["overall_result"], "eligible")

        read_only = {"applications.loan_application.read"}
        disabled = action(
            module.get(actor=self.actor, application_id=self.application.pk, actor_permissions=read_only).snapshot,
            "credit.eligibility.run",
        )
        self.assertFalse(disabled["enabled"])
        before = (AuditLog.objects.count(), WorkflowEvent.objects.count(), second.snapshot)
        with self.assertRaisesMessage(CreditModulePermissionDenied, disabled["disabled_reason"]):
            module.run(actor=self.actor, application_id=self.application.pk, actor_permissions=read_only)
        self.assertEqual((AuditLog.objects.count(), WorkflowEvent.objects.count()), before[:2])
        self.assertEqual(module.get(actor=self.actor, application_id=self.application.pk).snapshot["overall_result"], before[2]["overall_result"])


class LoanLimitActionWriteMatrixTests(TestCase):
    setUp = credit_fixtures.CreditEligibilityModuleTests.setUp
    _permission = staticmethod(credit_fixtures.CreditEligibilityModuleTests._permission)
    _user = staticmethod(credit_fixtures.CreditEligibilityModuleTests._user)
    _verified_required_documents = credit_fixtures.CreditEligibilityModuleTests._verified_required_documents
    _shareholding = credit_fixtures.CreditEligibilityModuleTests._shareholding
    _active_loan_policy = staticmethod(credit_fixtures.CreditEligibilityModuleTests._active_loan_policy)
    _loan_limit_payload = credit_fixtures.CreditEligibilityModuleTests._loan_limit_payload

    def test_enabled_calculation_succeeds_and_disabled_calculation_has_exact_reason_and_no_evidence(self):
        EligibilityAssessmentModule().run(actor=self.actor, application_id=self.application.pk)
        shareholding = self._shareholding()
        self._active_loan_policy()
        payload = self._loan_limit_payload(shareholding)
        module = LoanLimitCalculator()
        first = module.calculate_for_application(actor=self.actor, application_id=self.application.pk, payload=payload)
        enabled = action(first.snapshot, "credit.loan_limit.calculate")
        self.assertTrue(enabled["enabled"])
        second = module.calculate_for_application(actor=self.actor, application_id=self.application.pk, payload=payload)
        self.assertEqual(second.snapshot["loan_limit_assessment_id"], first.snapshot["loan_limit_assessment_id"])

        read_only = {"applications.loan_application.read"}
        disabled = action(module.get_assessment(actor=self.actor, application_id=self.application.pk, actor_permissions=read_only).snapshot, "credit.loan_limit.calculate")
        self.assertFalse(disabled["enabled"])
        before = (AuditLog.objects.count(), WorkflowEvent.objects.count(), second.snapshot)
        with self.assertRaisesMessage(CreditModulePermissionDenied, disabled["disabled_reason"]):
            module.calculate_for_application(actor=self.actor, application_id=self.application.pk, payload=payload, actor_permissions=read_only)
        self.assertEqual((AuditLog.objects.count(), WorkflowEvent.objects.count()), before[:2])
        self.assertEqual(module.get_assessment(actor=self.actor, application_id=self.application.pk).snapshot["loan_limit_assessment_id"], before[2]["loan_limit_assessment_id"])


class AppraisalActionWriteMatrixTests(TestCase):
    setUp = appraisal_fixtures.AppraisalApiTests.setUp
    _payload = appraisal_fixtures.AppraisalApiTests._payload
    _permission = staticmethod(appraisal_fixtures.AppraisalApiTests._permission)
    _user = staticmethod(appraisal_fixtures.AppraisalApiTests._user)

    def _create(self):
        return AppraisalWorkflow().create_or_update(actor=self.actor, application_id=self.application.pk, payload=self._payload()).snapshot

    def _review_ready(self):
        created = self._create()
        AppraisalWorkflow().submit_for_review(actor=self.actor, appraisal_id=created["loan_appraisal_note_id"], payload={"remarks": "Ready for independent review."})
        reviewer = self._user("credit.manager@sfpcl.example", self._permission("credit.appraisal.review", "Review appraisal"))
        self.application.received_by_user = reviewer
        self.application.save(update_fields=["received_by_user"])
        return created, reviewer

    def test_create_update_revalidate_and_submit_pair_enabled_success_with_disabled_denial(self):
        workflow = AppraisalWorkflow()
        limit = LoanLimitCalculator().get_assessment(actor=self.actor, application_id=self.application.pk)
        create_action = action(limit.snapshot, "credit.appraisal.create")
        self.assertTrue(create_action["enabled"])
        created = self._create()

        update_action = action(created, "credit.appraisal.update")
        self.assertTrue(update_action["enabled"])
        updated = workflow.create_or_update(actor=self.actor, application_id=self.application.pk, payload={"recommendation": "conditions"}, partial=True).snapshot
        self.assertEqual(updated["recommendation"], "conditions")

        note = LoanAppraisalNote.objects.get(pk=created["loan_appraisal_note_id"])
        note.prerequisite_provenance = "legacy_unverified"
        note.save(update_fields=["prerequisite_provenance"])
        projected = workflow.get(actor=self.actor, application_id=self.application.pk).snapshot
        revalidate_action = action(projected, "revalidate_appraisal_prerequisites")
        self.assertTrue(revalidate_action["enabled"])
        revalidated = workflow.revalidate_prerequisites(actor=self.actor, appraisal_id=note.pk, payload={}).snapshot
        self.assertEqual(revalidated["prerequisite_provenance"], "verified")

        submit_action = action(revalidated, "credit.appraisal.submit_review")
        self.assertTrue(submit_action["enabled"])
        submitted = workflow.submit_for_review(actor=self.actor, appraisal_id=note.pk, payload={"remarks": "Matrix submit."}).snapshot
        self.assertEqual(submitted["appraisal_status"], "review_pending")

    def test_each_appraisal_permission_denial_matches_projection_and_writes_no_evidence(self):
        workflow = AppraisalWorkflow()
        read_only = {"credit.appraisal.create"}
        limit = LoanLimitCalculator().get_assessment(actor=self.actor, application_id=self.application.pk, actor_permissions={"applications.loan_application.read"})
        create_disabled = action(limit.snapshot, "credit.appraisal.create")
        before = (AuditLog.objects.count(), WorkflowEvent.objects.count())
        with self.assertRaisesMessage(CreditModulePermissionDenied, create_disabled["disabled_reason"]):
            workflow.create_or_update(actor=self.actor, application_id=self.application.pk, payload=self._payload(), actor_permissions={"applications.loan_application.read", "credit.risk_assessment.manage"})
        self.assertEqual((AuditLog.objects.count(), WorkflowEvent.objects.count()), before)

        created = self._create()
        note = LoanAppraisalNote.objects.get(pk=created["loan_appraisal_note_id"])
        note.prerequisite_provenance = "legacy_unverified"
        note.save(update_fields=["prerequisite_provenance"])
        projected = workflow.get(actor=self.actor, application_id=self.application.pk, actor_permissions=read_only).snapshot
        calls = (
            ("credit.appraisal.update", lambda: workflow.create_or_update(actor=self.actor, application_id=self.application.pk, payload={"recommendation": "reject"}, partial=True, actor_permissions=read_only)),
            ("revalidate_appraisal_prerequisites", lambda: workflow.revalidate_prerequisites(actor=self.actor, appraisal_id=note.pk, payload={}, actor_permissions=read_only)),
            ("credit.appraisal.submit_review", lambda: workflow.submit_for_review(actor=self.actor, appraisal_id=note.pk, payload={"remarks": "Denied."}, actor_permissions=read_only)),
        )
        for code, write in calls:
            with self.subTest(code=code):
                denied = action(projected, code)
                self.assertFalse(denied["enabled"])
                evidence = (AuditLog.objects.count(), WorkflowEvent.objects.count())
                with self.assertRaisesMessage(CreditModulePermissionDenied, denied["disabled_reason"]):
                    write()
                self.assertEqual((AuditLog.objects.count(), WorkflowEvent.objects.count()), evidence)
        note.refresh_from_db()
        self.assertEqual(note.appraisal_status, "draft")
        self.assertEqual(note.prerequisite_provenance, "legacy_unverified")

    def _assert_review_pair(self, decision):
        created, reviewer = self._review_ready()
        workflow = AppraisalWorkflow()
        projected = workflow.get(actor=reviewer, application_id=self.application.pk).snapshot
        review_action = action(projected, "credit.appraisal.review")
        self.assertTrue(review_action["enabled"])
        payload = {"decision": decision, "review_comments": f"Matrix {decision}."}
        if decision == "rejected":
            payload.update(rejection_reason_category="eligibility", detailed_reason="Credit criteria were not met.", reapply_allowed_flag=True, communication_mode="email")
        result = workflow.review(actor=reviewer, appraisal_id=created["loan_appraisal_note_id"], decision=decision, comments=payload["review_comments"], payload_fields=payload).snapshot
        self.assertEqual(result["decision"], decision)
        self.assertEqual(len(result["review_history"]), 1)
        self.assertEqual(apps.get_model("applications", "RejectionNote").objects.count(), 1 if decision == "rejected" else 0)

    def test_reviewed_action_write_pair(self):
        self._assert_review_pair("reviewed")

    def test_returned_action_write_pair(self):
        self._assert_review_pair("returned")

    def test_rejected_action_write_pair_and_exact_note_cardinality(self):
        self._assert_review_pair("rejected")

    def test_review_denial_matches_projection_for_all_payloads_with_no_history_note_or_evidence(self):
        created, reviewer = self._review_ready()
        projected = AppraisalWorkflow().get(actor=reviewer, application_id=self.application.pk, actor_permissions={"credit.appraisal.create"}).snapshot
        denied = action(projected, "credit.appraisal.review")
        self.assertFalse(denied["enabled"])
        before = (AuditLog.objects.count(), WorkflowEvent.objects.count())
        for decision in ("reviewed", "returned", "rejected"):
            payload = {"decision": decision, "review_comments": "Denied matrix decision."}
            if decision == "rejected":
                payload.update(rejection_reason_category="eligibility", detailed_reason="Denied.", reapply_allowed_flag=True, communication_mode="email")
            with self.subTest(decision=decision), self.assertRaisesMessage(CreditModulePermissionDenied, denied["disabled_reason"]):
                AppraisalWorkflow().review(actor=reviewer, appraisal_id=created["loan_appraisal_note_id"], decision=decision, comments=payload["review_comments"], payload_fields=payload, actor_permissions={"credit.appraisal.create"})
        self.assertEqual((AuditLog.objects.count(), WorkflowEvent.objects.count()), before)
        self.assertEqual(apps.get_model("credit", "AppraisalReviewDecision").objects.count(), 0)
        self.assertEqual(apps.get_model("applications", "RejectionNote").objects.count(), 0)


class SanctionActionWriteMatrixTests(TestCase):
    setUp = sanction_fixtures.SanctionSubmissionApiTests.setUp
    _permission = staticmethod(sanction_fixtures.SanctionSubmissionApiTests._permission)
    _user = staticmethod(sanction_fixtures.SanctionSubmissionApiTests._user)

    def test_enabled_sanction_write_creates_exact_case_and_denied_state_creates_none(self):
        projected = AppraisalWorkflow().get(actor=self.reviewer, application_id=self.application.pk).snapshot
        enabled = action(projected, "credit.appraisal.submit_sanction")
        self.assertTrue(enabled["enabled"])
        result = SanctionHandoffModule().submit_reviewed_appraisal(actor=self.reviewer, application_id=self.application.pk, payload={"remarks": "Matrix sanction."}).snapshot
        self.assertEqual(result["submission_status"], "pending")
        self.assertEqual(apps.get_model("approvals", "ApprovalCase").objects.count(), 1)

    def test_disabled_sanction_reason_matches_write_and_has_zero_case_or_evidence(self):
        self.note.appraisal_status = LoanAppraisalNote.STATUS_REVIEW_PENDING
        self.note.save(update_fields=["appraisal_status"])
        projected = AppraisalWorkflow().get(actor=self.reviewer, application_id=self.application.pk).snapshot
        denied = action(projected, "credit.appraisal.submit_sanction")
        self.assertFalse(denied["enabled"])
        before = (AuditLog.objects.count(), WorkflowEvent.objects.count())
        with self.assertRaisesMessage(CreditModuleInvalidStateError, denied["disabled_reason"]):
            SanctionHandoffModule().submit_reviewed_appraisal(actor=self.reviewer, application_id=self.application.pk, payload={"remarks": "Stale projection."})
        self.assertEqual((AuditLog.objects.count(), WorkflowEvent.objects.count()), before)
        self.assertEqual(apps.get_model("approvals", "ApprovalCase").objects.count(), 0)
