from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from decimal import Decimal
import ast
from importlib.util import resolve_name
from pathlib import Path
from threading import Event
import tempfile
import uuid
from unittest import skipUnless
from unittest.mock import patch

from django.apps import apps
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import close_old_connections, connection, connections
from django.test import Client, RequestFactory, TestCase, TransactionTestCase, override_settings
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication, RejectionNote
from sfpcl_credit.approvals.models import (
    ApprovalConfigurationProposal,
    ApprovalMatrixRule,
    SanctionCommittee,
)
from sfpcl_credit.approvals.modules import approval_matrix_configuration
from sfpcl_credit.approvals.modules import sanction_handoff as sanction_handoff_module
from sfpcl_credit.approvals.modules import exception_register
from sfpcl_credit.approvals.modules.approval_matrix import resolve_approval_matrix
from sfpcl_credit.approvals.modules.approval_case_projection import (
    refresh_approval_case_projection,
)
from sfpcl_credit.approvals.modules.sanction_committee import resolve_sanction_committee
from sfpcl_credit.credit.models import (
    AppraisalReviewDecision,
    LoanAppraisalNote,
    RiskAssessment,
)
from sfpcl_credit.credit.modules.appraisal_workflow import (
    project_approval_case_review_facts,
)
from sfpcl_credit.configurations.models import VersionHistory
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


