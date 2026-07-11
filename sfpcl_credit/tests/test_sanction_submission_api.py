from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import ast
from importlib.util import resolve_name
from pathlib import Path
from threading import Event
from unittest import skipUnless
from unittest.mock import patch

from django.apps import apps
from django.db import close_old_connections, connection, connections
from django.test import Client, TestCase, TransactionTestCase
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication, RejectionNote
from sfpcl_credit.credit.models import (
    AppraisalReviewDecision,
    LoanAppraisalNote,
    RiskAssessment,
)
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import Member
from sfpcl_credit.tests.api_contracts import assert_success_envelope
from sfpcl_credit.workflows.models import WorkflowEvent


PUBLIC_CREDIT_HANDOFF_MODULES = frozenset(
    {"sfpcl_credit.credit.modules.appraisal_workflow"}
)


def resolved_import_references(source, *, package=None):
    """Return canonical package-aware references for every import in source."""
    references = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            references.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                if package is None:
                    raise ValueError("Relative imports require package context")
                imported_from = resolve_name(
                    f"{'.' * node.level}{node.module or ''}", package
                )
            else:
                imported_from = node.module
            if imported_from is None:
                continue
            if any(alias.name == "*" for alias in node.names):
                references.add(imported_from)
            references.update(
                f"{imported_from}.{alias.name}"
                for alias in node.names
                if alias.name != "*"
            )
    return references


def business_app_dependency_violations(*, owner, references):
    if owner == "credit":
        return sorted(
            reference
            for reference in references
            if reference == "sfpcl_credit.approvals"
            or reference.startswith("sfpcl_credit.approvals.")
        )
    if owner == "approvals":
        credit_references = {
            reference
            for reference in references
            if reference == "sfpcl_credit.credit"
            or reference.startswith("sfpcl_credit.credit.")
        }
        return sorted(
            reference
            for reference in credit_references
            if not any(
                reference == public_module
                or reference.startswith(f"{public_module}.")
                for public_module in PUBLIC_CREDIT_HANDOFF_MODULES
            )
        )
    raise ValueError(f"Unsupported business app owner: {owner}")


class SanctionSubmissionApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.preparer = self._user("deputy_manager_finance", "Appraisal Preparer")
        self.submit_permission = self._permission(
            "credit.appraisal.submit_sanction",
            "Submit to Sanction Committee",
        )
        self.reviewer = self._user(
            "credit_manager",
            "Credit Manager",
            self.submit_permission,
        )
        self.member = Member.objects.create(
            member_number="MEM-SANCTION-001",
            member_type="individual_farmer",
            legal_name="Sanction Test Member",
            display_name="Sanction Test Member",
            membership_status="active",
            folio_number="FOL-SANCTION-001",
            kyc_status="verified",
            default_status="no_default",
        )
        self.application = LoanApplication.objects.create(
            application_reference_number="LO00000699",
            member=self.member,
            borrower_type=self.member.member_type,
            received_by_user=self.preparer,
            required_loan_amount="400000.00",
            requested_tenure_months=12,
            declared_purpose="Crop production",
            purpose_category="crop_production",
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            application_status=LoanApplication.STATUS_REFERENCE_GENERATED,
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
            terms_acceptance_flag=True,
            created_by_user=self.preparer,
        )
        self.risk = RiskAssessment.objects.create(
            loan_application=self.application,
            market_risk_rating="medium",
            operational_risk_rating="low",
            borrower_risk_rating="low",
            overall_risk_rating="low",
            risk_mitigation_notes="Stored only on the risk assessment.",
            assessed_by_user=self.preparer,
        )
        self.reviewed_at = timezone.now() - timedelta(minutes=5)
        self.note = LoanAppraisalNote.objects.create(
            loan_application=self.application,
            prepared_by_user=self.preparer,
            reviewed_by_user=self.reviewer,
            prepared_at=timezone.now() - timedelta(hours=2),
            reviewed_at=self.reviewed_at,
            review_comments="Reviewed; comments must stay out of generic evidence.",
            last_review_decision="reviewed",
            tat_due_at=timezone.now() + timedelta(days=1),
            tat_status=LoanAppraisalNote.TAT_WITHIN,
            eligibility_assessment_id_snapshot="10000000-0000-0000-0000-000000000001",
            loan_limit_assessment_id_snapshot="20000000-0000-0000-0000-000000000002",
            eligibility_snapshot_json={
                "eligibility_assessment_id": "10000000-0000-0000-0000-000000000001",
                "loan_application_id": str(self.application.pk),
                "overall_result": "eligible",
            },
            loan_limit_snapshot_json={
                "loan_limit_assessment_id": "20000000-0000-0000-0000-000000000002",
                "loan_application_id": str(self.application.pk),
                "final_eligible_loan_amount": "500000.00",
                "exception_required_flag": False,
            },
            prerequisite_provenance="verified",
            borrower_summary="Stored borrower summary.",
            eligibility_summary="Stored eligibility summary.",
            loan_limit_summary="Stored loan-limit summary.",
            recommended_amount="400000.00",
            recommended_tenure_months=12,
            recommended_interest_type="floating",
            recommended_security_summary="Stored security recommendation.",
            repayment_capacity_notes="Stored repayment capacity.",
            submission_remarks="Prepared for independent review.",
            risk_assessment=self.risk,
            recommendation="approve",
            appraisal_status=LoanAppraisalNote.STATUS_REVIEWED,
        )
        self.history = AppraisalReviewDecision.objects.create(
            loan_appraisal_note=self.note,
            decision="reviewed",
            review_comments=self.note.review_comments,
            reviewer_user=self.reviewer,
            decided_at=self.reviewed_at,
            from_state=LoanAppraisalNote.STATUS_REVIEW_PENDING,
            to_state=LoanAppraisalNote.STATUS_REVIEWED,
        )

    def test_reviewed_appraisal_creates_one_pending_case_and_metadata_only_evidence(self):
        frozen_note = self._note_facts()
        frozen_risk = RiskAssessment.objects.filter(pk=self.risk.pk).values().get()
        frozen_history = list(
            AppraisalReviewDecision.objects.filter(loan_appraisal_note=self.note).values()
        )

        response = self._submit(
            {"remarks": "Reviewed package is ready for the committee."},
            request_id="submit-sanction-006g",
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        data = body["data"]
        self.assertEqual(data["loan_application_id"], str(self.application.pk))
        self.assertEqual(data["loan_appraisal_note_id"], str(self.note.pk))
        self.assertEqual(data["submission_status"], "pending")
        self.assertFalse(data["exception_required_flag"])
        self.assertEqual(
            data["submitted_by"],
            {"user_id": str(self.reviewer.pk), "full_name": self.reviewer.full_name},
        )
        self.assertIsNotNone(data["submitted_at"])
        self.assertEqual(data["application_status"], "submitted_to_sanction_committee")
        self.assertEqual(data["appraisal_status"], "submitted_to_sanction_committee")
        self.assertEqual(data["appraisal_review_decision_id"], str(self.history.pk))
        self.assertIsNotNone(data["workflow_event_id"])
        self.assertEqual(data["available_actions"], [])

        approval_case_model = apps.get_model("approvals", "ApprovalCase")
        case = approval_case_model.objects.get()
        self.assertEqual(data["approval_case_id"], str(case.pk))
        self.assertEqual(case.loan_application_id, self.application.pk)
        self.assertEqual(case.loan_appraisal_note_id, self.note.pk)
        self.assertEqual(case.current_status, "pending")
        self.assertEqual(case.submission_remarks, "Reviewed package is ready for the committee.")

        self.note.refresh_from_db()
        self.application.refresh_from_db()
        self.assertEqual(self.note.appraisal_status, "submitted_to_sanction_committee")
        self.assertEqual(
            self.application.application_status,
            "submitted_to_sanction_committee",
        )
        self.assertEqual(self._note_facts(exclude_status=True), frozen_note[1:])
        self.assertEqual(
            RiskAssessment.objects.filter(pk=self.risk.pk).values().get(),
            frozen_risk,
        )
        self.assertEqual(
            list(AppraisalReviewDecision.objects.filter(loan_appraisal_note=self.note).values()),
            frozen_history,
        )

        audit = AuditLog.objects.get(action="appraisal.submitted_to_sanction")
        self.assertEqual(audit.new_value_json["approval_case_id"], str(case.pk))
        self.assertEqual(
            audit.new_value_json["appraisal_review_decision_id"],
            str(self.history.pk),
        )
        self.assertEqual(audit.new_value_json["request_id"], "submit-sanction-006g")
        workflow = WorkflowEvent.objects.get(workflow_name="sanction_submission")
        self.assertEqual(workflow.entity_id, self.application.pk)
        self.assertEqual(case.workflow_event_id, workflow.pk)
        self.assertEqual(data["workflow_event_id"], str(case.workflow_event_id))
        evidence_text = f"{audit.old_value_json} {audit.new_value_json} {workflow.trigger_reason}"
        for secret in (
            self.note.borrower_summary,
            self.note.review_comments,
            self.risk.risk_mitigation_notes,
            case.submission_remarks,
        ):
            self.assertNotIn(secret, evidence_text)

        reloaded = self._get_case()
        self.assertEqual(reloaded.status_code, 200)
        self.assertEqual(reloaded.json()["data"], data)
        self.assertNotIn("submission_remarks", reloaded.json()["data"])

    def test_pending_case_read_is_scoped_and_missing_case_is_not_found(self):
        missing = self._get_case()
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(missing.json()["error"]["code"], "NOT_FOUND")

        self.assertEqual(self._submit({"remarks": "Ready."}).status_code, 200)
        LoanApplication.objects.filter(pk=self.application.pk).update(
            current_stage=LoanApplication.STAGE_INITIAL
        )
        denied = self._get_case()
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(denied.json()["error"]["code"], "OBJECT_ACCESS_DENIED")

    def test_malformed_and_non_object_json_are_validation_errors_without_writes(self):
        token = self._login(self.reviewer)
        url = f"/api/v1/loan-applications/{self.application.pk}/submit-to-sanction-committee/"
        for raw in ('{"remarks":', '["remarks"]'):
            with self.subTest(raw=raw):
                response = self.client.post(
                    url,
                    data=raw,
                    content_type="application/json",
                    headers={"Authorization": f"Bearer {token}"},
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json()["error"]["code"], "VALIDATION_ERROR")
                self._assert_no_submission_writes()

    def test_business_app_dependency_direction_is_approvals_to_credit_only(self):
        package_root = Path(__file__).resolve().parents[1]

        def imports_under(path):
            imported = []
            for module_path in path.rglob("*.py"):
                if "migrations" in module_path.parts or "tests" in module_path.parts:
                    continue
                relative_module = module_path.relative_to(package_root).with_suffix("")
                package_parts = relative_module.parts[:-1]
                package = ".".join((package_root.name, *package_parts))
                imported.extend(
                    (module_path, reference)
                    for reference in resolved_import_references(
                        module_path.read_text(), package=package
                    )
                )
            return imported

        credit_imports = imports_under(package_root / "credit")
        approvals_imports = imports_under(package_root / "approvals")
        self.assertEqual(
            [
                (path, name)
                for path, name in credit_imports
                if business_app_dependency_violations(
                    owner="credit", references={name}
                )
            ],
            [],
        )
        self.assertEqual(
            [
                (path, name)
                for path, name in approvals_imports
                if business_app_dependency_violations(
                    owner="approvals", references={name}
                )
            ],
            [],
        )
        public_edges = {
            public_module
            for _, name in approvals_imports
            for public_module in PUBLIC_CREDIT_HANDOFF_MODULES
            if name == public_module or name.startswith(f"{public_module}.")
        }
        self.assertEqual(public_edges, PUBLIC_CREDIT_HANDOFF_MODULES)

    def test_dependency_import_collector_resolves_package_and_alias_forms(self):
        source = """
import sfpcl_credit.approvals.modules.sanction_handoff as handoff
from sfpcl_credit import approvals as approvals_package
from sfpcl_credit.credit import modules as credit_modules
from sfpcl_credit.credit.modules import common as private_common
from sfpcl_credit.credit.modules.appraisal_workflow import AppraisalWorkflow as Workflow
"""
        imported = resolved_import_references(source)

        self.assertIn("sfpcl_credit.approvals", imported)
        self.assertIn("sfpcl_credit.credit.modules", imported)
        self.assertIn("sfpcl_credit.credit.modules.common", imported)
        self.assertIn(
            "sfpcl_credit.credit.modules.appraisal_workflow.AppraisalWorkflow",
            imported,
        )

    def test_dependency_import_collector_resolves_relative_syntax_matrix(self):
        cases = (
            (
                "from ..approvals import modules as approval_modules",
                "sfpcl_credit.credit",
                "sfpcl_credit.approvals.modules",
            ),
            (
                "from ... import approvals as approval_package",
                "sfpcl_credit.credit.modules",
                "sfpcl_credit.approvals",
            ),
            (
                "from . import models as concrete_models",
                "sfpcl_credit.credit",
                "sfpcl_credit.credit.models",
            ),
            (
                "from ..credit.modules import common as private_common",
                "sfpcl_credit.approvals",
                "sfpcl_credit.credit.modules.common",
            ),
            (
                "from ..credit.modules.appraisal_workflow import *",
                "sfpcl_credit.approvals",
                "sfpcl_credit.credit.modules.appraisal_workflow",
            ),
        )
        for source, package, expected in cases:
            with self.subTest(source=source, package=package):
                self.assertIn(
                    expected,
                    resolved_import_references(source, package=package),
                )

    def test_dependency_guard_classifies_relative_imports_like_absolute_imports(self):
        cases = (
            ("credit", "sfpcl_credit.credit", "from .. import approvals", True),
            (
                "credit",
                "sfpcl_credit.credit.modules",
                "from ...approvals import modules as approval_modules",
                True,
            ),
            (
                "approvals",
                "sfpcl_credit.approvals.modules",
                "from ...credit import models as concrete_models",
                True,
            ),
            (
                "approvals",
                "sfpcl_credit.approvals",
                "from ..credit.modules import common as private_common",
                True,
            ),
            (
                "approvals",
                "sfpcl_credit.approvals.modules",
                "from ...credit.modules.appraisal_workflow import AppraisalWorkflow as Workflow",
                False,
            ),
            (
                "credit",
                "sfpcl_credit.credit.modules",
                "from . import eligibility",
                False,
            ),
        )
        for owner, package, source, forbidden in cases:
            with self.subTest(owner=owner, source=source):
                violations = business_app_dependency_violations(
                    owner=owner,
                    references=resolved_import_references(source, package=package),
                )
                self.assertEqual(bool(violations), forbidden)

    def test_dependency_guard_rejects_forbidden_forms_and_allows_public_handoff(self):
        forbidden_credit_sources = (
            "import sfpcl_credit.approvals",
            "import sfpcl_credit.approvals.modules as approval_modules",
            "from sfpcl_credit import approvals",
            "from sfpcl_credit import approvals as approval_package",
        )
        for source in forbidden_credit_sources:
            with self.subTest(owner="credit", source=source):
                self.assertTrue(
                    business_app_dependency_violations(
                        owner="credit",
                        references=resolved_import_references(source),
                    )
                )

        forbidden_approvals_sources = (
            "import sfpcl_credit.credit.modules.common",
            "from sfpcl_credit.credit.modules import common",
            "from sfpcl_credit.credit.modules import common as credit_common",
            "from sfpcl_credit.credit import models",
            "from sfpcl_credit import credit",
        )
        for source in forbidden_approvals_sources:
            with self.subTest(owner="approvals", source=source):
                self.assertTrue(
                    business_app_dependency_violations(
                        owner="approvals",
                        references=resolved_import_references(source),
                    )
                )

        public_source = (
            "from sfpcl_credit.credit.modules.appraisal_workflow "
            "import AppraisalWorkflow as Workflow"
        )
        public_references = resolved_import_references(public_source)
        self.assertFalse(
            business_app_dependency_violations(
                owner="approvals", references=public_references
            )
        )
        self.assertIn(
            "sfpcl_credit.credit.modules.appraisal_workflow.AppraisalWorkflow",
            public_references,
        )

    def test_payload_permission_role_and_object_scope_are_independent(self):
        for payload, field in (
            ({}, "remarks"),
            ({"remarks": "   "}, "remarks"),
            ({"remarks": "Ready.", "committee_id": "not-owned-here"}, "committee_id"),
        ):
            with self.subTest(field=field):
                response = self._submit(payload)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json()["error"]["code"], "VALIDATION_ERROR")
                self.assertIn(field, response.json()["error"]["field_errors"])

        non_manager = self._user(
            "delegated_submitter",
            "Delegated Submitter",
            self.submit_permission,
        )
        role_denied = self._submit({"remarks": "Ready."}, actor=non_manager)
        self.assertEqual(role_denied.status_code, 403)
        self.assertEqual(role_denied.json()["error"]["code"], "FORBIDDEN")

        permission_link = RolePermission.objects.get(
            role=self.reviewer.primary_role,
            permission=self.submit_permission,
        )
        permission_link.delete()
        missing_permission_manager = self._user("credit_manager", "Second Credit Manager")
        permission_denied = self._submit(
            {"remarks": "Ready."}, actor=missing_permission_manager
        )
        self.assertEqual(permission_denied.status_code, 403)
        self.assertEqual(permission_denied.json()["error"]["code"], "FORBIDDEN")
        RolePermission.objects.create(
            role=self.reviewer.primary_role,
            permission=self.submit_permission,
        )

        LoanApplication.objects.filter(pk=self.application.pk).update(
            current_stage=LoanApplication.STAGE_INITIAL
        )
        scope_denied = self._submit({"remarks": "Ready."})
        self.assertEqual(scope_denied.status_code, 403)
        self.assertEqual(scope_denied.json()["error"]["code"], "OBJECT_ACCESS_DENIED")
        self._assert_no_submission_writes()

    def test_invalid_or_inconsistent_appraisal_states_and_repeat_have_no_side_effects(self):
        invalid_setups = (
            ("draft", "returned", None),
            ("review_pending", "", None),
            ("rejected", "rejected", None),
            ("reviewed", "reviewed", "history_comments"),
            ("reviewed", "reviewed", "legacy_unverified"),
        )
        for status, decision, mutation in invalid_setups:
            with self.subTest(status=status, mutation=mutation):
                self.note.appraisal_status = status
                self.note.last_review_decision = decision
                self.note.prerequisite_provenance = (
                    mutation if mutation == "legacy_unverified" else "verified"
                )
                self.note.save(
                    update_fields=(
                        "appraisal_status",
                        "last_review_decision",
                        "prerequisite_provenance",
                    )
                )
                if mutation == "history_comments":
                    AppraisalReviewDecision.objects.filter(pk=self.history.pk).update(
                        review_comments="Inconsistent history projection."
                    )
                response = self._submit({"remarks": "Ready."})
                self.assertEqual(response.status_code, 409)
                self.assertEqual(
                    response.json()["error"]["code"], "INVALID_STATE_TRANSITION"
                )
                self._assert_no_submission_writes()
                AppraisalReviewDecision.objects.filter(pk=self.history.pk).update(
                    review_comments=self.note.review_comments
                )

        self.note.appraisal_status = LoanAppraisalNote.STATUS_REVIEWED
        self.note.last_review_decision = "reviewed"
        self.note.prerequisite_provenance = "verified"
        self.note.save(
            update_fields=(
                "appraisal_status",
                "last_review_decision",
                "prerequisite_provenance",
            )
        )
        first = self._submit({"remarks": "Ready once."})
        self.assertEqual(first.status_code, 200)
        repeated = self._submit({"remarks": "Do not duplicate."})
        self.assertEqual(repeated.status_code, 409)
        approval_case_model = apps.get_model("approvals", "ApprovalCase")
        self.assertEqual(approval_case_model.objects.count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="appraisal.submitted_to_sanction").count(), 1)
        self.assertEqual(WorkflowEvent.objects.filter(workflow_name="sanction_submission").count(), 1)

    def test_missing_appraisal_is_an_invalid_transition_without_evidence(self):
        AppraisalReviewDecision.objects.filter(loan_appraisal_note=self.note).delete()
        self.note.delete()

        response = self._submit({"remarks": "No appraisal exists."})

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["error"]["code"], "INVALID_STATE_TRANSITION")
        self._assert_no_submission_writes()

    def test_exception_flag_is_frozen_and_audit_failure_rolls_back_every_write(self):
        loan_limit_snapshot = deepcopy(self.note.loan_limit_snapshot_json)
        loan_limit_snapshot["exception_required_flag"] = True
        self.note.loan_limit_snapshot_json = loan_limit_snapshot
        self.note.save(update_fields=["loan_limit_snapshot_json"])

        approval_case_model = apps.get_model("approvals", "ApprovalCase")
        with patch.object(
            approval_case_model.objects,
            "create",
            side_effect=RuntimeError("case unavailable"),
        ):
            with self.assertRaisesMessage(RuntimeError, "case unavailable"):
                self._submit({"remarks": "Exception route required later."})
        self.note.refresh_from_db()
        self.application.refresh_from_db()
        self.assertEqual(self.note.appraisal_status, LoanAppraisalNote.STATUS_REVIEWED)
        self.assertEqual(
            self.application.application_status,
            LoanApplication.STATUS_REFERENCE_GENERATED,
        )
        self._assert_no_submission_writes()

        with patch.object(
            AuditLog.objects,
            "create",
            side_effect=RuntimeError("audit unavailable"),
        ):
            with self.assertRaisesMessage(RuntimeError, "audit unavailable"):
                self._submit({"remarks": "Exception route required later."})

        self.note.refresh_from_db()
        self.application.refresh_from_db()
        self.assertEqual(self.note.appraisal_status, LoanAppraisalNote.STATUS_REVIEWED)
        self.assertEqual(
            self.application.application_status,
            LoanApplication.STATUS_REFERENCE_GENERATED,
        )
        self._assert_no_submission_writes()

        with patch(
            "sfpcl_credit.approvals.modules.sanction_handoff.record_workflow_event",
            side_effect=RuntimeError("workflow unavailable"),
        ):
            with self.assertRaisesMessage(RuntimeError, "workflow unavailable"):
                self._submit({"remarks": "Exception route required later."})
        self.note.refresh_from_db()
        self.application.refresh_from_db()
        self.assertEqual(self.note.appraisal_status, LoanAppraisalNote.STATUS_REVIEWED)
        self.assertEqual(
            self.application.application_status,
            LoanApplication.STATUS_REFERENCE_GENERATED,
        )
        self._assert_no_submission_writes()

        response = self._submit({"remarks": "Exception route required later."})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["data"]["exception_required_flag"])
        case = apps.get_model("approvals", "ApprovalCase").objects.get()
        self.assertTrue(case.exception_required_flag)

    def test_rejected_appraisal_preserves_unsent_rejection_note_byte_for_byte(self):
        rejection_note = RejectionNote.objects.create(
            loan_application=self.application,
            rejection_stage="credit_assessment",
            rejection_reason_category="eligibility",
            detailed_reason="Stored rejection reason must remain unchanged.",
            reapply_allowed_flag=True,
            communication_mode="email",
            note_status="draft",
            prepared_by_user=self.reviewer,
        )
        before = RejectionNote.objects.filter(pk=rejection_note.pk).values().get()
        self.note.appraisal_status = LoanAppraisalNote.STATUS_REJECTED
        self.note.last_review_decision = "rejected"
        self.note.save(update_fields=["appraisal_status", "last_review_decision"])

        response = self._submit({"remarks": "Must be blocked."})

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            RejectionNote.objects.filter(pk=rejection_note.pk).values().get(), before
        )
        self._assert_no_submission_writes()

    def _submit(self, payload, *, actor=None, request_id="submit-sanction-test"):
        actor = actor or self.reviewer
        token = self._login(actor)
        return self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/submit-to-sanction-committee/",
            data=payload,
            content_type="application/json",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Request-ID": request_id,
            },
        )

    def _get_case(self):
        token = self._login(self.reviewer)
        return self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/sanction-case/",
            headers={"Authorization": f"Bearer {token}"},
        )

    def _login(self, actor):
        login = self.client.post(
            "/api/v1/auth/login/",
            data={"email": actor.email, "password": "SanctionPass123!"},
            content_type="application/json",
        )
        self.assertEqual(login.status_code, 200)
        return login.json()["data"]["access_token"]

    def _assert_no_submission_writes(self):
        try:
            approval_case_model = apps.get_model("approvals", "ApprovalCase")
        except LookupError:
            approval_case_model = None
        if approval_case_model is not None:
            self.assertEqual(approval_case_model.objects.count(), 0)
        self.assertFalse(
            AuditLog.objects.filter(action="appraisal.submitted_to_sanction").exists()
        )
        self.assertFalse(
            WorkflowEvent.objects.filter(workflow_name="sanction_submission").exists()
        )

    def _note_facts(self, *, exclude_status=False):
        values = (
            self.note.appraisal_status,
            str(self.note.eligibility_assessment_id_snapshot),
            str(self.note.loan_limit_assessment_id_snapshot),
            deepcopy(self.note.eligibility_snapshot_json),
            deepcopy(self.note.loan_limit_snapshot_json),
            str(self.note.recommended_amount),
            self.note.recommended_tenure_months,
            self.note.recommended_interest_type,
            self.note.recommended_security_summary,
            self.note.repayment_capacity_notes,
            self.note.borrower_summary,
            self.note.eligibility_summary,
            self.note.loan_limit_summary,
            self.note.risk_assessment_id,
            self.note.recommendation,
            self.note.tat_due_at,
            self.note.reviewed_by_user_id,
            self.note.reviewed_at,
            self.note.review_comments,
        )
        return values[1:] if exclude_status else values

    @staticmethod
    def _permission(code, name):
        return Permission.objects.create(
            permission_code=code,
            permission_name=name,
            module_name=code.split(".")[0],
            risk_level="high",
        )

    @staticmethod
    def _user(role_code, full_name, *permissions):
        role = Role.objects.filter(role_code=role_code).first()
        if role is None:
            role = Role.objects.create(
                role_code=role_code,
                role_name=full_name,
                is_system_role=True,
                status="active",
            )
        for permission in permissions:
            RolePermission.objects.get_or_create(role=role, permission=permission)
        user = User.objects.create(
            full_name=full_name,
            email=f"{role_code}-{User.objects.count()}@sfpcl.example",
            status="active",
            primary_role=role,
        )
        user.set_password("SanctionPass123!")
        user.save()
        return user


