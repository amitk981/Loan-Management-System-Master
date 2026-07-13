from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from decimal import Decimal
import ast
from importlib.util import resolve_name
from pathlib import Path
from threading import Event
from unittest import skipUnless
from unittest.mock import patch

from django.apps import apps
from django.db import close_old_connections, connection, connections
from django.test import Client, RequestFactory, TestCase, TransactionTestCase
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication, RejectionNote
from sfpcl_credit.approvals.models import ApprovalMatrixRule, SanctionCommittee
from sfpcl_credit.approvals.modules import approval_matrix_configuration
from sfpcl_credit.approvals.modules import sanction_handoff as sanction_handoff_module
from sfpcl_credit.approvals.modules.approval_matrix import resolve_approval_matrix
from sfpcl_credit.approvals.modules.sanction_committee import resolve_sanction_committee
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

    def test_existing_case_is_enriched_from_authoritative_appraisal_facts(self):
        ApprovalMatrixRule.objects.all().delete()
        SanctionCommittee.objects.all().delete()
        self.note.recommended_amount = "500000.00"
        self.note.save(update_fields=["recommended_amount"])
        create_permission = self._permission(
            "approvals.case.create", "Create approval case"
        )
        RolePermission.objects.create(
            role=self.reviewer.primary_role, permission=create_permission
        )
        cfo = self._user("case_cfo", "Case CFO")
        cfo.approval_authority_type = "cfo"
        cfo.save(update_fields=["approval_authority_type"])
        director_1 = self._user("case_director_1", "Case Director 1")
        director_1.approval_authority_type = "director"
        director_1.save(update_fields=["approval_authority_type"])
        director_2 = self._user("case_director_2", "Case Director 2")
        director_2.approval_authority_type = "director"
        director_2.save(update_fields=["approval_authority_type"])
        decision_date = timezone.localdate(self.history.decided_at)
        rule = ApprovalMatrixRule.objects.create(
            decision_type="loan_sanction",
            amount_min="0.00",
            amount_max="500000.00",
            required_approver_roles_json=["cfo", "director"],
            required_director_count=1,
            joint_approval_required_flag=True,
            register_required="credit_sanction_register",
            effective_from=decision_date,
            status="active",
            version_number="lower-v1",
        )
        committee = SanctionCommittee.objects.create(
            committee_name="Case Committee",
            cfo_user=cfo,
            director_1_user=director_1,
            director_2_user=director_2,
            board_meeting_reference="BOARD-CASE-1",
            effective_from=decision_date,
            status="active",
            version_number="committee-v1",
        )
        snapshot = deepcopy(self.note.loan_limit_snapshot_json)
        snapshot.update(
            {
                "calculation_rule_version": "limit-v7",
                "policy_config_id": "30000000-0000-0000-0000-000000000003",
                "policy_name": "Approved loan-limit policy",
                "calculated_at": self.note.prepared_at.isoformat(),
            }
        )
        self.note.loan_limit_snapshot_json = snapshot
        self.note.save(update_fields=["loan_limit_snapshot_json"])

        submitted = self._submit({"remarks": "Create the unique shell."})
        self.assertEqual(submitted.status_code, 200)
        workflow_event_id = submitted.json()["data"]["workflow_event_id"]
        with patch.object(
            sanction_handoff_module,
            "resolve_approval_matrix",
            wraps=sanction_handoff_module.resolve_approval_matrix,
        ) as matrix_resolver, patch.object(
            sanction_handoff_module,
            "resolve_sanction_committee",
            wraps=sanction_handoff_module.resolve_sanction_committee,
        ) as committee_resolver:
            response = self.client.post(
                f"/api/v1/loan-applications/{self.application.pk}/approval-cases/",
                data={
                    "approval_type": "sanction",
                    "amount": "500000.00",
                    "reason_for_approval": "Loan appraisal recommended approval.",
                    "force_exception_route": False,
                },
                content_type="application/json",
                headers={"Authorization": f"Bearer {self._login(self.reviewer)}"},
            )
        matrix_resolver.assert_called_once_with(
            decision_type="loan_sanction",
            amount=Decimal("500000.00"),
            condition_code=None,
            decision_date=decision_date,
        )
        committee_resolver.assert_called_once_with(decision_date)

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(
            data["approval_case_id"], submitted.json()["data"]["approval_case_id"]
        )
        self.assertEqual(data["workflow_event_id"], workflow_event_id)
        self.assertEqual(data["approval_matrix_rule_id"], str(rule.pk))
        self.assertEqual(data["approval_matrix_rule_version"], "lower-v1")
        self.assertEqual(data["sanction_committee_id"], str(committee.pk))
        self.assertEqual(data["sanction_committee_version"], "committee-v1")
        self.assertEqual(data["decision_date"], decision_date.isoformat())
        self.assertEqual(data["amount"], "500000.00")
        self.assertEqual(
            data["required_approvers"],
            [
                {
                    "role_code": "cfo",
                    "user_id": str(cfo.pk),
                    "full_name": cfo.full_name,
                },
                {
                    "role_code": "director",
                    "user_id": str(director_1.pk),
                    "full_name": director_1.full_name,
                },
            ],
        )
        self.assertEqual(data["excluded_approvers"], [])
        self.assertEqual(data["related_entity_type"], "loan_application")
        self.assertEqual(data["related_entity_id"], str(self.application.pk))
        self.assertEqual(data["version"], 2)
        self.assertEqual(
            data["matrix_projection"],
            {
                "approval_matrix_rule_id": str(rule.pk),
                "version_number": "lower-v1",
                "decision_type": "loan_sanction",
                "amount": "500000.00",
                "amount_min": "0.00",
                "amount_max": "500000.00",
                "condition_code": None,
                "decision_date": decision_date.isoformat(),
                "required_approver_roles": ["cfo", "director"],
                "required_director_count": 1,
                "joint_approval_required": True,
                "register_required": "credit_sanction_register",
            },
        )
        self.assertEqual(data["loan_limit_provenance"]["calculation_rule_version"], "limit-v7")
        self.assertEqual(AuditLog.objects.filter(action="approval_case.enriched").count(), 1)
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="approval_case_enrichment").count(),
            1,
        )
        ApprovalMatrixRule.objects.create(
            decision_type="loan_sanction", amount_min="0.00", amount_max="500000.00",
            required_approver_roles_json=["cfo", "director"], required_director_count=2,
            effective_from=decision_date + timedelta(days=1), status="active",
            version_number="later-rule-v2",
        )
        SanctionCommittee.objects.create(
            committee_name="Later Committee", cfo_user=cfo,
            director_1_user=director_2, director_2_user=director_1,
            board_meeting_reference="BOARD-LATER-2",
            effective_from=decision_date + timedelta(days=1), status="active",
            version_number="later-committee-v2",
        )
        self.assertEqual(self._get_case().json()["data"], data)
        case = apps.get_model("approvals", "ApprovalCase").objects.get()
        case.current_status = "approved"
        case.save(update_fields=["current_status"])
        decided_before = apps.get_model("approvals", "ApprovalCase").objects.values().get()
        decided_repeat = self._enrich({
            "approval_type": "sanction", "amount": "500000.00",
            "reason_for_approval": "Loan appraisal recommended approval.",
            "force_exception_route": False,
        })
        self.assertEqual(decided_repeat.status_code, 409, decided_repeat.content)
        self.assertEqual(
            apps.get_model("approvals", "ApprovalCase").objects.values().get(), decided_before
        )
        self.assertEqual(AuditLog.objects.filter(action="approval_case.enriched").count(), 1)

    def test_exception_condition_not_amount_selects_two_director_route(self):
        ApprovalMatrixRule.objects.all().delete()
        SanctionCommittee.objects.all().delete()
        create_permission = self._permission("approvals.case.create", "Create approval case")
        RolePermission.objects.create(role=self.reviewer.primary_role, permission=create_permission)
        members = []
        for code, name, authority in (
            ("exception_cfo", "Exception CFO", "cfo"),
            ("exception_d1", "Exception Director 1", "director"),
            ("exception_d2", "Exception Director 2", "director"),
        ):
            user = self._user(code, name)
            user.approval_authority_type = authority
            user.save(update_fields=["approval_authority_type"])
            members.append(user)
        decision_date = timezone.localdate(self.history.decided_at)
        ApprovalMatrixRule.objects.create(
            decision_type="loan_sanction", amount_min="0.00", amount_max="500000.00",
            condition_code="exceeds_permissible_limit",
            required_approver_roles_json=["cfo", "director"], required_director_count=2,
            joint_approval_required_flag=True, register_required="exception_register",
            effective_from=decision_date, status="active", version_number="exception-v1",
        )
        SanctionCommittee.objects.create(
            committee_name="Exception Committee", cfo_user=members[0],
            director_1_user=members[1], director_2_user=members[2],
            board_meeting_reference="BOARD-EXCEPTION-1", effective_from=decision_date,
            status="active", version_number="exception-committee-v1",
        )
        snapshot = deepcopy(self.note.loan_limit_snapshot_json)
        snapshot.update({
            "exception_required_flag": True,
            "calculation_rule_version": "limit-exception-v1",
            "policy_config_id": "30000000-0000-0000-0000-000000000003",
            "policy_name": "Approved exception policy",
            "calculated_at": self.note.prepared_at.isoformat(),
        })
        self.note.loan_limit_snapshot_json = snapshot
        self.note.save(update_fields=["loan_limit_snapshot_json"])
        self.assertEqual(self._submit({"remarks": "Exception shell."}).status_code, 200)

        response = self._enrich({
            "approval_type": "sanction", "amount": "400000.00",
            "reason_for_approval": "Stored assessment requires exception approval.",
            "force_exception_route": False,
        })

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["exception_condition_code"], "exceeds_permissible_limit")
        self.assertEqual(data["matrix_projection"]["required_director_count"], 2)
        self.assertEqual(data["matrix_projection"]["register_required"], "exception_register")
        self.assertEqual(
            [item["user_id"] for item in data["required_approvers"]],
            [str(user.pk) for user in members],
        )
        case_before = apps.get_model("approvals", "ApprovalCase").objects.values().get()
        repeat = self._enrich({
            "approval_type": "sanction", "amount": "400000.00",
            "reason_for_approval": "Stored assessment requires exception approval.",
            "force_exception_route": False,
        })
        self.assertEqual(repeat.status_code, 200, repeat.content)
        self.assertEqual(repeat.json()["data"], data)
        self.assertEqual(
            apps.get_model("approvals", "ApprovalCase").objects.values().get(), case_before
        )
        self.assertEqual(AuditLog.objects.filter(action="approval_case.enriched").count(), 1)
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="approval_case_enrichment").count(), 1
        )
        conflict = self._enrich({
            "approval_type": "sanction", "amount": "400000.00",
            "reason_for_approval": "A conflicting immutable reason.",
            "force_exception_route": False,
        })
        self.assertEqual(conflict.status_code, 409, conflict.content)
        self.assertEqual(
            apps.get_model("approvals", "ApprovalCase").objects.values().get(), case_before
        )
        self.assertEqual(AuditLog.objects.filter(action="approval_case.enriched").count(), 1)

    def test_above_threshold_snapshots_cfo_and_two_directors(self):
        ApprovalMatrixRule.objects.all().delete()
        SanctionCommittee.objects.all().delete()
        permission = self._permission("approvals.case.create", "Create approval case")
        RolePermission.objects.create(role=self.reviewer.primary_role, permission=permission)
        members = []
        for code, authority in (("upper_cfo", "cfo"), ("upper_d1", "director"), ("upper_d2", "director")):
            user = self._user(code, code.replace("_", " ").title())
            user.approval_authority_type = authority
            user.save(update_fields=["approval_authority_type"])
            members.append(user)
        decision_date = timezone.localdate(self.history.decided_at)
        ApprovalMatrixRule.objects.create(
            decision_type="loan_sanction", amount_min="500000.01", amount_max=None,
            required_approver_roles_json=["cfo", "director"], required_director_count=2,
            joint_approval_required_flag=True, register_required="credit_sanction_register",
            effective_from=decision_date, status="active", version_number="upper-v1",
        )
        SanctionCommittee.objects.create(
            committee_name="Upper Committee", cfo_user=members[0],
            director_1_user=members[1], director_2_user=members[2],
            board_meeting_reference="BOARD-UPPER-1", effective_from=decision_date,
            status="active", version_number="upper-committee-v1",
        )
        self.note.recommended_amount = "500000.01"
        snapshot = deepcopy(self.note.loan_limit_snapshot_json)
        snapshot.update({
            "calculation_rule_version": "limit-upper-v1",
            "policy_config_id": "30000000-0000-0000-0000-000000000003",
            "policy_name": "Approved upper policy",
            "calculated_at": self.note.prepared_at.isoformat(),
        })
        self.note.loan_limit_snapshot_json = snapshot
        self.note.save(update_fields=["recommended_amount", "loan_limit_snapshot_json"])
        self.assertEqual(self._submit({"remarks": "Upper shell."}).status_code, 200)

        response = self._enrich({
            "approval_type": "sanction", "amount": "500000.01",
            "reason_for_approval": "Above threshold route.", "force_exception_route": False,
        })

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            [item["user_id"] for item in response.json()["data"]["required_approvers"]],
            [str(user.pk) for user in members],
        )
        self.assertEqual(response.json()["data"]["matrix_projection"]["amount_min"], "500000.01")
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="approval_case_enrichment").count(), 1
        )

    def test_no_effective_rule_leaves_existing_shell_and_ledgers_unchanged(self):
        ApprovalMatrixRule.objects.all().delete()
        SanctionCommittee.objects.all().delete()
        permission = self._permission("approvals.case.create", "Create approval case")
        RolePermission.objects.create(role=self.reviewer.primary_role, permission=permission)
        snapshot = deepcopy(self.note.loan_limit_snapshot_json)
        snapshot.update({
            "calculation_rule_version": "limit-v7",
            "policy_config_id": "30000000-0000-0000-0000-000000000003",
            "policy_name": "Approved policy",
            "calculated_at": self.note.prepared_at.isoformat(),
        })
        self.note.loan_limit_snapshot_json = snapshot
        self.note.save(update_fields=["loan_limit_snapshot_json"])
        self.assertEqual(self._submit({"remarks": "Unrouted shell."}).status_code, 200)
        case_model = apps.get_model("approvals", "ApprovalCase")
        before = {
            "case": case_model.objects.values().get(),
            "audit": list(AuditLog.objects.exclude(action__startswith="auth.").values()),
            "workflow": list(WorkflowEvent.objects.values()),
        }

        response = self._enrich({
            "approval_type": "sanction", "amount": "400000.00",
            "reason_for_approval": "No effective rule.", "force_exception_route": False,
        })

        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(response.json()["error"]["code"], "NO_EFFECTIVE_APPROVAL_RULE")
        self.assertEqual(case_model.objects.values().get(), before["case"])
        self.assertEqual(
            list(AuditLog.objects.exclude(action__startswith="auth.").values()), before["audit"]
        )
        self.assertEqual(list(WorkflowEvent.objects.values()), before["workflow"])

    def test_enrichment_requires_auth_permission_and_fresh_policy_provenance(self):
        self.assertEqual(self._submit({"remarks": "Protected shell."}).status_code, 200)
        case_model = apps.get_model("approvals", "ApprovalCase")
        case_before = case_model.objects.values().get()
        payload = {
            "approval_type": "sanction", "amount": "400000.00",
            "reason_for_approval": "Protected enrichment.", "force_exception_route": False,
        }
        url = f"/api/v1/loan-applications/{self.application.pk}/approval-cases/"

        unauthenticated = self.client.post(url, data=payload, content_type="application/json")
        self.assertEqual(unauthenticated.status_code, 401)
        denied = self._enrich(payload, actor=self.preparer)
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(denied.json()["error"]["code"], "FORBIDDEN")
        self.assertEqual(case_model.objects.values().get(), case_before)

        permission = self._permission("approvals.case.create", "Create approval case")
        RolePermission.objects.create(role=self.reviewer.primary_role, permission=permission)
        stale = self._enrich(payload)
        self.assertEqual(stale.status_code, 409, stale.content)
        self.assertEqual(stale.json()["error"]["code"], "INVALID_STATE_TRANSITION")
        self.assertEqual(case_model.objects.values().get(), case_before)
        self.assertFalse(AuditLog.objects.filter(action="approval_case.enriched").exists())
        self.assertFalse(
            WorkflowEvent.objects.filter(workflow_name="approval_case_enrichment").exists()
        )

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

    def test_open_case_configuration_snapshot_is_immutable_across_governed_decisions(self):
        self.assertEqual(self._submit({"remarks": "Freeze configuration facts."}).status_code, 200)
        ApprovalMatrixRule.objects.all().delete()
        SanctionCommittee.objects.all().delete()
        checker = self._user("snapshot_checker", "Snapshot Checker")
        checker.approval_authority_type = "cfo"
        checker.save(update_fields=["approval_authority_type"])
        director_1 = self._user("snapshot_director_1", "Snapshot Director 1")
        director_1.approval_authority_type = "director"
        director_1.save(update_fields=["approval_authority_type"])
        director_2 = self._user("snapshot_director_2", "Snapshot Director 2")
        director_2.approval_authority_type = "director"
        director_2.save(update_fields=["approval_authority_type"])
        rule = ApprovalMatrixRule.objects.create(
            decision_type="loan_sanction", amount_min="0", amount_max="500000",
            required_approver_roles_json=["cfo", "director"], required_director_count=1,
            effective_from=date(2026, 4, 1), status="active", version_number="snapshot-v1",
        )
        committee = SanctionCommittee.objects.create(
            committee_name="Snapshot Committee", cfo_user=checker,
            director_1_user=director_1, director_2_user=director_2,
            board_meeting_reference="BOARD-SNAPSHOT-1", effective_from=date(2026, 4, 1),
            status="active", version_number="snapshot-v1",
        )
        case_model = apps.get_model("approvals", "ApprovalCase")
        case = case_model.objects.get()
        case.approval_matrix_rule = rule
        case.approval_matrix_rule_version = rule.version_number
        case.sanction_committee = committee
        case.sanction_committee_version = committee.version_number
        case.required_approvers_json = {
            "cfo_user_id": str(checker.pk),
            "director_user_ids": [str(director_1.pk)],
        }
        case.decision_date = date(2026, 7, 13)
        case.version = 1
        case.save(update_fields=[
            "approval_matrix_rule", "approval_matrix_rule_version", "sanction_committee",
            "sanction_committee_version", "required_approvers_json", "decision_date", "version",
        ])
        before = case_model.objects.filter(pk=case.pk).values().get()
        request = RequestFactory().post("/api/v1/approval-matrix-rules/")
        replacement = {
            "decision_type": "loan_sanction", "amount_min": "0", "amount_max": "500000",
            "condition_code": None, "required_approver_roles": ["cfo", "director"],
            "required_director_count": 2, "joint_approval_required_flag": True,
            "register_required": "credit_sanction_register", "effective_from": "2027-01-01",
            "effective_to": None, "version_number": "snapshot-v2", "reason": "Annual replacement",
        }
        rejected = approval_matrix_configuration.supersede_rule(
            self.reviewer, request, rule.pk, replacement
        )
        approval_matrix_configuration.decide_proposal(
            rejected["approval_configuration_proposal_id"], checker, request,
            {"version": 1, "reason": "Evidence incomplete"}, "reject",
        )
        approved = approval_matrix_configuration.supersede_rule(
            self.reviewer, request, rule.pk, replacement | {"version_number": "snapshot-v2-approved"}
        )
        approval_matrix_configuration.decide_proposal(
            approved["approval_configuration_proposal_id"], checker, request,
            {"version": 1}, "approve",
        )
        resolve_approval_matrix(
            decision_type="loan_sanction", amount="100", condition_code=None,
            decision_date=date(2026, 7, 13),
        )
        resolve_sanction_committee(date(2026, 7, 13))
        approval_matrix_configuration.get_proposal(approved["approval_configuration_proposal_id"], checker)
        self.assertEqual(case_model.objects.filter(pk=case.pk).values().get(), before)

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

    def _enrich(self, payload, *, actor=None):
        actor = actor or self.reviewer
        return self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/approval-cases/",
            data=payload,
            content_type="application/json",
            headers={"Authorization": f"Bearer {self._login(actor)}"},
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
        from sfpcl_credit.credit.modules.appraisal_workflow import (
            AppraisalWorkflow,
            CreditModuleInvalidStateError,
        )

        projected = AppraisalWorkflow().get(
            actor=self.reviewer,
            application_id=self.application.pk,
        ).snapshot
        sanction_action = next(
            item
            for item in projected["available_actions"]
            if item["action_code"] == "credit.appraisal.submit_sanction"
        )
        self.assertTrue(sanction_action["enabled"])

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
                with self.assertRaisesMessage(
                    CreditModuleInvalidStateError,
                    "Only a reviewed appraisal note can be submitted for sanction.",
                ):
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