@override_settings(DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-sanction-doc-tests-"))
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
                "member_active_check": "pass",
                "default_check": "pass",
                "document_check": "pass",
                "terms_acceptance_check": "pass",
                "purpose_check": "pass",
                "nominee_check": "pass",
                "overall_result": "eligible",
                "assessment_notes": "Eligible.",
                "active_member_snapshot": {},
                "assessed_by_user_id": str(self.preparer.pk),
                "assessed_at": self.reviewed_at.isoformat(),
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
        self.assertEqual(data["current_status"], "pending")
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

    def test_above_limit_exception_completes_public_three_approver_and_register_workflow(self):
        ApprovalMatrixRule.objects.all().delete()
        SanctionCommittee.objects.all().delete()
        create_permission = self._permission("approvals.case.create", "Create approval case")
        RolePermission.objects.create(role=self.reviewer.primary_role, permission=create_permission)
        read_permission = self._permission("approvals.case.read", "Read approval cases")
        RolePermission.objects.create(role=self.reviewer.primary_role, permission=read_permission)
        exception_permission = self._permission(
            "approvals.exception.create", "Create exception entry"
        )
        for code, name in (
            ("approvals.general_meeting.record", "Record general meeting evidence"),
            ("documents.file.download", "Reference document files"),
            ("documents.file.upload", "Upload document files"),
        ):
            RolePermission.objects.create(
                role=self.reviewer.primary_role,
                permission=self._permission(code, name),
            )
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
        approver_permissions = [
            read_permission,
            self._permission("approvals.case.approve", "Approve approval cases"),
        ]
        for member in members:
            for permission in approver_permissions:
                RolePermission.objects.create(
                    role=member.primary_role, permission=permission
                )
        for code, name in (
            ("approvals.exception_register.read", "Read Exception Register"),
            ("approvals.sanction.read", "Read sanction decisions"),
            ("approvals.sanction_register.read", "Read Credit Sanction Register"),
        ):
            RolePermission.objects.create(
                role=members[0].primary_role,
                permission=self._permission(code, name),
            )
        decision_date = timezone.localdate(self.history.decided_at)
        ApprovalMatrixRule.objects.create(
            decision_type="loan_sanction", amount_min="0.00", amount_max=None,
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
        related_director = self._user(
            "related_noncommittee_director", "Related Noncommittee Director"
        )
        apps.get_model("approvals", "ApprovalConflictDeclaration").objects.create(
            loan_application=self.application,
            user=related_director,
            conflict_type="director_relative",
            reason="Borrower is related to a Director outside the assigned committee.",
            declared_by_user=self.reviewer,
        )
        snapshot = deepcopy(self.note.loan_limit_snapshot_json)
        snapshot.update({
            "exception_required_flag": True,
            "calculation_rule_version": "limit-exception-v1",
            "policy_config_id": "30000000-0000-0000-0000-000000000003",
            "policy_name": "Approved exception policy",
            "calculated_at": self.note.prepared_at.isoformat(),
        })
        self.note.recommended_amount = Decimal("600000.00")
        self.note.loan_limit_snapshot_json = snapshot
        self.note.save(update_fields=["recommended_amount", "loan_limit_snapshot_json"])
        self.assertEqual(self._submit({"remarks": "Exception shell."}).status_code, 200)

        missing_reason = self._enrich({
            "approval_type": "sanction", "amount": "600000.00",
            "reason_for_approval": "Stored assessment requires exception approval.",
            "force_exception_route": False,
        })
        self.assertEqual(missing_reason.status_code, 400, missing_reason.content)
        self.assertIn(
            "business_reason", missing_reason.json()["error"]["field_errors"]
        )
        self.assertFalse(
            apps.get_model("approvals", "ExceptionRegisterEntry").objects.exists()
        )
        reviewer_token = self._login(self.reviewer)
        supporting_upload = self.client.post(
            "/api/v1/document-files/",
            data={
                "file": SimpleUploadedFile(
                    "cash-flow-evidence.pdf",
                    b"public exception supporting evidence",
                    content_type="application/pdf",
                ),
                "document_category": "legal",
                "sensitivity_level": "restricted",
                "related_entity_type": "application",
                "related_entity_id": str(self.application.pk),
            },
            headers={"Authorization": f"Bearer {reviewer_token}"},
        )
        self.assertEqual(supporting_upload.status_code, 200, supporting_upload.content)
        supporting_document_id = supporting_upload.json()["data"]["document_id"]
        exception_payload = {
            "approval_type": "sanction", "amount": "600000.00",
            "reason_for_approval": "Stored assessment requires exception approval.",
            "business_reason": "Seasonal exception is commercially justified.",
            "risk_assessment": "Seasonal cash-flow monitoring.",
            "supporting_document_ids": [supporting_document_id],
            "force_exception_route": False,
        }
        denied = self._enrich(exception_payload)
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertFalse(
            apps.get_model("approvals", "ExceptionRegisterEntry").objects.exists()
        )
        self.assertFalse(AuditLog.objects.filter(action="approval_case.enriched").exists())
        RolePermission.objects.create(
            role=self.reviewer.primary_role, permission=exception_permission
        )
        duplicate_ids = self._enrich(
            exception_payload
            | {"supporting_document_ids": [supporting_document_id, supporting_document_id]}
        )
        self.assertEqual(duplicate_ids.status_code, 400, duplicate_ids.content)
        self.assertIn(
            "supporting_document_ids",
            duplicate_ids.json()["error"]["field_errors"],
        )
        self.assertFalse(
            apps.get_model("approvals", "ExceptionRegisterEntry").objects.exists()
        )
        too_many_ids = self._enrich(
            exception_payload
            | {"supporting_document_ids": [str(uuid.uuid4()) for _ in range(21)]}
        )
        self.assertEqual(too_many_ids.status_code, 400, too_many_ids.content)
        self.assertIn(
            "supporting_document_ids",
            too_many_ids.json()["error"]["field_errors"],
        )
        self.assertFalse(
            apps.get_model("approvals", "ExceptionRegisterEntry").objects.exists()
        )
        response = self._enrich(exception_payload)

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["exception_condition_code"], "exceeds_permissible_limit")
        self.assertEqual(data["matrix_projection"]["required_director_count"], 2)
        self.assertEqual(data["matrix_projection"]["register_required"], "exception_register")
        self.assertEqual(
            [item["user_id"] for item in data["required_approvers"]],
            [str(user.pk) for user in members],
        )
        case = apps.get_model("approvals", "ApprovalCase").objects.get(
            pk=data["approval_case_id"]
        )
        self.assertTrue(case.routing_snapshot_is_coherent)
        listed = self.client.get(
            "/api/v1/approval-cases/",
            headers={"Authorization": f"Bearer {self._login(self.reviewer)}"},
        )
        self.assertEqual(listed.status_code, 200, listed.content)
        self.assertEqual(listed.json()["pagination"]["total_count"], 1)
        self.assertEqual(listed.json()["data"][0]["approval_case_id"], str(case.pk))
        register_entry = apps.get_model(
            "approvals", "ExceptionRegisterEntry"
        ).objects.get(approval_case_id=data["approval_case_id"])
        self.assertEqual(register_entry.loan_application, self.application)
        self.assertEqual(register_entry.exception_type, "exceeds_loan_limit")
        self.assertEqual(
            register_entry.description,
            "Recommended loan amount exceeds the frozen permissible loan limit.",
        )
        self.assertEqual(
            register_entry.business_reason,
            "Seasonal exception is commercially justified.",
        )
        self.assertEqual(register_entry.risk_assessment, "Seasonal cash-flow monitoring.")
        self.assertEqual(
            register_entry.supporting_documents_json,
            [
                {
                    "document_id": supporting_document_id,
                    "file_name": "cash-flow-evidence.pdf",
                    "mime_type": "application/pdf",
                    "file_size_bytes": 36,
                    "sensitivity_level": "restricted",
                    "uploaded_at": supporting_upload.json()["data"]["uploaded_at"],
                }
            ],
        )
        self.assertEqual(register_entry.status, "pending")
        self.assertIsNone(register_entry.closed_at)
        creation_audit = AuditLog.objects.get(action="exception_register.created")
        self.assertEqual(creation_audit.entity_id, register_entry.pk)
        self.assertEqual(
            creation_audit.new_value_json["approval_case_id"], data["approval_case_id"]
        )
        self.assertEqual(
            creation_audit.new_value_json["supporting_document_ids"],
            [supporting_document_id],
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="exception_register").count(),
            1,
        )
        self.assertIn(
            "with 1 supporting document reference(s)",
            WorkflowEvent.objects.get(
                workflow_name="exception_register"
            ).trigger_reason,
        )
        case_before = apps.get_model("approvals", "ApprovalCase").objects.values().get()
        repeat = self._enrich({
            "approval_type": "sanction", "amount": "600000.00",
            "reason_for_approval": "Stored assessment requires exception approval.",
            "business_reason": "Seasonal exception is commercially justified.",
            "risk_assessment": "Seasonal cash-flow monitoring.",
            "supporting_document_ids": [supporting_document_id],
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
        self.assertEqual(
            apps.get_model("approvals", "ExceptionRegisterEntry").objects.count(), 1
        )
        changed_risk = self._enrich(
            exception_payload | {"risk_assessment": "Changed immutable risk text."}
        )
        self.assertEqual(changed_risk.status_code, 409, changed_risk.content)
        register_entry.refresh_from_db()
        self.assertEqual(register_entry.risk_assessment, "Seasonal cash-flow monitoring.")
        changed_business_reason = self._enrich(
            exception_payload
            | {"business_reason": "Changed immutable exception justification."}
        )
        self.assertEqual(
            changed_business_reason.status_code, 409, changed_business_reason.content
        )
        register_entry.refresh_from_db()
        self.assertEqual(
            register_entry.business_reason,
            "Seasonal exception is commercially justified.",
        )
        changed_document_upload = self.client.post(
            "/api/v1/document-files/",
            data={
                "file": SimpleUploadedFile(
                    "changed-evidence.pdf",
                    b"changed exception supporting evidence",
                    content_type="application/pdf",
                ),
                "document_category": "legal",
                "sensitivity_level": "restricted",
                "related_entity_type": "application",
                "related_entity_id": str(self.application.pk),
            },
            headers={"Authorization": f"Bearer {reviewer_token}"},
        )
        changed_document_id = changed_document_upload.json()["data"]["document_id"]
        before_changed_document = self._approval_case_business_ledger()
        changed_document = self._enrich(
            exception_payload | {"supporting_document_ids": [changed_document_id]}
        )
        self.assertEqual(changed_document.status_code, 409, changed_document.content)
        self.assertEqual(self._approval_case_business_ledger(), before_changed_document)
        conflict = self._enrich({
            "approval_type": "sanction", "amount": "600000.00",
            "reason_for_approval": "A conflicting immutable reason.",
            "business_reason": "Seasonal exception is commercially justified.",
            "risk_assessment": "Seasonal cash-flow monitoring.",
            "force_exception_route": False,
        })
        self.assertEqual(conflict.status_code, 409, conflict.content)
        self.assertEqual(
            apps.get_model("approvals", "ApprovalCase").objects.values().get(), case_before
        )
        self.assertEqual(AuditLog.objects.filter(action="approval_case.enriched").count(), 1)

        cfo_token = self._login(members[0])
        assigned = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true",
            headers={"Authorization": f"Bearer {cfo_token}"},
        )
        detail = self.client.get(
            f"/api/v1/approval-cases/{case.pk}/",
            headers={"Authorization": f"Bearer {cfo_token}"},
        )
        self.assertEqual(assigned.status_code, 200, assigned.content)
        self.assertEqual(assigned.json()["pagination"]["total_count"], 1)
        self.assertEqual(assigned.json()["data"][0]["approval_case_id"], str(case.pk))
        self.assertEqual(detail.status_code, 200, detail.content)
        self.assertEqual(detail.json()["data"]["approval_case_id"], str(case.pk))
        self.assertEqual(detail.json()["data"]["exception_reason"], register_entry.business_reason)
        self.assertTrue(detail.json()["data"]["general_meeting_evidence_required"])

        document_ids = []
        reviewer_token = self._login(self.reviewer)
        for file_name in ("notice.pdf", "minutes.pdf", "resolution.pdf"):
            upload = self.client.post(
                "/api/v1/document-files/",
                data={
                    "file": SimpleUploadedFile(
                        file_name,
                        f"public exception evidence:{file_name}".encode(),
                        content_type="application/pdf",
                    ),
                    "document_category": "legal",
                    "sensitivity_level": "restricted",
                    "related_entity_type": "application",
                    "related_entity_id": str(self.application.pk),
                },
                headers={"Authorization": f"Bearer {reviewer_token}"},
            )
            self.assertEqual(upload.status_code, 200, upload.content)
            document_ids.append(upload.json()["data"]["document_id"])
        meeting_payload = {
            "related_party_type": "director_relative",
            "related_party_user_id": str(related_director.pk),
            "relationship_description": "Borrower is related to a noncommittee Director.",
            "meeting_date": timezone.localdate().isoformat(),
            "notice_document_id": document_ids[0],
            "minutes_document_id": document_ids[1],
            "resolution_document_id": document_ids[2],
        }
        original_reasons = (
            data["reason_for_approval"],
            data["exception_reason"],
            str(register_entry.pk),
        )
        for status in ("pending", "rejected", "approved"):
            meeting = self.client.post(
                f"/api/v1/loan-applications/{self.application.pk}/general-meeting-approval/",
                data={**meeting_payload, "approval_status": status},
                content_type="application/json",
                headers={"Authorization": f"Bearer {reviewer_token}"},
            )
            self.assertEqual(meeting.status_code, 200, meeting.content)
            current = self.client.get(
                f"/api/v1/approval-cases/{case.pk}/",
                headers={"Authorization": f"Bearer {cfo_token}"},
            )
            current_assigned = self.client.get(
                "/api/v1/approval-cases/?assigned_to_me=true",
                headers={"Authorization": f"Bearer {cfo_token}"},
            )
            self.assertEqual(
                current.json()["data"]["general_meeting_approval"],
                {**meeting.json()["data"], "evidence_scope": "current_pending"},
            )
            self.assertEqual(current_assigned.json()["pagination"]["total_count"], 1)
            self.assertEqual(
                (
                    current.json()["data"]["reason_for_approval"],
                    current.json()["data"]["exception_reason"],
                    str(
                        apps.get_model(
                            "approvals", "ExceptionRegisterEntry"
                        ).objects.get(approval_case=case).pk
                    ),
                ),
                original_reasons,
            )

        action_responses = []
        for version, approver in zip((2, 3, 4), members, strict=True):
            action_response = self.client.post(
                f"/api/v1/approval-cases/{case.pk}/approve/",
                data={"version": version, "comments": f"{approver.full_name} approves."},
                content_type="application/json",
                headers={"Authorization": f"Bearer {self._login(approver)}"},
            )
            self.assertEqual(action_response.status_code, 200, action_response.content)
            action_responses.append(action_response.json()["data"])
        self.assertEqual(
            [item["approval_case_status"] for item in action_responses],
            ["pending", "pending", "approved"],
        )
        self.assertFalse(action_responses[0]["sanction_decision_created"])
        self.assertFalse(action_responses[1]["sanction_decision_created"])
        self.assertTrue(action_responses[2]["sanction_decision_created"])

        register_entry.refresh_from_db()
        self.assertEqual(register_entry.status, "approved")
        self.assertIsNotNone(register_entry.closed_at)
        exception_rows = self.client.get(
            "/api/v1/exception-register/?status=approved&exception_type=exceeds_loan_limit",
            headers={"Authorization": f"Bearer {cfo_token}"},
        )
        decision = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/sanction-decision/",
            headers={"Authorization": f"Bearer {cfo_token}"},
        )
        sanction_rows = self.client.get(
            "/api/v1/credit-sanction-register/?decision=sanctioned",
            headers={"Authorization": f"Bearer {cfo_token}"},
        )
        self.assertEqual(exception_rows.status_code, 200, exception_rows.content)
        self.assertEqual(exception_rows.json()["pagination"]["total_count"], 1)
        self.assertEqual(
            exception_rows.json()["data"][0]["exception_register_entry_id"],
            str(register_entry.pk),
        )
        exception_row = exception_rows.json()["data"][0]
        self.assertEqual(
            exception_row["supporting_documents"],
            register_entry.supporting_documents_json,
        )
        self.assertEqual(
            [action["comments"] for action in exception_row["approval_actions"]],
            [f"{approver.full_name} approves." for approver in members],
        )
        self.assertTrue(
            all(action["acted_at"] for action in exception_row["approval_actions"])
        )
        self.assertEqual(decision.status_code, 200, decision.content)
        self.assertEqual(
            decision.json()["data"]["sanction_decision_id"],
            action_responses[2]["sanction_decision_id"],
        )
        self.assertEqual(decision.json()["data"]["sanctioned_amount"], "600000.00")
        self.assertEqual(sanction_rows.status_code, 200, sanction_rows.content)
        self.assertEqual(sanction_rows.json()["pagination"]["total_count"], 1)
        sanction_row = sanction_rows.json()["data"][0]
        self.assertEqual(sanction_row["approval_case_id"], str(case.pk))
        self.assertEqual(
            sanction_row["sanction_decision_id"],
            action_responses[2]["sanction_decision_id"],
        )
        self.assertEqual(
            sanction_row["exception_reference"]["exception_register_entry_id"],
            str(register_entry.pk),
        )
        self.assertEqual(
            decision.json()["data"]["decision_reason"],
            "Stored assessment requires exception approval.",
        )
        self.assertEqual(
            sanction_row["reasons"],
            "Stored assessment requires exception approval.",
        )
        self.assertEqual(
            sanction_row["exception_reference"]["business_reason"],
            "Seasonal exception is commercially justified.",
        )
        self.assertNotEqual(
            sanction_row["reasons"],
            sanction_row["exception_reference"]["business_reason"],
        )
        unused_reader = self._user(
            "unused_exception_committee_candidate",
            "Unused Exception Committee Candidate",
        )
        unused_reader.approval_authority_type = "director"
        unused_reader.save(update_fields=["approval_authority_type"])
        for permission in approver_permissions:
            RolePermission.objects.create(
                role=unused_reader.primary_role,
                permission=permission,
            )
        for permission_code in (
            "approvals.sanction.read",
            "approvals.sanction_register.read",
        ):
            RolePermission.objects.create(
                role=unused_reader.primary_role,
                permission=Permission.objects.get(permission_code=permission_code),
            )
            RolePermission.objects.create(
                role=members[1].primary_role,
                permission=Permission.objects.get(permission_code=permission_code),
            )
        ordinary_case, ordinary_application = self._create_scoped_ordinary_terminal_case(
            cfo=members[0], director=unused_reader
        )
        ordinary_cfo_action = self.client.post(
            f"/api/v1/approval-cases/{ordinary_case.pk}/approve/",
            data={"version": 2, "comments": "CFO approves ordinary case."},
            content_type="application/json",
            headers={"Authorization": f"Bearer {cfo_token}"},
        )
        unused_token = self._login(unused_reader)
        ordinary_final = self.client.post(
            f"/api/v1/approval-cases/{ordinary_case.pk}/approve/",
            data={"version": 3, "comments": "Director approves ordinary case."},
            content_type="application/json",
            headers={"Authorization": f"Bearer {unused_token}"},
        )
        self.assertEqual(ordinary_cfo_action.status_code, 200, ordinary_cfo_action.content)
        self.assertEqual(ordinary_final.status_code, 200, ordinary_final.content)
        unrelated_decision = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/sanction-decision/",
            headers={"Authorization": f"Bearer {unused_token}"},
        )
        unrelated_register = self.client.get(
            "/api/v1/credit-sanction-register/?decision=sanctioned",
            headers={"Authorization": f"Bearer {unused_token}"},
        )
        self.assertEqual(unrelated_decision.status_code, 403)
        self.assertEqual(
            unrelated_decision.json()["error"]["code"], "OBJECT_ACCESS_DENIED"
        )
        self.assertEqual(unrelated_register.status_code, 200)
        self.assertEqual(unrelated_register.json()["pagination"]["total_count"], 1)
        self.assertEqual(
            unrelated_register.json()["data"][0]["approval_case_id"],
            str(ordinary_case.pk),
        )
        ordinary_decision = self.client.get(
            f"/api/v1/loan-applications/{ordinary_application.pk}/sanction-decision/",
            headers={"Authorization": f"Bearer {unused_token}"},
        )
        self.assertEqual(ordinary_decision.status_code, 200, ordinary_decision.content)
        first_director_token = self._login(members[1])
        first_director_register = self.client.get(
            "/api/v1/credit-sanction-register/?decision=sanctioned",
            headers={"Authorization": f"Bearer {first_director_token}"},
        )
        first_director_other_decision = self.client.get(
            f"/api/v1/loan-applications/{ordinary_application.pk}/sanction-decision/",
            headers={"Authorization": f"Bearer {first_director_token}"},
        )
        self.assertEqual(first_director_register.status_code, 200)
        self.assertEqual(first_director_register.json()["pagination"]["total_count"], 1)
        self.assertEqual(
            first_director_register.json()["data"][0]["approval_case_id"], str(case.pk)
        )
        self.assertEqual(first_director_other_decision.status_code, 403)

        cfo_two_case_register = self.client.get(
            "/api/v1/credit-sanction-register/?decision=sanctioned",
            headers={"Authorization": f"Bearer {cfo_token}"},
        )
        self.assertEqual(cfo_two_case_register.status_code, 200)
        self.assertEqual(cfo_two_case_register.json()["pagination"]["total_count"], 2)
        above_limit_row = next(
            row
            for row in cfo_two_case_register.json()["data"]
            if row["approval_case_id"] == str(case.pk)
        )
        self.assertEqual(
            above_limit_row["reasons"], "Stored assessment requires exception approval."
        )
        self.assertEqual(
            above_limit_row["exception_reference"]["business_reason"],
            "Seasonal exception is commercially justified.",
        )
        self.assertNotEqual(
            above_limit_row["reasons"],
            above_limit_row["exception_reference"]["business_reason"],
        )
    def test_exception_type_vocabulary_rejects_unknown_values(self):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError) as raised:
            exception_register.validate_exception_type("display-only-exception")
        self.assertIn("exception_type", raised.exception.message_dict)
        self.assertEqual(
            exception_register.validate_exception_type("stage_bypass"),
            "stage_bypass",
        )
        self.assertEqual(exception_register.validate_exception_type("waiver"), "waiver")

    def test_contradictory_frozen_exception_predicates_are_stable_zero_write_denials(self):
        create_permission = self._permission(
            "approvals.case.create", "Create approval case"
        )
        RolePermission.objects.create(
            role=self.reviewer.primary_role, permission=create_permission
        )
        snapshot = {
            **self.note.loan_limit_snapshot_json,
            "calculation_rule_version": "contradiction-limit-v1",
            "policy_config_id": "30000000-0000-0000-0000-000000000003",
            "policy_name": "Approved contradiction test policy",
            "calculated_at": self.note.prepared_at.isoformat(),
        }
        self.note.loan_limit_snapshot_json = snapshot
        self.note.save(update_fields=["loan_limit_snapshot_json"])
        submitted = self._submit({"remarks": "Create contradiction test shell."})
        self.assertEqual(submitted.status_code, 200, submitted.content)
        case_model = apps.get_model("approvals", "ApprovalCase")
        exception_model = apps.get_model("approvals", "ExceptionRegisterEntry")

        for amount, flag in (
            (Decimal("500000.00"), True),
            (Decimal("600000.00"), False),
        ):
            with self.subTest(amount=amount, exception_required_flag=flag):
                snapshot = {
                    **self.note.loan_limit_snapshot_json,
                    "exception_required_flag": flag,
                }
                self.note.recommended_amount = amount
                self.note.loan_limit_snapshot_json = snapshot
                self.note.save(
                    update_fields=["recommended_amount", "loan_limit_snapshot_json"]
                )
                before = {
                    "case": case_model.objects.values().get(),
                    "exceptions": exception_model.objects.count(),
                    "audits": AuditLog.objects.exclude(
                        action__startswith="auth."
                    ).count(),
                    "workflows": WorkflowEvent.objects.count(),
                    "communications": apps.get_model(
                        "communications", "Communication"
                    ).objects.count(),
                }

                denied = self._enrich(
                    {
                        "approval_type": "sanction",
                        "amount": f"{amount:.2f}",
                        "reason_for_approval": "Contradictory facts must not route.",
                        "business_reason": "This payload cannot repair frozen facts.",
                        "force_exception_route": False,
                    }
                )

                self.assertEqual(denied.status_code, 409, denied.content)
                self.assertEqual(
                    denied.json()["error"]["code"], "INVALID_STATE_TRANSITION"
                )
                self.assertEqual(case_model.objects.values().get(), before["case"])
                self.assertEqual(exception_model.objects.count(), before["exceptions"])
                self.assertEqual(
                    AuditLog.objects.exclude(action__startswith="auth.").count(),
                    before["audits"],
                )
                self.assertEqual(WorkflowEvent.objects.count(), before["workflows"])
                self.assertEqual(
                    apps.get_model("communications", "Communication").objects.count(),
                    before["communications"],
                )

    def test_forced_within_limit_endpoint_routes_and_registers_truthful_waiver(self):
        ApprovalMatrixRule.objects.all().delete()
        SanctionCommittee.objects.all().delete()
        for code in ("approvals.case.create", "approvals.exception.create"):
            permission = self._permission(code, code)
            RolePermission.objects.create(
                role=self.reviewer.primary_role, permission=permission
            )
        members = []
        for code, authority in (
            ("forced_cfo", "cfo"),
            ("forced_director_1", "director"),
            ("forced_director_2", "director"),
        ):
            user = self._user(code, code.replace("_", " ").title())
            user.approval_authority_type = authority
            user.save(update_fields=["approval_authority_type"])
            members.append(user)
        decision_date = timezone.localdate(self.history.decided_at)
        ApprovalMatrixRule.objects.create(
            decision_type="loan_sanction",
            amount_min="0.00",
            amount_max="500000.00",
            condition_code="exceeds_permissible_limit",
            required_approver_roles_json=["cfo", "director"],
            required_director_count=2,
            joint_approval_required_flag=True,
            register_required="exception_register",
            effective_from=decision_date,
            status="active",
            version_number="forced-exception-v1",
        )
        SanctionCommittee.objects.create(
            committee_name="Forced Exception Committee",
            cfo_user=members[0],
            director_1_user=members[1],
            director_2_user=members[2],
            board_meeting_reference="BOARD-FORCED-1",
            effective_from=decision_date,
            status="active",
            version_number="forced-committee-v1",
        )
        snapshot = deepcopy(self.note.loan_limit_snapshot_json)
        snapshot.update(
            {
                "exception_required_flag": False,
                "calculation_rule_version": "within-limit-v1",
                "policy_config_id": "30000000-0000-0000-0000-000000000003",
                "policy_name": "Approved within-limit policy",
                "calculated_at": self.note.prepared_at.isoformat(),
            }
        )
        self.note.loan_limit_snapshot_json = snapshot
        self.note.save(update_fields=["loan_limit_snapshot_json"])
        self.assertEqual(self._submit({"remarks": "Forced exception shell."}).status_code, 200)
        base_payload = {
            "approval_type": "sanction",
            "amount": "400000.00",
            "reason_for_approval": "Appraisal recommends a governed exception.",
            "force_exception_route": True,
            "exception_type": "waiver",
        }

        missing_type = self._enrich(
            {
                key: value
                for key, value in base_payload.items()
                if key != "exception_type"
            }
            | {"business_reason": "Board policy waiver is documented."}
        )
        self.assertEqual(missing_type.status_code, 400, missing_type.content)
        self.assertIn("exception_type", missing_type.json()["error"]["field_errors"])
        missing_reason = self._enrich(base_payload)
        self.assertEqual(missing_reason.status_code, 400)
        self.assertIn("business_reason", missing_reason.json()["error"]["field_errors"])
        response = self._enrich(
            base_payload | {"business_reason": "Board policy waiver is documented."}
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["matrix_projection"]["required_director_count"], 2)
        self.assertFalse(data["exception_required_flag"])
        entry = apps.get_model("approvals", "ExceptionRegisterEntry").objects.get()
        self.assertEqual(str(entry.approval_case_id), data["approval_case_id"])
        self.assertEqual(entry.exception_type, "waiver")
        self.assertEqual(entry.status, "pending")
        self.assertEqual(AuditLog.objects.filter(action="exception_register.created").count(), 1)
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="exception_register").count(), 1
        )
        before = self._approval_case_business_ledger()
        changed_type = self._enrich(
            base_payload
            | {
                "business_reason": "Board policy waiver is documented.",
                "exception_type": "stage_bypass",
            }
        )
        self.assertEqual(changed_type.status_code, 409, changed_type.content)
        self.assertEqual(self._approval_case_business_ledger(), before)

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
            "final_eligible_loan_amount": "600000.00",
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

    def test_enrichment_replay_rejects_changed_loan_limit_assessment_provenance(self):
        setup = self._create_real_enriched_case()
        changed_assessment_id = "70000000-0000-0000-0000-000000000007"
        self.note.loan_limit_assessment_id_snapshot = changed_assessment_id
        self.note.loan_limit_snapshot_json[
            "loan_limit_assessment_id"
        ] = changed_assessment_id
        self.note.save(
            update_fields=[
                "loan_limit_assessment_id_snapshot",
                "loan_limit_snapshot_json",
            ]
        )
        before = self._approval_case_business_ledger()

        response = self._enrich_with_token(setup["payload"], setup["token"])

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(response.json()["error"]["code"], "INVALID_STATE_TRANSITION")
        self.assertEqual(self._approval_case_business_ledger(), before)

    def test_enrichment_replay_rejects_changed_policy_provenance(self):
        setup = self._create_real_enriched_case()
        self.note.loan_limit_snapshot_json.update(
            {
                "calculation_rule_version": "changed-limit-v2",
                "policy_config_id": "80000000-0000-0000-0000-000000000008",
                "policy_name": "Changed Board Policy",
                "calculated_at": (self.note.prepared_at - timedelta(minutes=1)).isoformat(),
            }
        )
        self.note.save(update_fields=["loan_limit_snapshot_json"])
        before = self._approval_case_business_ledger()

        response = self._enrich_with_token(setup["payload"], setup["token"])

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(response.json()["error"]["code"], "INVALID_STATE_TRANSITION")
        self.assertEqual(self._approval_case_business_ledger(), before)

    def test_enrichment_replay_rejects_changed_review_decision_date(self):
        setup = self._create_real_enriched_case()
        changed_reviewed_at = self.reviewed_at + timedelta(days=1)
        self.note.reviewed_at = changed_reviewed_at
        self.note.save(update_fields=["reviewed_at"])
        AppraisalReviewDecision.objects.filter(pk=self.history.pk).update(
            decided_at=changed_reviewed_at
        )
        before = self._approval_case_business_ledger()

        response = self._enrich_with_token(setup["payload"], setup["token"])

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(response.json()["error"]["code"], "INVALID_STATE_TRANSITION")
        self.assertEqual(self._approval_case_business_ledger(), before)

    def test_enrichment_replay_rejects_changed_exception_provenance(self):
        setup = self._create_real_enriched_case()
        self.note.loan_limit_snapshot_json["exception_required_flag"] = True
        self.note.save(update_fields=["loan_limit_snapshot_json"])
        before = self._approval_case_business_ledger()

        response = self._enrich_with_token(
            setup["payload"] | {"business_reason": "Changed snapshot needs exception."},
            setup["token"],
        )

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(response.json()["error"]["code"], "INVALID_STATE_TRANSITION")
        self.assertEqual(self._approval_case_business_ledger(), before)

    def test_enrichment_replay_rejects_changed_recommended_amount(self):
        setup = self._create_real_enriched_case()
        self.note.recommended_amount = "410000.00"
        self.note.save(update_fields=["recommended_amount"])
        replay_payload = setup["payload"] | {"amount": "410000.00"}
        before = self._approval_case_business_ledger()

        response = self._enrich_with_token(replay_payload, setup["token"])

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(response.json()["error"]["code"], "INVALID_STATE_TRANSITION")
        self.assertEqual(self._approval_case_business_ledger(), before)

    def test_enrichment_replay_rejects_changed_application_provenance(self):
        setup = self._create_real_enriched_case()
        self.note.loan_limit_snapshot_json[
            "loan_application_id"
        ] = "90000000-0000-0000-0000-000000000009"
        self.note.save(update_fields=["loan_limit_snapshot_json"])
        before = self._approval_case_business_ledger()

        response = self._enrich_with_token(setup["payload"], setup["token"])

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(response.json()["error"]["code"], "INVALID_STATE_TRANSITION")
        self.assertEqual(self._approval_case_business_ledger(), before)

    def test_enrichment_list_and_detail_share_the_canonical_routing_projection(self):
        setup = self._create_real_enriched_case()
        headers = {
            "Authorization": f"Bearer {self._login(setup['cfo'])}"
        }

        collection = self.client.get("/api/v1/approval-cases/", headers=headers)
        detail = self.client.get(
            f"/api/v1/approval-cases/{setup['data']['approval_case_id']}/",
            headers=headers,
        )

        self.assertEqual(collection.status_code, 200, collection.content)
        self.assertEqual(detail.status_code, 200, detail.content)
        list_case = collection.json()["data"][0]
        detail_case = detail.json()["data"]
        canonical_fields = (
            "approval_case_id",
            "approval_type",
            "related_entity_type",
            "related_entity_id",
            "loan_application_id",
            "amount",
            "current_status",
            "decision_date",
            "version",
            "approval_matrix_rule_id",
            "approval_matrix_rule_version",
            "sanction_committee_id",
            "sanction_committee_version",
            "excluded_approvers",
            "reason_for_approval",
            "exception_condition_code",
            "matrix_projection",
            "committee_projection",
            "loan_limit_provenance",
        )
        for field in canonical_fields:
            self.assertEqual(list_case[field], setup["data"][field], field)
            self.assertEqual(detail_case[field], setup["data"][field], field)

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
        setup = self._create_real_enriched_case()
        case_model = apps.get_model("approvals", "ApprovalCase")
        case = case_model.objects.get()
        checker = setup["cfo"]
        read_headers = {"Authorization": f"Bearer {self._login(checker)}"}
        canonical_url = f"/api/v1/approval-cases/{case.pk}/"
        canonical_before = self.client.get(canonical_url, headers=read_headers)
        self.assertEqual(canonical_before.status_code, 200, canonical_before.content)
        case_ledger_before = {
            "case": case_model.objects.filter(pk=case.pk).values().get(),
            "actions": list(case.actions.order_by("pk").values()),
            "case_audits": list(
                AuditLog.objects.filter(entity_id=case.pk).order_by("pk").values()
            ),
            "workflows": list(WorkflowEvent.objects.order_by("pk").values()),
        }
        rule = case.approval_matrix_rule
        replacement = {
            "decision_type": "loan_sanction",
            "amount_min": "0.00",
            "amount_max": "500000.00",
            "condition_code": None,
            "required_approver_roles": ["cfo", "director"],
            "required_director_count": 2,
            "joint_approval_required_flag": True,
            "register_required": "credit_sanction_register",
            "effective_from": "2027-01-01",
            "effective_to": None,
            "version_number": "rejected-rule-v2",
            "reason": "Rejected route reason must not enter winner evidence",
        }
        rejected_request = RequestFactory().post(
            "/api/v1/approval-matrix-rules/",
            HTTP_X_REQUEST_ID="rejected-route-request",
        )
        rejected = approval_matrix_configuration.supersede_rule(
            self.reviewer, rejected_request, rule.pk, replacement
        )
        approval_matrix_configuration.decide_proposal(
            rejected["approval_configuration_proposal_id"],
            checker,
            rejected_request,
            {"version": 1, "reason": "Evidence incomplete"},
            "reject",
        )
        approved_request = RequestFactory().post(
            "/api/v1/approval-matrix-rules/",
            HTTP_X_REQUEST_ID="approved-route-request",
        )
        approved = approval_matrix_configuration.supersede_rule(
            self.reviewer,
            approved_request,
            rule.pk,
            replacement
            | {
                "version_number": "approved-rule-v2",
                "reason": "Approved annual route replacement",
            },
        )
        approval_matrix_configuration.decide_proposal(
            approved["approval_configuration_proposal_id"],
            checker,
            approved_request,
            {"version": 1},
            "approve",
        )
        rejected_row = ApprovalConfigurationProposal.objects.get(
            pk=rejected["approval_configuration_proposal_id"]
        )
        approved_row = ApprovalConfigurationProposal.objects.get(
            pk=approved["approval_configuration_proposal_id"]
        )
        activated = ApprovalMatrixRule.objects.get(version_number="approved-rule-v2")
        history = VersionHistory.objects.get(
            versioned_entity_type="approval_matrix_rule",
            versioned_entity_id=activated.pk,
        )
        audit = AuditLog.objects.get(
            action="config.changed",
            entity_type="approval_matrix_rule",
            entity_id=activated.pk,
        )

        self.assertEqual(history.author_user_id, self.reviewer.pk)
        self.assertEqual(history.approver_user_id, checker.pk)
        self.assertNotEqual(history.author_user_id, history.approver_user_id)
        self.assertEqual(history.change_summary, approved_row.reason)
        self.assertEqual(history.approval_reference, "approved-route-request")
        self.assertEqual(history.approved_at, approved_row.decided_at)
        self.assertEqual(history.new_value_json["proposal_id"], str(approved_row.pk))
        self.assertEqual(
            history.new_value_json["target_entity_id"], str(rule.pk)
        )
        self.assertEqual(audit.actor_user_id, checker.pk)
        self.assertEqual(audit.new_value_json["proposal_id"], str(approved_row.pk))
        self.assertEqual(audit.new_value_json["author_user_id"], str(self.reviewer.pk))
        self.assertEqual(audit.new_value_json["approver_user_id"], str(checker.pk))
        self.assertEqual(audit.new_value_json["request_id"], "approved-route-request")
        self.assertEqual(
            audit.new_value_json["superseded_configuration"]["approval_matrix_rule_id"],
            str(rule.pk),
        )
        winner_evidence = str({"history": history.new_value_json, "audit": audit.new_value_json})
        self.assertNotIn(rejected_row.reason, winner_evidence)
        self.assertNotIn(rejected_row.request_id, winner_evidence)
        self.assertNotIn(rejected_row.payload_json["version_number"], winner_evidence)

        self.assertEqual(
            {
                "case": case_model.objects.filter(pk=case.pk).values().get(),
                "actions": list(case.actions.order_by("pk").values()),
                "case_audits": list(
                    AuditLog.objects.filter(entity_id=case.pk).order_by("pk").values()
                ),
                "workflows": list(WorkflowEvent.objects.order_by("pk").values()),
            },
            case_ledger_before,
        )
        canonical_after = self.client.get(canonical_url, headers=read_headers)
        self.assertEqual(canonical_after.status_code, 200, canonical_after.content)
        self.assertEqual(canonical_after.json()["data"], canonical_before.json()["data"])
        self.assertEqual(setup["data"]["approval_case_id"], str(case.pk))

    def _create_scoped_ordinary_terminal_case(self, *, cfo, director):
        decision_date = timezone.localdate()
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
            version_number="scope-matrix-lower-v1",
        )
        committee = SanctionCommittee.objects.create(
            committee_name="Scope Matrix Ordinary Committee",
            cfo_user=cfo,
            director_1_user=director,
            director_2_user=self._user(
                "scope_matrix_reserve_director", "Scope Matrix Reserve Director"
            ),
            board_meeting_reference="BOARD-SCOPE-MATRIX-2",
            effective_from=decision_date,
            status="active",
            version_number="scope-matrix-committee-v1",
        )
        application = LoanApplication.objects.create(
            application_reference_number="LO00000799",
            member=self.member,
            borrower_type=self.member.member_type,
            received_by_user=self.preparer,
            required_loan_amount="400000.00",
            requested_tenure_months=12,
            declared_purpose="Independent ordinary scope row",
            purpose_category="crop_production",
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            application_status=LoanApplication.STATUS_SUBMITTED_TO_SANCTION,
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
            terms_acceptance_flag=True,
            created_by_user=self.preparer,
        )
        risk = RiskAssessment.objects.create(
            loan_application=application,
            market_risk_rating="low",
            operational_risk_rating="low",
            borrower_risk_rating="low",
            overall_risk_rating="low",
            risk_mitigation_notes="Ordinary scoped row.",
            assessed_by_user=self.preparer,
        )
        calculated_at = timezone.now() - timedelta(minutes=1)
        note = LoanAppraisalNote.objects.create(
            loan_application=application,
            prepared_by_user=self.preparer,
            reviewed_by_user=self.reviewer,
            reviewed_at=timezone.now(),
            last_review_decision="reviewed",
            tat_due_at=timezone.now() + timedelta(days=1),
            tat_status=LoanAppraisalNote.TAT_WITHIN,
            eligibility_assessment_id_snapshot="80000000-0000-0000-0000-000000000008",
            loan_limit_assessment_id_snapshot="90000000-0000-0000-0000-000000000009",
            eligibility_snapshot_json={
                "eligibility_assessment_id": "80000000-0000-0000-0000-000000000008",
                "loan_application_id": str(application.pk),
                "member_active_check": "pass",
                "default_check": "pass",
                "document_check": "pass",
                "terms_acceptance_check": "pass",
                "purpose_check": "pass",
                "nominee_check": "pass",
                "overall_result": "eligible",
                "assessment_notes": "Eligible.",
                "active_member_snapshot": {},
                "assessed_by_user_id": str(self.preparer.pk),
                "assessed_at": calculated_at.isoformat(),
            },
            loan_limit_snapshot_json={
                "loan_limit_assessment_id": "90000000-0000-0000-0000-000000000009",
                "loan_application_id": str(application.pk),
                "final_eligible_loan_amount": "500000.00",
                "exception_required_flag": False,
                "calculation_rule_version": "scope-limit-v1",
                "policy_config_id": "30000000-0000-0000-0000-000000000003",
                "policy_name": "Approved ordinary policy",
                "calculated_at": calculated_at.isoformat(),
            },
            prerequisite_provenance="verified",
            borrower_summary="Independent ordinary borrower.",
            eligibility_summary="Eligible.",
            loan_limit_summary="Within limit.",
            recommended_amount="400000.00",
            recommended_tenure_months=12,
            recommended_interest_type="floating",
            recommended_security_summary="Standard member security package.",
            repayment_capacity_notes="Adequate.",
            risk_assessment=risk,
            recommendation="approve",
            appraisal_status=LoanAppraisalNote.STATUS_SUBMITTED_TO_SANCTION,
        )
        review = AppraisalReviewDecision.objects.create(
            loan_appraisal_note=note,
            decision="reviewed",
            review_comments="Immutable ordinary-case review.",
            reviewer_user=self.reviewer,
            decided_at=note.reviewed_at,
            from_state=LoanAppraisalNote.STATUS_REVIEW_PENDING,
            to_state=LoanAppraisalNote.STATUS_REVIEWED,
        )
        case = apps.get_model("approvals", "ApprovalCase").objects.create(
            loan_application=application,
            loan_appraisal_note=note,
            appraisal_review_decision=review,
            submitted_by_user=self.reviewer,
            submission_remarks="Ordinary case ready for scoped approval.",
            approval_matrix_rule=rule,
            approval_matrix_rule_version=rule.version_number,
            sanction_committee=committee,
            sanction_committee_version=committee.version_number,
            required_approvers_json=[
                {"role_code": "cfo", "user_id": str(cfo.pk), "full_name": cfo.full_name},
                {
                    "role_code": "director",
                    "user_id": str(director.pk),
                    "full_name": director.full_name,
                },
            ],
            excluded_approvers_json=[],
            amount="400000.00",
            related_entity_type="loan_application",
            related_entity_id=application.pk,
            reason_for_approval="Ordinary case sanction reason.",
            matrix_projection_json={
                "approval_matrix_rule_id": str(rule.pk),
                "version_number": rule.version_number,
                "decision_type": "loan_sanction",
                "amount": "400000.00",
                "amount_min": "0.00",
                "amount_max": "500000.00",
                "condition_code": None,
                "decision_date": decision_date.isoformat(),
                "required_approver_roles": ["cfo", "director"],
                "required_director_count": 1,
                "joint_approval_required": True,
                "register_required": "credit_sanction_register",
            },
            committee_projection_json={
                "sanction_committee_id": str(committee.pk),
                "version_number": committee.version_number,
                "decision_date": decision_date.isoformat(),
                "cfo_user_id": str(cfo.pk),
                "director_user_ids": [
                    str(director.pk),
                    str(committee.director_2_user_id),
                ],
            },
            loan_limit_provenance_json=note.loan_limit_snapshot_json,
            decision_date=decision_date,
            version=2,
        )
        case = apps.get_model("approvals", "ApprovalCase").objects.select_related(
            "loan_application", "loan_appraisal_note__risk_assessment"
        ).get(pk=case.pk)
        case.appraisal_facts_json = project_approval_case_review_facts(
            application=case.loan_application,
            appraisal_note=case.loan_appraisal_note,
            review=case.appraisal_review_decision,
        )
        case.save(update_fields=["appraisal_facts_json"])
        self.assertTrue(refresh_approval_case_projection(case))
        return case, application

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

    def _enrich_with_token(self, payload, token):
        return self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/approval-cases/",
            data=payload,
            content_type="application/json",
            headers={"Authorization": f"Bearer {token}"},
        )

    def _create_real_enriched_case(self):
        ApprovalMatrixRule.objects.all().delete()
        SanctionCommittee.objects.all().delete()
        create_permission = self._permission(
            "approvals.case.create", "Create approval case"
        )
        RolePermission.objects.create(
            role=self.reviewer.primary_role, permission=create_permission
        )
        read_permission = self._permission(
            "approvals.case.read", "Read approval cases"
        )
        cfo = self._user("replay_cfo", "Replay CFO", read_permission)
        cfo.approval_authority_type = "cfo"
        cfo.save(update_fields=["approval_authority_type"])
        director_1 = self._user("replay_director_1", "Replay Director 1")
        director_1.approval_authority_type = "director"
        director_1.save(update_fields=["approval_authority_type"])
        director_2 = self._user("replay_director_2", "Replay Director 2")
        director_2.approval_authority_type = "director"
        director_2.save(update_fields=["approval_authority_type"])
        decision_date = timezone.localdate(self.history.decided_at)
        ApprovalMatrixRule.objects.create(
            decision_type="loan_sanction",
            amount_min="0.00",
            amount_max="500000.00",
            required_approver_roles_json=["cfo", "director"],
            required_director_count=1,
            joint_approval_required_flag=True,
            register_required="credit_sanction_register",
            effective_from=decision_date,
            status="active",
            version_number="replay-rule-v1",
        )
        SanctionCommittee.objects.create(
            committee_name="Replay Committee",
            cfo_user=cfo,
            director_1_user=director_1,
            director_2_user=director_2,
            board_meeting_reference="BOARD-REPLAY-1",
            effective_from=decision_date,
            status="active",
            version_number="replay-committee-v1",
        )
        provenance = {
            "loan_limit_assessment_id": str(
                self.note.loan_limit_assessment_id_snapshot
            ),
            "loan_application_id": str(self.application.pk),
            "exception_required_flag": False,
            "calculation_rule_version": "replay-limit-v1",
            "policy_config_id": "30000000-0000-0000-0000-000000000003",
            "policy_name": "Replay Board Policy",
            "calculated_at": self.note.prepared_at.isoformat(),
        }
        self.note.loan_limit_snapshot_json = {
            **self.note.loan_limit_snapshot_json,
            **provenance,
        }
        self.note.save(update_fields=["loan_limit_snapshot_json"])
        self.assertEqual(
            self._submit({"remarks": "Create a real replay shell."}).status_code,
            200,
        )
        payload = {
            "approval_type": "sanction",
            "amount": "400000.00",
            "reason_for_approval": "Replay the reviewed appraisal exactly.",
            "force_exception_route": False,
        }
        enriched = self._enrich(payload)
        self.assertEqual(enriched.status_code, 200, enriched.content)
        return {
            "payload": payload,
            "token": self._login(self.reviewer),
            "data": enriched.json()["data"],
            "cfo": cfo,
            "directors": (director_1, director_2),
        }

    @staticmethod
    def _approval_case_business_ledger():
        case_model = apps.get_model("approvals", "ApprovalCase")
        action_model = apps.get_model("approvals", "ApprovalAction")
        return {
            "cases": list(case_model.objects.order_by("pk").values()),
            "actions": list(action_model.objects.order_by("pk").values()),
            "audits": list(
                AuditLog.objects.exclude(action__startswith="auth.")
                .order_by("pk")
                .values()
            ),
            "workflows": list(WorkflowEvent.objects.order_by("pk").values()),
        }

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
    _submit = SanctionSubmissionApiTests._submit
    _enrich = SanctionSubmissionApiTests._enrich
    _login = SanctionSubmissionApiTests._login
    _create_real_enriched_case = SanctionSubmissionApiTests._create_real_enriched_case

    def test_concurrent_returned_cycle_resubmissions_create_one_cycle_two_ledger(self):
        from sfpcl_credit.approvals.models import ApprovalCase
        from sfpcl_credit.approvals.modules import approval_actions
        from sfpcl_credit.approvals.modules.sanction_handoff import SanctionHandoffModule
        from sfpcl_credit.credit.modules.appraisal_workflow import (
            AppraisalWorkflow,
            CreditModuleInvalidStateError,
        )

        setup = self._create_real_enriched_case()
        cycle_one = ApprovalCase.objects.get(pk=setup["data"]["approval_case_id"])
        approval_actions.return_case(
            actor=setup["cfo"],
            case_id=cycle_one.pk,
            payload={"version": 2, "comments": "Correct and resubmit."},
            actor_permissions={"approvals.case.read", "approvals.case.return"},
        )
        cycle_one.refresh_from_db()
        cycle_one_before = ApprovalCase.objects.filter(pk=cycle_one.pk).values().get()
        cycle_one_actions_before = list(cycle_one.actions.order_by("pk").values())

        AppraisalWorkflow().create_or_update(
            actor=self.preparer,
            application_id=self.application.pk,
            payload={"borrower_summary": "Corrected concurrent-resubmission facts."},
            partial=True,
            actor_permissions={"credit.appraisal.update"},
        )
        AppraisalWorkflow().submit_for_review(
            actor=self.preparer,
            appraisal_id=self.note.pk,
            payload={"remarks": "Corrected facts ready."},
            actor_permissions={"credit.appraisal.submit_review"},
        )
        AppraisalWorkflow().review(
            actor=self.reviewer,
            appraisal_id=self.note.pk,
            decision="reviewed",
            comments="Fresh independent review for cycle two.",
            payload_fields={
                "decision": "reviewed",
                "review_comments": "Fresh independent review for cycle two.",
            },
            actor_permissions={"credit.appraisal.review"},
        )

        winner_reached_create = Event()
        release_winner = Event()
        original_create = ApprovalCase.objects.create

        def coordinated_create(**kwargs):
            winner_reached_create.set()
            if not release_winner.wait(timeout=10):
                raise AssertionError("Timed out releasing cycle-two submission.")
            return original_create(**kwargs)

        def resubmit(request_id):
            close_old_connections()
            try:
                actor = User.objects.get(pk=self.reviewer.pk)
                return SanctionHandoffModule().submit_reviewed_appraisal(
                    actor=actor,
                    application_id=self.application.pk,
                    payload={"remarks": f"Concurrent resubmission {request_id}."},
                    request_meta={"request_id": request_id},
                ).snapshot
            finally:
                connections["default"].close()

        with patch.object(ApprovalCase.objects, "create", side_effect=coordinated_create):
            with ThreadPoolExecutor(max_workers=2) as executor:
                winner_future = executor.submit(resubmit, "winner")
                self.assertTrue(winner_reached_create.wait(timeout=10))
                loser_future = executor.submit(resubmit, "loser")
                try:
                    self.assertFalse(loser_future.done())
                finally:
                    release_winner.set()
                winner = winner_future.result(timeout=10)
                with self.assertRaises(CreditModuleInvalidStateError):
                    loser_future.result(timeout=10)

        cases = list(ApprovalCase.objects.order_by("cycle_number"))
        self.assertEqual([case.cycle_number for case in cases], [1, 2])
        self.assertEqual(winner["approval_case_id"], str(cases[1].pk))
        self.assertEqual(
            AuditLog.objects.filter(action="appraisal.submitted_to_sanction").count(),
            2,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="sanction_submission").count(),
            2,
        )
        self.assertEqual(
            ApprovalCase.objects.filter(pk=cycle_one.pk).values().get(),
            cycle_one_before,
        )
        self.assertEqual(
            list(cycle_one.actions.order_by("pk").values()), cycle_one_actions_before
        )


@skipUnless(
    connection.vendor == "postgresql",
    "Authoritative sanction-submission concurrency proof requires PostgreSQL.",
)
class InitialSanctionSubmissionConcurrencyTests(TransactionTestCase):
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
