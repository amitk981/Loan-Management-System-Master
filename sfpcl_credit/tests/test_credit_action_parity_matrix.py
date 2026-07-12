"""Executable public credit action/write parity matrix for slice 006X5."""

from django.apps import apps
from django.test import TestCase

from sfpcl_credit.approvals.modules.sanction_handoff import SanctionHandoffModule
from sfpcl_credit.credit.models import LoanAppraisalNote
from sfpcl_credit.credit.modules.appraisal_workflow import AppraisalWorkflow
from sfpcl_credit.credit.modules.common import (
    CreditModuleInvalidStateError,
    CreditModuleObjectAccessDenied,
    CreditModulePermissionDenied,
    CreditModuleValidationError,
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
PUBLIC_ACTIONS = {
    "credit.eligibility.run",
    "credit.loan_limit.calculate",
    "credit.appraisal.create",
    "credit.appraisal.update",
    "revalidate_appraisal_prerequisites",
    "credit.appraisal.submit_review",
    "credit.appraisal.review",
    "credit.appraisal.submit_sanction",
}

REQUIRED_VARIANTS = {
    "credit.eligibility.run": {"enabled", "permission", "object_scope", "state", "stale_state"},
    "credit.loan_limit.calculate": {"enabled", "permission", "object_scope", "state", "stale_state"},
    "credit.appraisal.create": {"enabled", "permission", "object_scope", "state"},
    "credit.appraisal.update": {"enabled", "permission", "object_scope", "state"},
    "revalidate_appraisal_prerequisites": {"enabled", "permission", "object_scope", "state", "frozen_provenance"},
    "credit.appraisal.submit_review": {"enabled", "permission", "object_scope", "state", "frozen_provenance"},
    "credit.appraisal.review": {"enabled", "permission", "role", "object_scope", "maker_checker", "state", "frozen_provenance", "rejection_payload"},
    "credit.appraisal.submit_sanction": {"enabled", "permission", "role", "object_scope", "state", "frozen_provenance", "immutable_review", "stale_state"},
}


def action(snapshot, code):
    projected = {item["action_code"]: item for item in snapshot["available_actions"]}[code]
    assert set(projected) == ACTION_FIELDS
    return projected


class MatrixInventoryTests(TestCase):
    def test_executable_case_catalogue_is_complete_and_uses_only_real_action_codes(self):
        executable = {}
        for case_class in (
            EligibilityActionWriteMatrixTests,
            LoanLimitActionWriteMatrixTests,
            AppraisalActionWriteMatrixTests,
            SanctionActionWriteMatrixTests,
        ):
            for action_code, variant in case_class.EXECUTED_CASES:
                executable.setdefault(action_code, set()).add(variant)
        self.assertEqual(set(executable), PUBLIC_ACTIONS)
        self.assertEqual(executable, REQUIRED_VARIANTS)
        self.assertNotIn("credit.appraisal.review:reviewed", executable)


class EligibilityActionWriteMatrixTests(TestCase):
    EXECUTED_CASES = (
        ("credit.eligibility.run", "enabled"),
        ("credit.eligibility.run", "permission"),
        ("credit.eligibility.run", "object_scope"),
        ("credit.eligibility.run", "state"),
        ("credit.eligibility.run", "stale_state"),
    )
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

    def test_state_and_stale_scope_variants_execute_the_same_public_run(self):
        module = EligibilityAssessmentModule()
        baseline = module.run(actor=self.actor, application_id=self.application.pk)
        original = {
            "application_reference_number": self.application.application_reference_number,
            "application_status": self.application.application_status,
            "completeness_status": self.application.completeness_status,
            "current_stage": self.application.current_stage,
        }
        variants = (
            ("application_reference_number", "DRAFT-999"),
            ("application_status", "draft"),
            ("completeness_status", "incomplete"),
        )
        for field, value in variants:
            with self.subTest(field=field):
                setattr(self.application, field, value)
                type(self.application).objects.filter(pk=self.application.pk).update(**{field: value})
                projected = module.get(actor=self.actor, application_id=self.application.pk).snapshot
                denied = action(projected, "credit.eligibility.run")
                before = self._eligibility_evidence()
                with self.assertRaises(CreditModuleInvalidStateError) as raised:
                    module.run(actor=self.actor, application_id=self.application.pk)
                self.assertEqual(str(raised.exception), denied["disabled_reason"])
                self.assertEqual(self._eligibility_evidence(), before)
                setattr(self.application, field, original[field])
                type(self.application).objects.filter(pk=self.application.pk).update(
                    **{field: original[field]}
                )

        enabled = action(
            module.get(actor=self.actor, application_id=self.application.pk).snapshot,
            "credit.eligibility.run",
        )
        self.assertTrue(enabled["enabled"])
        type(self.application).objects.filter(pk=self.application.pk).update(
            application_status="draft"
        )
        before = self._eligibility_evidence()
        with self.assertRaises(CreditModuleInvalidStateError):
            module.run(actor=self.actor, application_id=self.application.pk)
        self.assertEqual(self._eligibility_evidence(), before)
        type(self.application).objects.filter(pk=self.application.pk).update(
            application_status=original["application_status"]
        )
        outsider = self._user(
            "eligibility.matrix.outsider@sfpcl.example",
            apps.get_model("identity", "Permission").objects.get(
                permission_code="applications.loan_application.read"
            ),
        )
        type(self.application).objects.filter(pk=self.application.pk).update(
            created_by_user=outsider,
            received_by_user=outsider,
            current_stage="initial_loan_request",
        )
        before = self._eligibility_evidence()
        with self.assertRaises(CreditModuleObjectAccessDenied):
            module.run(actor=self.actor, application_id=self.application.pk)
        self.assertEqual(self._eligibility_evidence(), before)
        self.assertEqual(baseline.snapshot["eligibility_assessment_id"], before[2])

    @staticmethod
    def _eligibility_evidence():
        assessment = apps.get_model("credit", "EligibilityAssessment").objects.get()
        application = apps.get_model("applications", "LoanApplication").objects.get()
        return (
            application.application_status,
            application.current_stage,
            str(assessment.pk),
            assessment.overall_result,
            assessment.assessed_at,
            AuditLog.objects.count(),
            WorkflowEvent.objects.count(),
            apps.get_model("credit", "AppraisalReviewDecision").objects.count(),
            apps.get_model("applications", "RejectionNote").objects.count(),
            apps.get_model("approvals", "ApprovalCase").objects.count(),
        )


class LoanLimitActionWriteMatrixTests(TestCase):
    EXECUTED_CASES = (
        ("credit.loan_limit.calculate", "enabled"),
        ("credit.loan_limit.calculate", "permission"),
        ("credit.loan_limit.calculate", "object_scope"),
        ("credit.loan_limit.calculate", "state"),
        ("credit.loan_limit.calculate", "stale_state"),
    )
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

    def test_state_stale_state_and_object_scope_execute_calculation_without_loser_evidence(self):
        EligibilityAssessmentModule().run(actor=self.actor, application_id=self.application.pk)
        shareholding = self._shareholding()
        self._active_loan_policy()
        payload = self._loan_limit_payload(shareholding)
        module = LoanLimitCalculator()
        module.calculate_for_application(actor=self.actor, application_id=self.application.pk, payload=payload)

        eligibility = apps.get_model("credit", "EligibilityAssessment").objects.get()
        eligibility.overall_result = "ineligible"
        eligibility.save(update_fields=["overall_result"])
        projected = module.get_assessment(actor=self.actor, application_id=self.application.pk).snapshot
        denied = action(projected, "credit.loan_limit.calculate")
        before = self._limit_evidence()
        with self.assertRaises(CreditModuleInvalidStateError) as raised:
            module.calculate_for_application(actor=self.actor, application_id=self.application.pk, payload=payload)
        self.assertEqual(str(raised.exception), denied["disabled_reason"])
        self.assertEqual(self._limit_evidence(), before)

        eligibility.overall_result = "eligible"
        eligibility.save(update_fields=["overall_result"])
        stale_enabled = action(
            module.get_assessment(actor=self.actor, application_id=self.application.pk).snapshot,
            "credit.loan_limit.calculate",
        )
        self.assertTrue(stale_enabled["enabled"])
        AppraisalWorkflow().create_or_update(
            actor=self.actor,
            application_id=self.application.pk,
            payload=appraisal_fixtures.AppraisalApiTests._payload(self),
            actor_permissions={
                "applications.loan_application.read",
                "credit.appraisal.create",
                "credit.risk_assessment.manage",
            },
        )
        before = self._limit_evidence()
        with self.assertRaisesMessage(CreditModuleInvalidStateError, "after appraisal has started"):
            module.calculate_for_application(actor=self.actor, application_id=self.application.pk, payload=payload)
        self.assertEqual(self._limit_evidence(), before)

        apps.get_model("credit", "LoanAppraisalNote").objects.all().delete()
        outsider = self._user(
            "limit.matrix.outsider@sfpcl.example",
            apps.get_model("identity", "Permission").objects.get(
                permission_code="applications.loan_application.read"
            ),
        )
        self.assertTrue(action(module.get_assessment(actor=self.actor, application_id=self.application.pk).snapshot, "credit.loan_limit.calculate")["enabled"])
        type(self.application).objects.filter(pk=self.application.pk).update(
            created_by_user=outsider,
            received_by_user=outsider,
            current_stage="initial_loan_request",
        )
        before = self._limit_evidence()
        with self.assertRaises(CreditModuleObjectAccessDenied):
            module.calculate_for_application(actor=self.actor, application_id=self.application.pk, payload=payload)
        self.assertEqual(self._limit_evidence(), before)

    @staticmethod
    def _limit_evidence():
        assessment = apps.get_model("credit", "LoanLimitAssessment").objects.get()
        application = apps.get_model("applications", "LoanApplication").objects.get()
        return (
            application.application_status,
            application.current_stage,
            str(assessment.pk),
            assessment.final_eligible_loan_amount,
            assessment.calculated_at,
            AuditLog.objects.count(),
            WorkflowEvent.objects.count(),
            apps.get_model("credit", "AppraisalReviewDecision").objects.count(),
            apps.get_model("applications", "RejectionNote").objects.count(),
            apps.get_model("approvals", "ApprovalCase").objects.count(),
        )


class AppraisalActionWriteMatrixTests(TestCase):
    EXECUTED_CASES = tuple(
        (code, variant)
        for code, variants in {
            "credit.appraisal.create": ("enabled", "permission", "object_scope", "state"),
            "credit.appraisal.update": ("enabled", "permission", "object_scope", "state"),
            "revalidate_appraisal_prerequisites": ("enabled", "permission", "object_scope", "state", "frozen_provenance"),
            "credit.appraisal.submit_review": ("enabled", "permission", "object_scope", "state", "frozen_provenance"),
            "credit.appraisal.review": ("enabled", "permission", "role", "object_scope", "maker_checker", "state", "frozen_provenance", "rejection_payload"),
        }.items()
        for variant in variants
    )
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

    def test_create_update_revalidate_and_submit_execute_state_provenance_and_scope_denials(self):
        workflow = AppraisalWorkflow()
        eligibility = self.eligibility
        eligibility.overall_result = "ineligible"
        eligibility.save(update_fields=["overall_result"])
        projected = LoanLimitCalculator().get_assessment(
            actor=self.actor,
            application_id=self.application.pk,
        ).snapshot
        create_denied = action(projected, "credit.appraisal.create")
        before = self._appraisal_evidence()
        with self.assertRaises(CreditModuleInvalidStateError) as raised:
            workflow.create_or_update(actor=self.actor, application_id=self.application.pk, payload=self._payload())
        self.assertEqual(str(raised.exception), create_denied["disabled_reason"])
        self.assertEqual(self._appraisal_evidence(), before)
        eligibility.overall_result = "eligible"
        eligibility.save(update_fields=["overall_result"])

        create_enabled = action(
            LoanLimitCalculator().get_assessment(
                actor=self.actor,
                application_id=self.application.pk,
            ).snapshot,
            "credit.appraisal.create",
        )
        self.assertTrue(create_enabled["enabled"])
        create_outsider = self._user(
            "appraisal.create.outsider@sfpcl.example",
            apps.get_model("identity", "Permission").objects.get(
                permission_code="applications.loan_application.read"
            ),
        )
        type(self.application).objects.filter(pk=self.application.pk).update(
            created_by_user=create_outsider,
            received_by_user=create_outsider,
        )
        before = self._appraisal_evidence()
        with self.assertRaises(CreditModuleObjectAccessDenied):
            workflow.create_or_update(
                actor=self.actor,
                application_id=self.application.pk,
                payload=self._payload(),
            )
        self.assertEqual(self._appraisal_evidence(), before)
        type(self.application).objects.filter(pk=self.application.pk).update(
            created_by_user=self.actor,
            received_by_user=self.actor,
        )

        created = self._create()
        note_id = created["loan_appraisal_note_id"]
        outsider = self._user(
            "appraisal.matrix.outsider@sfpcl.example",
            apps.get_model("identity", "Permission").objects.get(
                permission_code="applications.loan_application.read"
            ),
        )
        self.assertTrue(action(created, "credit.appraisal.update")["enabled"])
        type(self.application).objects.filter(pk=self.application.pk).update(
            created_by_user=outsider,
            received_by_user=outsider,
        )
        before = self._appraisal_evidence()
        with self.assertRaises(CreditModuleObjectAccessDenied):
            workflow.create_or_update(
                actor=self.actor,
                application_id=self.application.pk,
                payload={"recommendation": "conditions"},
                partial=True,
            )
        self.assertEqual(self._appraisal_evidence(), before)
        type(self.application).objects.filter(pk=self.application.pk).update(
            created_by_user=self.actor,
            received_by_user=self.actor,
        )

        for code, mutation, write in (
            (
                "credit.appraisal.update",
                {"appraisal_status": "review_pending"},
                lambda: workflow.create_or_update(actor=self.actor, application_id=self.application.pk, payload={"recommendation": "conditions"}, partial=True),
            ),
            (
                "revalidate_appraisal_prerequisites",
                {"appraisal_status": "draft", "prerequisite_provenance": "verified"},
                lambda: workflow.revalidate_prerequisites(actor=self.actor, appraisal_id=note_id, payload={}),
            ),
            (
                "revalidate_appraisal_prerequisites",
                {"appraisal_status": "rejected", "prerequisite_provenance": "legacy_unverified"},
                lambda: workflow.revalidate_prerequisites(actor=self.actor, appraisal_id=note_id, payload={}),
            ),
            (
                "credit.appraisal.submit_review",
                {"appraisal_status": "draft", "prerequisite_provenance": "legacy_unverified"},
                lambda: workflow.submit_for_review(actor=self.actor, appraisal_id=note_id, payload={"remarks": "Denied."}),
            ),
            (
                "credit.appraisal.submit_review",
                {"appraisal_status": "reviewed", "prerequisite_provenance": "verified"},
                lambda: workflow.submit_for_review(actor=self.actor, appraisal_id=note_id, payload={"remarks": "Denied."}),
            ),
        ):
            with self.subTest(code=code, mutation=mutation):
                LoanAppraisalNote.objects.filter(pk=note_id).update(**mutation)
                projected = workflow.get(actor=self.actor, application_id=self.application.pk).snapshot
                denied = action(projected, code)
                before = self._appraisal_evidence()
                with self.assertRaises(CreditModuleInvalidStateError) as raised:
                    write()
                self.assertEqual(str(raised.exception), denied["disabled_reason"])
                self.assertEqual(self._appraisal_evidence(), before)

    @staticmethod
    def _appraisal_evidence():
        note = LoanAppraisalNote.objects.first()
        return (
            None if note is None else str(note.pk),
            None if note is None else note.appraisal_status,
            None if note is None else note.prerequisite_provenance,
            apps.get_model("credit", "RiskAssessment").objects.count(),
            apps.get_model("credit", "AppraisalReviewDecision").objects.count(),
            apps.get_model("applications", "RejectionNote").objects.count(),
            apps.get_model("approvals", "ApprovalCase").objects.count(),
            AuditLog.objects.count(),
            WorkflowEvent.objects.count(),
        )

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

    def test_revalidate_and_submit_object_scope_denials_preserve_the_draft(self):
        created = self._create()
        note_id = created["loan_appraisal_note_id"]
        LoanAppraisalNote.objects.filter(pk=note_id).update(
            prerequisite_provenance="legacy_unverified"
        )
        workflow = AppraisalWorkflow()
        projected = workflow.get(actor=self.actor, application_id=self.application.pk).snapshot
        self.assertTrue(action(projected, "revalidate_appraisal_prerequisites")["enabled"])
        outsider = self._user(
            "appraisal.actions.outsider@sfpcl.example",
            apps.get_model("identity", "Permission").objects.get(
                permission_code="applications.loan_application.read"
            ),
        )
        type(self.application).objects.filter(pk=self.application.pk).update(
            created_by_user=outsider,
            received_by_user=outsider,
        )
        before = self._appraisal_evidence()
        with self.assertRaises(CreditModuleObjectAccessDenied):
            workflow.revalidate_prerequisites(actor=self.actor, appraisal_id=note_id, payload={})
        self.assertEqual(self._appraisal_evidence(), before)
        type(self.application).objects.filter(pk=self.application.pk).update(
            created_by_user=self.actor,
            received_by_user=self.actor,
        )
        workflow.revalidate_prerequisites(actor=self.actor, appraisal_id=note_id, payload={})
        submit_projection = workflow.get(actor=self.actor, application_id=self.application.pk).snapshot
        self.assertTrue(action(submit_projection, "credit.appraisal.submit_review")["enabled"])
        type(self.application).objects.filter(pk=self.application.pk).update(
            created_by_user=outsider,
            received_by_user=outsider,
        )
        before = self._appraisal_evidence()
        with self.assertRaises(CreditModuleObjectAccessDenied):
            workflow.submit_for_review(
                actor=self.actor,
                appraisal_id=note_id,
                payload={"remarks": "Scope denial."},
            )
        self.assertEqual(self._appraisal_evidence(), before)

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

    def test_review_role_denial_matches_the_projected_reason_and_preserves_evidence(self):
        created, _ = self._review_ready()
        delegated = self._user(
            "delegated.matrix.reviewer@sfpcl.example",
            apps.get_model("identity", "Permission").objects.get(
                permission_code="credit.appraisal.review"
            ),
        )
        self.application.received_by_user = delegated
        self.application.save(update_fields=["received_by_user"])
        projected = AppraisalWorkflow().get(
            actor=delegated,
            application_id=self.application.pk,
        ).snapshot
        denied = action(projected, "credit.appraisal.review")
        before = (AuditLog.objects.count(), WorkflowEvent.objects.count())

        with self.assertRaises(CreditModulePermissionDenied) as raised:
            AppraisalWorkflow().review(
                actor=delegated,
                appraisal_id=created["loan_appraisal_note_id"],
                decision="reviewed",
                comments="Delegated role denial.",
                payload_fields={
                    "decision": "reviewed",
                    "review_comments": "Delegated role denial.",
                },
            )

        self.assertFalse(denied["enabled"])
        self.assertEqual(str(raised.exception), denied["disabled_reason"])
        self.assertEqual((AuditLog.objects.count(), WorkflowEvent.objects.count()), before)
        self.assertEqual(apps.get_model("credit", "AppraisalReviewDecision").objects.count(), 0)

    def test_review_object_scope_denial_follows_an_enabled_projection_without_evidence(self):
        created, reviewer = self._review_ready()
        workflow = AppraisalWorkflow()
        projected = workflow.get(actor=reviewer, application_id=self.application.pk).snapshot
        self.assertTrue(action(projected, "credit.appraisal.review")["enabled"])
        outsider = self._user("review.scope.outsider@sfpcl.example")
        type(self.application).objects.filter(pk=self.application.pk).update(
            created_by_user=outsider,
            received_by_user=outsider,
            current_stage="initial_loan_request",
        )
        before = self._review_evidence()
        with self.assertRaises(CreditModuleObjectAccessDenied):
            workflow.review(
                actor=reviewer,
                appraisal_id=created["loan_appraisal_note_id"],
                decision="reviewed",
                comments="Scope denial.",
                payload_fields={"decision": "reviewed", "review_comments": "Scope denial."},
            )
        self.assertEqual(self._review_evidence(), before)

    def test_review_maker_state_provenance_and_rejection_payload_use_the_real_review_action(self):
        created, reviewer = self._review_ready()
        workflow = AppraisalWorkflow()
        self.actor.primary_role = reviewer.primary_role
        self.actor.save(update_fields=["primary_role"])
        maker_snapshot = workflow.get(
            actor=self.actor,
            application_id=self.application.pk,
        ).snapshot
        maker_denied = action(maker_snapshot, "credit.appraisal.review")
        before = self._review_evidence()
        with self.assertRaises(CreditModulePermissionDenied) as raised:
            workflow.review(
                actor=self.actor,
                appraisal_id=created["loan_appraisal_note_id"],
                decision="reviewed",
                comments="Maker denial.",
                payload_fields={"decision": "reviewed", "review_comments": "Maker denial."},
            )
        self.assertEqual(str(raised.exception), maker_denied["disabled_reason"])
        self.assertEqual(self._review_evidence(), before)

        for status, provenance in (("draft", "verified"), ("review_pending", "legacy_unverified")):
            with self.subTest(status=status, provenance=provenance):
                LoanAppraisalNote.objects.filter(pk=created["loan_appraisal_note_id"]).update(
                    appraisal_status=status,
                    prerequisite_provenance=provenance,
                )
                projected = workflow.get(
                    actor=reviewer,
                    application_id=self.application.pk,
                ).snapshot
                denied = action(projected, "credit.appraisal.review")
                before = self._review_evidence()
                with self.assertRaises(CreditModuleInvalidStateError) as raised:
                    workflow.review(
                        actor=reviewer,
                        appraisal_id=created["loan_appraisal_note_id"],
                        decision="returned",
                        comments="Governed denial.",
                        payload_fields={"decision": "returned", "review_comments": "Governed denial."},
                    )
                self.assertEqual(str(raised.exception), denied["disabled_reason"])
                self.assertEqual(self._review_evidence(), before)

        LoanAppraisalNote.objects.filter(pk=created["loan_appraisal_note_id"]).update(
            appraisal_status="review_pending",
            prerequisite_provenance="verified",
        )
        enabled = action(
            workflow.get(actor=reviewer, application_id=self.application.pk).snapshot,
            "credit.appraisal.review",
        )
        self.assertTrue(enabled["enabled"])
        before = self._review_evidence()
        with self.assertRaises(CreditModuleValidationError) as raised:
            workflow.review(
                actor=reviewer,
                appraisal_id=created["loan_appraisal_note_id"],
                decision="rejected",
                comments="Malformed rejection.",
                payload_fields={"decision": "rejected", "review_comments": "Malformed rejection."},
            )
        self.assertEqual(
            raised.exception.field_errors,
            {"reapply_allowed_flag": "This field is required."},
        )
        self.assertEqual(self._review_evidence(), before)

    @staticmethod
    def _review_evidence():
        note = LoanAppraisalNote.objects.get()
        return (
            note.appraisal_status,
            note.prerequisite_provenance,
            note.last_review_decision,
            AuditLog.objects.count(),
            WorkflowEvent.objects.count(),
            apps.get_model("credit", "AppraisalReviewDecision").objects.count(),
            apps.get_model("applications", "RejectionNote").objects.count(),
            apps.get_model("approvals", "ApprovalCase").objects.count(),
        )


class SanctionActionWriteMatrixTests(TestCase):
    EXECUTED_CASES = tuple(
        ("credit.appraisal.submit_sanction", variant)
        for variant in ("enabled", "permission", "role", "object_scope", "state", "frozen_provenance", "immutable_review", "stale_state")
    )
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

    def test_role_permission_provenance_and_immutable_history_denials_match_the_write(self):
        module = SanctionHandoffModule()
        permissions = {
            "applications.loan_application.read",
            "credit.appraisal.submit_sanction",
        }
        non_manager = self._user(
            "delegated_submitter_matrix",
            "Delegated Submitter Matrix",
            self.submit_permission,
        )
        self.application.received_by_user = non_manager
        self.application.save(update_fields=["received_by_user"])
        role_projection = AppraisalWorkflow().get(
            actor=non_manager,
            application_id=self.application.pk,
            actor_permissions=permissions,
        ).snapshot
        role_denied = action(role_projection, "credit.appraisal.submit_sanction")
        before = self._matrix_evidence()
        with self.assertRaises(CreditModulePermissionDenied) as raised:
            module.submit_reviewed_appraisal(
                actor=non_manager,
                application_id=self.application.pk,
                payload={"remarks": "Role denial."},
                actor_permissions=permissions,
            )
        self.assertEqual(str(raised.exception), role_denied["disabled_reason"])
        self.assertEqual(self._matrix_evidence(), before)

        self.application.received_by_user = self.reviewer
        self.application.save(update_fields=["received_by_user"])
        for mutation, expected_fragment in (
            ("provenance", "verified prerequisite snapshots"),
            ("history", "latest immutable review decision"),
        ):
            with self.subTest(mutation=mutation):
                self.note.refresh_from_db()
                self.note.prerequisite_provenance = "verified"
                self.note.save(update_fields=["prerequisite_provenance"])
                latest = self.note.review_decisions.order_by("decided_at", "pk").last()
                original_comments = latest.review_comments
                if mutation == "provenance":
                    self.note.prerequisite_provenance = "legacy_unverified"
                    self.note.save(update_fields=["prerequisite_provenance"])
                else:
                    type(latest).objects.filter(pk=latest.pk).update(
                        review_comments=f"{original_comments} tampered"
                    )
                projected = AppraisalWorkflow().get(
                    actor=self.reviewer,
                    application_id=self.application.pk,
                ).snapshot
                denied = action(projected, "credit.appraisal.submit_sanction")
                self.assertIn(expected_fragment, denied["disabled_reason"])
                before = self._matrix_evidence()
                with self.assertRaises(CreditModuleInvalidStateError) as raised:
                    module.submit_reviewed_appraisal(
                        actor=self.reviewer,
                        application_id=self.application.pk,
                        payload={"remarks": "Governed denial."},
                    )
                self.assertEqual(str(raised.exception), denied["disabled_reason"])
                self.assertEqual(self._matrix_evidence(), before)
                if mutation == "history":
                    type(latest).objects.filter(pk=latest.pk).update(
                        review_comments=original_comments
                    )

    def test_permission_object_scope_and_stale_state_invoke_the_public_sanction_write(self):
        workflow = AppraisalWorkflow()
        module = SanctionHandoffModule()
        review_only = {
            "applications.loan_application.read",
            "credit.appraisal.review",
        }
        projected = workflow.get(
            actor=self.reviewer,
            application_id=self.application.pk,
            actor_permissions=review_only,
        ).snapshot
        permission_denied = action(projected, "credit.appraisal.submit_sanction")
        before = self._matrix_evidence()
        with self.assertRaises(CreditModulePermissionDenied) as raised:
            module.submit_reviewed_appraisal(
                actor=self.reviewer,
                application_id=self.application.pk,
                payload={"remarks": "Permission denial."},
                actor_permissions=review_only,
            )
        self.assertEqual(str(raised.exception), permission_denied["disabled_reason"])
        self.assertEqual(self._matrix_evidence(), before)

        enabled = action(
            workflow.get(actor=self.reviewer, application_id=self.application.pk).snapshot,
            "credit.appraisal.submit_sanction",
        )
        self.assertTrue(enabled["enabled"])
        outsider = self._user("credit_manager_outsider", "Credit Manager Outsider")
        type(self.application).objects.filter(pk=self.application.pk).update(
            created_by_user=outsider,
            received_by_user=outsider,
            current_stage="initial_loan_request",
        )
        before = self._matrix_evidence()
        with self.assertRaises(CreditModuleObjectAccessDenied):
            module.submit_reviewed_appraisal(
                actor=self.reviewer,
                application_id=self.application.pk,
                payload={"remarks": "Scope denial."},
            )
        self.assertEqual(self._matrix_evidence(), before)
        type(self.application).objects.filter(pk=self.application.pk).update(
            created_by_user=self.reviewer,
            received_by_user=self.reviewer,
            current_stage="credit_assessment",
        )

        stale_enabled = action(
            workflow.get(actor=self.reviewer, application_id=self.application.pk).snapshot,
            "credit.appraisal.submit_sanction",
        )
        self.assertTrue(stale_enabled["enabled"])
        LoanAppraisalNote.objects.filter(pk=self.note.pk).update(appraisal_status="review_pending")
        before = self._matrix_evidence()
        with self.assertRaisesMessage(CreditModuleInvalidStateError, "Only a reviewed appraisal note"):
            module.submit_reviewed_appraisal(
                actor=self.reviewer,
                application_id=self.application.pk,
                payload={"remarks": "Stale denial."},
            )
        self.assertEqual(self._matrix_evidence(), before)

    @staticmethod
    def _matrix_evidence():
        return (
            apps.get_model("applications", "LoanApplication").objects.values_list(
                "application_status", flat=True
            ).get(),
            apps.get_model("credit", "LoanAppraisalNote").objects.values_list(
                "appraisal_status", flat=True
            ).get(),
            AuditLog.objects.count(),
            WorkflowEvent.objects.count(),
            apps.get_model("credit", "AppraisalReviewDecision").objects.count(),
            apps.get_model("applications", "RejectionNote").objects.count(),
            apps.get_model("approvals", "ApprovalCase").objects.count(),
        )