@skipUnless(
    connection.vendor == "postgresql",
    "Authoritative sanction-submission concurrency proof requires PostgreSQL.",
)
class SanctionSubmissionConcurrencyTests(TransactionTestCase):
    setUp = SanctionSubmissionApiTests.setUp
    _permission = staticmethod(SanctionSubmissionApiTests._permission)
    _user = staticmethod(SanctionSubmissionApiTests._user)

    def test_duplicate_submissions_serialize_to_one_case_and_one_evidence_set(self):
        from sfpcl_credit.approvals.models import ApprovalCase
        from sfpcl_credit.approvals.modules.sanction_handoff import SanctionHandoffModule
        from sfpcl_credit.credit.modules.appraisal_workflow import CreditModuleInvalidStateError

        history_before = list(
            AppraisalReviewDecision.objects.filter(loan_appraisal_note=self.note).values()
        )
        winner_reached_case_create = Event()
        loser_started = Event()
        release_winner = Event()
        original_create = ApprovalCase.objects.create

        def coordinated_create(**kwargs):
            winner_reached_case_create.set()
            if not release_winner.wait(timeout=10):
                raise AssertionError("Timed out waiting to release sanction submission.")
            return original_create(**kwargs)

        def submit(request_id, started_event=None):
            close_old_connections()
            try:
                if started_event is not None:
                    started_event.set()
                actor = User.objects.get(pk=self.reviewer.pk)
                return SanctionHandoffModule().submit_reviewed_appraisal(
                    actor=actor,
                    application_id=self.application.pk,
                    payload={"remarks": f"Submission {request_id}."},
                    request_meta={"request_id": request_id},
                ).snapshot
            finally:
                connections["default"].close()

        with patch.object(
            ApprovalCase.objects,
            "create",
            side_effect=coordinated_create,
        ):
            with ThreadPoolExecutor(max_workers=2) as executor:
                winner_future = executor.submit(submit, "sanction-race-winner")
                self.assertTrue(winner_reached_case_create.wait(timeout=10))
                loser_future = executor.submit(
                    submit,
                    "sanction-race-loser",
                    loser_started,
                )
                self.assertTrue(loser_started.wait(timeout=10))
                try:
                    self.assertFalse(
                        loser_future.done(),
                        "The competing submission bypassed the application lock.",
                    )
                finally:
                    release_winner.set()
                winner = winner_future.result(timeout=10)
                with self.assertRaises(CreditModuleInvalidStateError):
                    loser_future.result(timeout=10)

        self.note.refresh_from_db()
        self.application.refresh_from_db()
        case = ApprovalCase.objects.get()
        self.assertEqual(winner["approval_case_id"], str(case.pk))
        self.assertEqual(self.note.appraisal_status, "submitted_to_sanction_committee")
        self.assertEqual(
            self.application.application_status,
            "submitted_to_sanction_committee",
        )
        self.assertEqual(
            list(AppraisalReviewDecision.objects.filter(loan_appraisal_note=self.note).values()),
            history_before,
        )
        self.assertEqual(
            AuditLog.objects.filter(action="appraisal.submitted_to_sanction").count(),
            1,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="sanction_submission").count(),
            1,
        )
        winning_event = WorkflowEvent.objects.get(workflow_name="sanction_submission")
        self.assertEqual(winner["workflow_event_id"], str(winning_event.pk))
        self.assertEqual(case.workflow_event_id, winning_event.pk)
        self.assertEqual(winning_event.from_state, "reviewed")
        self.assertEqual(winning_event.to_state, "submitted_to_sanction_committee")
        self.assertEqual(
            winning_event.trigger_reason,
            f"Appraisal {self.note.pk} submitted as approval case {case.pk} "
            f"from review decision {self.history.pk}.",
        )
        self.assertFalse(
            AuditLog.objects.filter(
                action="appraisal.submitted_to_sanction",
                new_value_json__request_id="sanction-race-loser",
            ).exists()
        )
