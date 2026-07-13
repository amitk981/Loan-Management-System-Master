from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
import ast
import inspect
import tempfile
from unittest import skipUnless
from unittest.mock import patch

from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, close_old_connections, connection, connections, transaction
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import (
    ApprovalAction,
    ApprovalCase,
    ExceptionRegisterEntry,
    ApprovalCaseRequiredApprover,
    ApprovalCaseReadScopeGrant,
    ApprovalConflictDeclaration,
    ApprovalMatrixRule,
    SanctionCommittee,
)
from sfpcl_credit.approvals.modules.approval_case_selector import (
    select_approval_case_candidates,
)
from sfpcl_credit.approvals.modules import (
    approval_actions,
    approval_case_engine,
    approval_case_selector,
    exception_register,
    sanction_register,
)
from sfpcl_credit.approvals.modules.conflict_of_interest import ConflictOfInterestModule
from sfpcl_credit.approvals.modules.approval_case_projection import (
    refresh_approval_case_projection,
)
from sfpcl_credit.approvals.modules.sanction_handoff import SanctionHandoffModule
from sfpcl_credit.credit.models import (
    AppraisalReviewDecision,
    LoanAppraisalNote,
    RiskAssessment,
)
from sfpcl_credit.credit.modules.appraisal_workflow import AppraisalWorkflow
from sfpcl_credit.credit.modules.appraisal_workflow import (
    project_approval_case_review_facts,
)
from sfpcl_credit.domain_errors import DomainInvalidStateError
from sfpcl_credit.communications.models import Communication, Notification
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.identity.modules.auth_service import effective_permission_codes
from sfpcl_credit.members.models import Member
from sfpcl_credit.tests.api_contracts import (
    assert_available_actions_shape,
    assert_error_envelope,
    assert_pagination_shape,
    assert_success_envelope,
)
from sfpcl_credit.workflows.models import WorkflowEvent


def _project_review_facts(case):
    return project_approval_case_review_facts(
        application=case.loan_application,
        appraisal_note=case.loan_appraisal_note,
        review=case.appraisal_review_decision,
    )


@override_settings(DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-gm-doc-tests-"))
class ApprovalCaseRoutingApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.read_permission = self._permission("approvals.case.read")
        self.application_read_permission = self._permission(
            "applications.loan_application.read"
        )
        self.approve_permission = self._permission("approvals.case.approve")
        self.reject_permission = self._permission("approvals.case.reject")
        self.return_permission = self._permission("approvals.case.return")
        self.cfo = self._user(
            "cfo",
            "Snapshot CFO",
            self.read_permission,
            self.approve_permission,
            self.reject_permission,
            self.return_permission,
        )
        self.director = self._user(
            "director",
            "Snapshot Director",
            self.read_permission,
            self.approve_permission,
            self.reject_permission,
            self.return_permission,
        )
        self.preparer = self._user("deputy_manager_finance", "Case Preparer")
        self.member = Member.objects.create(
            member_number="MEM-APPROVAL-QUEUE-001",
            member_type="individual_farmer",
            legal_name="Approval Queue Member",
            display_name="Approval Queue Member",
            membership_status="active",
            folio_number="FOL-APPROVAL-QUEUE-001",
            kyc_status="verified",
            default_status="no_default",
        )
        self.application = LoanApplication.objects.create(
            application_reference_number="LO00000701",
            member=self.member,
            borrower_type=self.member.member_type,
            received_by_user=self.preparer,
            required_loan_amount="500000.00",
            requested_tenure_months=12,
            declared_purpose="Crop production",
            purpose_category="crop_production",
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            application_status=LoanApplication.STATUS_SUBMITTED_TO_SANCTION,
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
            risk_mitigation_notes="Seasonal cash-flow monitoring.",
            assessed_by_user=self.preparer,
        )
        calculated_at = timezone.now() - timedelta(hours=1)
        self.note = LoanAppraisalNote.objects.create(
            loan_application=self.application,
            prepared_by_user=self.preparer,
            reviewed_by_user=self.preparer,
            reviewed_at=timezone.now(),
            last_review_decision="reviewed",
            tat_due_at=timezone.now() + timedelta(days=1),
            tat_status=LoanAppraisalNote.TAT_WITHIN,
            eligibility_assessment_id_snapshot="10000000-0000-0000-0000-000000000001",
            loan_limit_assessment_id_snapshot="20000000-0000-0000-0000-000000000002",
            eligibility_snapshot_json={
                "eligibility_assessment_id": "10000000-0000-0000-0000-000000000001",
                "loan_application_id": str(self.application.pk),
                "overall_result": "eligible",
                "member_active_check": "pass",
                "default_check": "pass",
                "document_check": "pass",
                "terms_acceptance_check": "pass",
                "purpose_check": "pass",
                "nominee_check": "pass",
                "assessment_notes": "Eligible for appraisal.",
                "active_member_snapshot": {},
                "assessed_by_user_id": str(self.preparer.pk),
                "assessed_at": calculated_at.isoformat(),
            },
            loan_limit_snapshot_json={
                "loan_limit_assessment_id": "20000000-0000-0000-0000-000000000002",
                "loan_application_id": str(self.application.pk),
                "final_eligible_loan_amount": "500000.00",
                "exception_required_flag": False,
                "calculation_rule_version": "limit-v7",
                "policy_config_id": "30000000-0000-0000-0000-000000000003",
                "policy_name": "Board Loan Policy",
                "calculated_at": calculated_at.isoformat(),
            },
            prerequisite_provenance="verified",
            borrower_summary="No prior SFPCL borrowing.",
            eligibility_summary="All eligibility checks passed.",
            loan_limit_summary="Recommended amount is within the verified limit.",
            recommended_amount="500000.00",
            recommended_tenure_months=12,
            recommended_interest_type="floating",
            recommended_security_summary="Standard member security package.",
            repayment_capacity_notes="Projected proceeds cover instalments.",
            risk_assessment=self.risk,
            recommendation="approve",
            appraisal_status=LoanAppraisalNote.STATUS_SUBMITTED_TO_SANCTION,
        )
        self.review = AppraisalReviewDecision.objects.create(
            loan_appraisal_note=self.note,
            decision="reviewed",
            review_comments="Initial immutable review.",
            reviewer_user=self.preparer,
            decided_at=self.note.reviewed_at,
            from_state=LoanAppraisalNote.STATUS_REVIEW_PENDING,
            to_state=LoanAppraisalNote.STATUS_REVIEWED,
        )
        decision_date = timezone.localdate()
        self.rule = ApprovalMatrixRule.objects.create(
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
        self.committee = SanctionCommittee.objects.create(
            committee_name="Historical Committee",
            cfo_user=self.cfo,
            director_1_user=self.director,
            director_2_user=self._user("director_2", "Second Director"),
            board_meeting_reference="BM-2026-07",
            effective_from=decision_date,
            status="active",
            version_number="committee-v1",
        )
        self.case = ApprovalCase.objects.create(
            loan_application=self.application,
            loan_appraisal_note=self.note,
            appraisal_review_decision=self.review,
            submitted_by_user=self.preparer,
            submission_remarks="Ready for sanction review.",
            approval_matrix_rule=self.rule,
            approval_matrix_rule_version=self.rule.version_number,
            sanction_committee=self.committee,
            sanction_committee_version=self.committee.version_number,
            required_approvers_json=[
                {"role_code": "cfo", "user_id": str(self.cfo.pk), "full_name": self.cfo.full_name},
                {
                    "role_code": "director",
                    "user_id": str(self.director.pk),
                    "full_name": self.director.full_name,
                },
            ],
            excluded_approvers_json=[],
            amount="500000.00",
            related_entity_type="loan_application",
            related_entity_id=self.application.pk,
            reason_for_approval="Reviewed appraisal recommends approval.",
            matrix_projection_json={
                "approval_matrix_rule_id": str(self.rule.pk),
                "version_number": self.rule.version_number,
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
            committee_projection_json={
                "sanction_committee_id": str(self.committee.pk),
                "version_number": self.committee.version_number,
                "decision_date": decision_date.isoformat(),
                "cfo_user_id": str(self.cfo.pk),
                "director_user_ids": [
                    str(self.director.pk),
                    str(self.committee.director_2_user_id),
                ],
            },
            loan_limit_provenance_json={
                "loan_limit_assessment_id": str(self.note.loan_limit_assessment_id_snapshot),
                "loan_application_id": str(self.application.pk),
                "final_eligible_loan_amount": "500000.00",
                "exception_required_flag": False,
                "calculation_rule_version": "limit-v7",
                "policy_config_id": "30000000-0000-0000-0000-000000000003",
                "policy_name": "Board Loan Policy",
                "calculated_at": calculated_at.isoformat(),
            },
            decision_date=decision_date,
            version=2,
        )
        self.case = ApprovalCase.objects.select_related(
            "loan_application", "loan_appraisal_note__risk_assessment"
        ).get(pk=self.case.pk)
        self.case.appraisal_facts_json = _project_review_facts(self.case)
        self.case.save(update_fields=["appraisal_facts_json"])
        refresh_approval_case_projection(self.case)

    def test_assigned_to_me_returns_the_pending_snapshotted_case(self):
        response = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true",
            **self._auth(self.cfo),
        )

        self.assertEqual(response.status_code, 200, response.json())
        body = response.json()
        assert_pagination_shape(self, body)
        self.assertEqual(
            [item["approval_case_id"] for item in body["data"]],
            [str(self.case.pk)],
        )
        self.assertEqual(body["pagination"]["total_count"], 1)

    def test_conflict_module_uses_frozen_cycle_maker_facts(self):
        self.application.created_by_user = self.cfo
        self.application.save(update_fields=["created_by_user"])
        self.case.refresh_from_db()
        frozen_facts = {
            **_project_review_facts(self.case),
            "maker_checker": {
                "application_created_by_user_id": str(self.cfo.pk),
                "application_received_by_user_id": str(self.preparer.pk),
                "application_submitted_by_user_id": None,
                "appraisal_prepared_by_user_id": str(self.preparer.pk),
                "appraisal_reviewed_by_user_id": str(self.preparer.pk),
            },
        }
        self.case.appraisal_facts_json = frozen_facts
        self.case.save(update_fields=["appraisal_facts_json"])
        self.application.created_by_user = self.preparer
        self.application.save(update_fields=["created_by_user"])

        assessment = ConflictOfInterestModule().evaluate_for_case(self.case)

        self.assertEqual(
            assessment.exclusions,
            (
                {
                    "user_id": str(self.cfo.pk),
                    "conflict_code": "own_application",
                    "reason": "User created the loan application.",
                },
            ),
        )

    def test_conflict_module_maps_declared_relationship_and_interest_facts(self):
        for conflict_type, actor, reason in (
            ("borrower", self.cfo, "Committee member is the borrower."),
            ("director_relative", self.director, "Borrower is relative of Director."),
            (
                "material_interest",
                self.committee.director_2_user,
                "Committee member declared a material interest.",
            ),
        ):
            ApprovalConflictDeclaration.objects.create(
                loan_application=self.application,
                user=actor,
                conflict_type=conflict_type,
                reason=reason,
                declared_by_user=self.preparer,
            )

        assessment = ConflictOfInterestModule().evaluate_for_case(self.case)

        self.assertEqual(
            {item["conflict_code"] for item in assessment.exclusions},
            {"borrower", "director_relative", "material_interest"},
        )
        self.assertTrue(assessment.general_meeting_evidence_required)

    def test_enrichment_freezes_exclusions_without_rewriting_authority_snapshot(self):
        review = self.review
        ApprovalConflictDeclaration.objects.create(
            loan_application=self.application,
            user=self.director,
            conflict_type="director_relative",
            reason="Borrower is relative of Director.",
            declared_by_user=self.preparer,
        )
        self.case.approval_matrix_rule = None
        self.case.approval_matrix_rule_version = ""
        self.case.sanction_committee = None
        self.case.sanction_committee_version = ""
        self.case.required_approvers_json = {}
        self.case.excluded_approvers_json = []
        self.case.amount = None
        self.case.related_entity_type = ""
        self.case.related_entity_id = None
        self.case.reason_for_approval = ""
        self.case.matrix_projection_json = {}
        self.case.committee_projection_json = {}
        self.case.loan_limit_provenance_json = {}
        self.case.appraisal_facts_json = {}
        self.case.decision_date = None
        self.case.appraisal_review_decision = review
        self.case.version = 1
        self.case.save()
        ApprovalMatrixRule.objects.exclude(pk=self.rule.pk).update(status="inactive")
        SanctionCommittee.objects.exclude(pk=self.committee.pk).update(status="inactive")

        snapshot = SanctionHandoffModule().enrich_pending(
            actor=self.preparer,
            application_id=self.application.pk,
            payload={
                "approval_type": "sanction",
                "amount": "500000.00",
                "reason_for_approval": "Reviewed appraisal recommends approval.",
                "force_exception_route": False,
            },
            actor_permissions={"approvals.case.create"},
        ).snapshot

        self.case.refresh_from_db()
        self.assertEqual(
            self.case.required_approvers_json,
            [
                {"role_code": "cfo", "user_id": str(self.cfo.pk), "full_name": self.cfo.full_name},
                {
                    "role_code": "director",
                    "user_id": str(self.director.pk),
                    "full_name": self.director.full_name,
                },
            ],
        )
        self.assertEqual(
            self.case.excluded_approvers_json,
            [
                {
                    "user_id": str(self.director.pk),
                    "conflict_code": "director_relative",
                    "reason": "Borrower is relative of Director.",
                }
            ],
        )
        self.assertTrue(snapshot["general_meeting_evidence_required"])
        self.assertEqual(
            self.case.appraisal_facts_json["maker_checker"]["appraisal_prepared_by_user_id"],
            str(self.preparer.pk),
        )

    def test_conflicted_approval_returns_exact_source_error_and_denial_audit(self):
        reason = "Borrower is relative of Director."
        self.case.excluded_approvers_json = [
            {
                "user_id": str(self.director.pk),
                "conflict_code": "director_relative",
                "reason": reason,
            }
        ]
        self.case.general_meeting_evidence_required = True
        self.case.save(
            update_fields=[
                "excluded_approvers_json",
                "general_meeting_evidence_required",
            ]
        )
        case_before = ApprovalCase.objects.filter(pk=self.case.pk).values().get()

        response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2, "comments": "Conflicted attempt."},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-conflict-denial",
            HTTP_USER_AGENT="Conflict Contract Test",
            REMOTE_ADDR="203.0.113.27",
            **self._auth(self.director),
        )

        self.assertEqual(response.status_code, 409, response.json())
        assert_error_envelope(self, response.json(), "CONFLICTED_APPROVER_NOT_ALLOWED")
        self.assertEqual(
            response.json()["error"],
            {
                "code": "CONFLICTED_APPROVER_NOT_ALLOWED",
                "message": "This user is marked as conflicted for the approval case and cannot approve it.",
                "details": {
                    "approval_case_id": str(self.case.pk),
                    "conflict_reason": reason,
                },
                "field_errors": {},
            },
        )
        self.assertEqual(ApprovalCase.objects.filter(pk=self.case.pk).values().get(), case_before)
        self.assertFalse(ApprovalAction.objects.filter(approval_case=self.case).exists())
        denial = AuditLog.objects.get(
            action="approval_case.conflicted_action_denied", entity_id=self.case.pk
        )
        self.assertEqual(denial.actor_user, self.director)
        self.assertEqual(denial.ip_address, "203.0.113.27")
        self.assertEqual(denial.user_agent, "Conflict Contract Test")
        self.assertEqual(
            denial.new_value_json,
            {
                "approval_case_id": str(self.case.pk),
                "cycle_number": 1,
                "attempted_action": "approve",
                "conflict_reason": reason,
                "request_id": "req-conflict-denial",
            },
        )

    def test_every_conflicted_write_path_uses_one_exact_denial_contract(self):
        reason = "Committee member declared a material interest."
        self.case.excluded_approvers_json = [
            {
                "user_id": str(self.director.pk),
                "conflict_code": "material_interest",
                "reason": reason,
            }
        ]
        self.case.save(update_fields=["excluded_approvers_json"])
        for path, action_code in (
            ("approve", "approve"),
            ("reject", "reject"),
            ("return-for-clarification", "return"),
        ):
            with self.subTest(path=path):
                response = self.client.post(
                    f"/api/v1/approval-cases/{self.case.pk}/{path}/",
                    {"version": 2, "comments": "Denied conflict attempt."},
                    content_type="application/json",
                    **self._auth(self.director),
                )
                self.assertEqual(response.status_code, 409)
                assert_error_envelope(
                    self, response.json(), "CONFLICTED_APPROVER_NOT_ALLOWED"
                )
                self.assertEqual(
                    response.json()["error"]["details"]["conflict_reason"], reason
                )
                self.assertTrue(
                    AuditLog.objects.filter(
                        action="approval_case.conflicted_action_denied",
                        entity_id=self.case.pk,
                        new_value_json__attempted_action=action_code,
                    ).exists()
                )
        self.assertFalse(ApprovalAction.objects.filter(approval_case=self.case).exists())
        self.case.refresh_from_db()
        self.assertEqual(self.case.current_status, ApprovalCase.STATUS_PENDING)
        self.assertEqual(self.case.version, 2)

    def test_frozen_alternate_director_satisfies_original_role_count_after_exclusion(self):
        alternate = self.committee.director_2_user
        for permission in (
            self.read_permission,
            self.approve_permission,
            self.reject_permission,
            self.return_permission,
        ):
            RolePermission.objects.create(role=alternate.primary_role, permission=permission)
        self.case.excluded_approvers_json = [
            {
                "user_id": str(self.director.pk),
                "conflict_code": "director_relative",
                "reason": "Borrower is relative of Director.",
            }
        ]
        self.case.save(update_fields=["excluded_approvers_json"])
        refresh_approval_case_projection(self.case)

        queue = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true", **self._auth(alternate)
        )
        cfo = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2}, content_type="application/json", **self._auth(self.cfo),
        )
        final = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 3}, content_type="application/json", **self._auth(alternate),
        )

        self.assertEqual(queue.status_code, 200)
        self.assertEqual(queue.json()["pagination"]["total_count"], 1)
        self.assertEqual(cfo.status_code, 200, cfo.json())
        self.assertEqual(final.status_code, 200, final.json())
        self.assertEqual(final.json()["data"]["current_status"], "approved")
        self.assertTrue(final.json()["data"]["sanction_decision_created"])
        self.assertEqual(
            ApprovalAction.objects.get(
                approval_case=self.case, approver_user=alternate
            ).approver_role_code,
            "director",
        )

    def test_two_director_route_never_reuses_remaining_director(self):
        alternate = self.committee.director_2_user
        self.case.required_approvers_json = [
            *self.case.required_approvers_json,
            {
                "role_code": "director",
                "user_id": str(alternate.pk),
                "full_name": alternate.full_name,
            },
        ]
        self.case.matrix_projection_json = {
            **self.case.matrix_projection_json,
            "required_director_count": 2,
        }
        self.case.excluded_approvers_json = [
            {
                "user_id": str(self.director.pk),
                "conflict_code": "director_relative",
                "reason": "Borrower is relative of Director 1.",
            }
        ]

        effective = ConflictOfInterestModule.effective_approvers(self.case)

        self.assertEqual(
            [(item["role_code"], item["user_id"]) for item in effective],
            [("cfo", str(self.cfo.pk)), ("director", str(alternate.pk))],
        )
        self.assertEqual(len({item["user_id"] for item in effective}), 2)
        self.assertFalse(ConflictOfInterestModule.authority_is_satisfiable(self.case))
        self.assertEqual(
            ConflictOfInterestModule.authority_gap_reason(self.case),
            "Required Director approval authority is unavailable after conflict exclusion.",
        )

    def test_public_enrichment_blocks_when_first_of_two_directors_is_excluded(self):
        self._assert_public_two_director_conflict_block(self.director)

    def test_public_enrichment_blocks_when_second_of_two_directors_is_excluded(self):
        self._assert_public_two_director_conflict_block(
            self.committee.director_2_user
        )

    def test_alternate_action_is_canonical_without_rewriting_route_provenance(self):
        alternate = self.committee.director_2_user
        for permission in (
            self.read_permission,
            self.approve_permission,
            self.reject_permission,
            self.return_permission,
        ):
            RolePermission.objects.create(role=alternate.primary_role, permission=permission)
        immutable_route = list(self.case.required_approvers_json)
        self.case.excluded_approvers_json = [
            {
                "user_id": str(self.director.pk),
                "conflict_code": "director_relative",
                "reason": "Borrower is relative of Director.",
            }
        ]
        self.case.save(update_fields=["excluded_approvers_json"])

        first = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2},
            content_type="application/json",
            **self._auth(self.cfo),
        )
        final = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 3},
            content_type="application/json",
            **self._auth(alternate),
        )
        detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **self._auth(alternate)
        )
        collection = self.client.get(
            "/api/v1/approval-cases/", **self._auth(alternate)
        )

        self.assertEqual(first.status_code, 200, first.json())
        self.assertEqual(final.status_code, 200, final.json())
        self.assertEqual(detail.status_code, 200, detail.json())
        self.assertEqual(collection.status_code, 200, collection.json())
        action_facts = {
            key: final.json()["data"][key]
            for key in ("route_approvers", "required_approvers", "approval_actions")
        }
        self.assertEqual(
            {key: detail.json()["data"][key] for key in action_facts}, action_facts
        )
        self.assertEqual(
            {key: collection.json()["data"][0][key] for key in action_facts},
            action_facts,
        )
        alternate_row = next(
            item
            for item in action_facts["required_approvers"]
            if item["user_id"] == str(alternate.pk)
        )
        self.assertEqual(alternate_row["decision"], "approved")
        self.assertEqual(alternate_row["replacement_for_user_id"], str(self.director.pk))
        self.assertEqual(
            {item["user_id"] for item in action_facts["approval_actions"]},
            {str(self.cfo.pk), str(alternate.pk)},
        )
        self.case.refresh_from_db()
        self.assertEqual(self.case.required_approvers_json, immutable_route)
        self.assertEqual(action_facts["route_approvers"], immutable_route)

    def test_unused_committee_alternate_is_nondisclosed_before_pagination(self):
        unused_alternate = self.committee.director_2_user
        RolePermission.objects.create(
            role=unused_alternate.primary_role, permission=self.read_permission
        )
        headers = self._auth(unused_alternate)

        for declared in (False, True):
            with self.subTest(declared=declared):
                if declared:
                    ApprovalConflictDeclaration.objects.create(
                        loan_application=self.application,
                        user=unused_alternate,
                        conflict_type="material_interest",
                        reason="Unused committee alternate declared an interest.",
                        declared_by_user=self.preparer,
                    )
                    self.case.excluded_approvers_json = [
                        {
                            "user_id": str(unused_alternate.pk),
                            "conflict_code": "material_interest",
                            "reason": "Unused committee alternate declared an interest.",
                        }
                    ]
                    self.case.save(update_fields=["excluded_approvers_json"])
                ordinary = self.client.get("/api/v1/approval-cases/", **headers)
                assigned = self.client.get(
                    "/api/v1/approval-cases/?assigned_to_me=true", **headers
                )
                detail = self.client.get(
                    f"/api/v1/approval-cases/{self.case.pk}/", **headers
                )
                action = self.client.post(
                    f"/api/v1/approval-cases/{self.case.pk}/approve/",
                    {"version": 2},
                    content_type="application/json",
                    **headers,
                )

                self.assertEqual(ordinary.status_code, 200, ordinary.json())
                self.assertEqual(ordinary.json()["data"], [])
                self.assertEqual(ordinary.json()["pagination"]["total_count"], 0)
                self.assertEqual(assigned.json()["pagination"]["total_count"], 0)
                self.assertEqual(detail.status_code, 403, detail.json())
                self.assertEqual(detail.json()["error"]["code"], "OBJECT_ACCESS_DENIED")
                self.assertEqual(action.status_code, 403, action.json())
                self.assertEqual(action.json()["error"]["code"], "OBJECT_ACCESS_DENIED")
                self.assertFalse(
                    ApprovalAction.objects.filter(approval_case=self.case).exists()
                )

        RolePermission.objects.filter(
            role=unused_alternate.primary_role, permission=self.read_permission
        ).delete()
        removed_list = self.client.get("/api/v1/approval-cases/", **headers)
        removed_detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **headers
        )
        removed_action = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2},
            content_type="application/json",
            **headers,
        )
        self.assertEqual(removed_list.status_code, 403, removed_list.json())
        self.assertEqual(removed_detail.status_code, 403, removed_detail.json())
        self.assertEqual(removed_action.status_code, 403, removed_action.json())
        self.assertFalse(ApprovalAction.objects.filter(approval_case=self.case).exists())

    def test_noncommittee_related_director_sets_general_meeting_flag_only(self):
        noncommittee_director = self._user(
            "noncommittee_director", "Noncommittee Related Director"
        )
        ApprovalConflictDeclaration.objects.create(
            loan_application=self.application,
            user=noncommittee_director,
            conflict_type="director_relative",
            reason="Borrower is a relative of a Director outside this committee.",
            declared_by_user=self.preparer,
        )

        assessment = ConflictOfInterestModule().evaluate_for_case(self.case)

        self.assertTrue(assessment.general_meeting_evidence_required)
        self.assertEqual(assessment.exclusions, ())

    def test_public_committee_borrower_conflict_matrix(self):
        self._assert_public_conflict_class(
            actor=self.director,
            conflict_type="borrower",
            expected_code="borrower",
            expected_general_meeting=True,
        )

    def test_public_director_relative_conflict_matrix(self):
        self._assert_public_conflict_class(
            actor=self.director,
            conflict_type="director_relative",
            expected_code="director_relative",
            expected_general_meeting=True,
        )

    def test_public_material_interest_conflict_matrix(self):
        self._assert_public_conflict_class(
            actor=self.director,
            conflict_type="material_interest",
            expected_code="material_interest",
            expected_general_meeting=False,
        )

    def test_public_own_application_conflict_matrix(self):
        self._assert_public_conflict_class(
            actor=self.cfo,
            source_fact="application_created_by_user",
            expected_code="own_application",
            expected_general_meeting=False,
        )

    def test_public_maker_checker_conflict_matrix(self):
        self._assert_public_conflict_class(
            actor=self.director,
            source_fact="appraisal_prepared_by_user",
            expected_code="maker_checker",
            expected_general_meeting=False,
        )

    def test_conflict_declaration_rejects_whitespace_only_reason(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            ApprovalConflictDeclaration.objects.create(
                loan_application=self.application,
                user=self.director,
                conflict_type="director_relative",
                reason="  \t  ",
                declared_by_user=self.preparer,
            )

        self.assertFalse(
            ApprovalConflictDeclaration.objects.filter(
                loan_application=self.application,
                user=self.director,
            ).exists()
        )

    def test_plain_model_save_does_not_hide_projection_mutation(self):
        projection_before = set(
            ApprovalCaseRequiredApprover.objects.filter(
                approval_case=self.case
            ).values_list("user_id", flat=True)
        )
        coherence_before = self.case.routing_snapshot_is_coherent
        injected = self._user("projection_injected", "Projection Injected User")
        self.case.required_approvers_json = [
            self.case.required_approvers_json[0],
            {
                "role_code": "director",
                "user_id": str(injected.pk),
                "full_name": injected.full_name,
            },
        ]

        self.case.save(update_fields=["required_approvers_json"])

        self.case.refresh_from_db()
        self.assertEqual(self.case.routing_snapshot_is_coherent, coherence_before)
        self.assertEqual(
            set(
                ApprovalCaseRequiredApprover.objects.filter(
                    approval_case=self.case
                ).values_list("user_id", flat=True)
            ),
            projection_before,
        )

    def test_live_appraisal_policy_change_preserves_pending_case_reads_and_action(self):
        projection_before = list(
            ApprovalCaseRequiredApprover.objects.filter(
                approval_case=self.case
            ).order_by("pk").values()
        )
        self.case.refresh_from_db()
        self.assertTrue(self.case.routing_snapshot_is_coherent)
        frozen_provenance = dict(self.case.loan_limit_provenance_json)
        frozen_appraisal_facts = dict(self.case.appraisal_facts_json)
        headers = self._auth(self.cfo)
        detail_before = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **headers
        )
        queue_before = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true", **headers
        )
        self.assertEqual(detail_before.status_code, 200, detail_before.json())
        self.assertEqual(queue_before.json()["pagination"]["total_count"], 1)
        snapshot = dict(self.note.loan_limit_snapshot_json)
        snapshot["policy_name"] = "Later live policy must not rewrite this cycle"
        self.note.loan_limit_snapshot_json = snapshot

        self.note.save(update_fields=["loan_limit_snapshot_json"])

        detail_after = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **headers
        )
        queue_after = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true", **headers
        )
        self.assertEqual(detail_after.status_code, 200, detail_after.json())
        self.assertEqual(detail_after.json()["data"], detail_before.json()["data"])
        self.assertEqual(queue_after.json()["data"], queue_before.json()["data"])
        self.assertEqual(
            queue_after.json()["pagination"], queue_before.json()["pagination"]
        )
        approved = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2},
            content_type="application/json",
            **headers,
        )
        self.assertEqual(approved.status_code, 200, approved.json())
        self.assertEqual(approved.json()["data"]["decision"], "approved")
        self.case.refresh_from_db()
        self.assertTrue(self.case.routing_snapshot_is_coherent)
        self.assertEqual(self.case.loan_limit_provenance_json, frozen_provenance)
        self.assertEqual(self.case.appraisal_facts_json, frozen_appraisal_facts)
        self.assertEqual(
            list(
                ApprovalCaseRequiredApprover.objects.filter(
                    approval_case=self.case
                ).order_by("pk").values()
            ),
            projection_before,
        )

    def test_conflict_abstention_uses_immutable_action_and_assigns_frozen_alternate(self):
        alternate = self.committee.director_2_user
        for permission in (
            self.read_permission,
            self.approve_permission,
            self.reject_permission,
            self.return_permission,
        ):
            RolePermission.objects.create(role=alternate.primary_role, permission=permission)

        abstention = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/abstain/",
            {"version": 2, "comments": "Borrower is my relative."},
            content_type="application/json",
            **self._auth(self.director),
        )

        self.assertEqual(abstention.status_code, 200, abstention.json())
        self.assertEqual(abstention.json()["data"]["decision"], "abstained")
        self.assertEqual(abstention.json()["data"]["current_status"], "pending")
        self.assertEqual(abstention.json()["data"]["version"], 3)
        self.case.refresh_from_db()
        self.assertEqual(
            self.case.excluded_approvers_json,
            [
                {
                    "user_id": str(self.director.pk),
                    "conflict_code": "self_declared_abstention",
                    "reason": "Borrower is my relative.",
                }
            ],
        )
        action = ApprovalAction.objects.get(
            approval_case=self.case, approver_user=self.director
        )
        self.assertEqual(action.decision, "abstained")
        queue = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true", **self._auth(alternate)
        )
        self.assertEqual(queue.json()["pagination"]["total_count"], 1)

    def test_unsatisfiable_abstention_blocks_case_without_creating_sanction(self):
        recorder, payload = self._general_meeting_recorder_and_payload()
        meeting = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/general-meeting-approval/",
            {**payload, "approval_status": "pending"},
            content_type="application/json",
            **self._auth(recorder),
        )
        self.assertEqual(meeting.status_code, 200, meeting.content)
        entry = ExceptionRegisterEntry.objects.create(
            loan_application=self.application,
            exception_type="waiver",
            description="A governed policy requirement was waived.",
            business_reason="Exception requires conflict-safe authority.",
            approval_case=self.case,
        )
        response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/abstain/",
            {"version": 2, "comments": "I have a material interest."},
            content_type="application/json",
            **self._auth(self.cfo),
        )

        self.assertEqual(response.status_code, 200, response.json())
        data = response.json()["data"]
        self.assertEqual(data["decision"], "abstained")
        self.assertEqual(data["current_status"], "blocked_by_conflict")
        self.assertEqual(
            data["general_meeting_approval"],
            {**meeting.json()["data"], "evidence_scope": "cycle_frozen"},
        )
        self.assertEqual(
            data["conflict_block_reason"],
            "Required CFO approval authority is unavailable after conflict exclusion.",
        )
        self.case.refresh_from_db()
        self.assertEqual(self.case.current_status, "blocked_by_conflict")
        self.assertIsNotNone(self.case.closed_at)
        entry.refresh_from_db()
        self.assertEqual(entry.status, "pending")
        self.assertEqual(entry.closed_at, self.case.closed_at)
        self.assertFalse(
            apps.get_model("approvals", "SanctionDecision").objects.filter(
                approval_case=self.case
            ).exists()
        )
        self.assertTrue(
            Communication.objects.filter(
                related_entity_type="approval_case", related_entity_id=self.case.pk
            ).exists()
        )

    def test_malformed_exclusion_snapshot_is_not_public_or_actionable(self):
        self.case.excluded_approvers_json = [
            {
                "user_id": str(self.director.pk),
                "conflict_code": "director_relative",
                "reason": "",
            }
        ]
        self.case.save(update_fields=["excluded_approvers_json"])

        detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **self._auth(self.cfo)
        )
        action = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2}, content_type="application/json", **self._auth(self.cfo),
        )

        self.assertEqual(detail.status_code, 404)
        self.assertEqual(action.status_code, 404)
        self.assertFalse(ApprovalAction.objects.filter(approval_case=self.case).exists())

    def test_cycle_database_constraints_reject_duplicate_pending_and_nonpositive_rows(self):
        review = AppraisalReviewDecision.objects.create(
            loan_appraisal_note=self.note,
            decision="reviewed",
            review_comments="Constraint fixture review.",
            reviewer_user=self.preparer,
            decided_at=self.note.reviewed_at,
            from_state="review_pending",
            to_state=LoanAppraisalNote.STATUS_REVIEWED,
        )
        common = {
            "loan_application": self.application,
            "loan_appraisal_note": self.note,
            "appraisal_review_decision": review,
            "submitted_by_user": self.preparer,
            "submission_remarks": "Constraint fixture.",
        }
        with self.assertRaises(IntegrityError), transaction.atomic():
            ApprovalCase.objects.create(**common, cycle_number=2)

        self.case.current_status = ApprovalCase.STATUS_RETURNED
        self.case.save(update_fields=["current_status"])
        with self.assertRaises(IntegrityError), transaction.atomic():
            ApprovalCase.objects.create(
                **common,
                cycle_number=1,
                current_status=ApprovalCase.STATUS_RETURNED,
            )
        with self.assertRaises(IntegrityError), transaction.atomic():
            ApprovalCase.objects.create(
                **common,
                cycle_number=0,
                current_status=ApprovalCase.STATUS_RETURNED,
            )
        with self.assertRaises(IntegrityError), transaction.atomic():
            ApprovalCase.objects.create(
                loan_application=self.application,
                loan_appraisal_note=self.note,
                submitted_by_user=self.preparer,
                submission_remarks="Missing later-cycle review.",
                cycle_number=2,
                current_status=ApprovalCase.STATUS_RETURNED,
            )

    def test_credit_manager_reads_only_a_case_owned_through_the_credit_submission_scope(self):
        credit_manager = self._user(
            "credit_manager",
            "Submitting Credit Manager",
            self.read_permission,
            self.application_read_permission,
        )
        credit_manager.primary_role.role_code = "credit_manager"
        credit_manager.primary_role.save(update_fields=["role_code"])
        self.case.submitted_by_user = credit_manager
        self.case.save(update_fields=["submitted_by_user"])
        headers = self._auth(credit_manager)

        owned_list = self.client.get("/api/v1/approval-cases/", **headers)
        owned_detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **headers
        )

        self.assertEqual(owned_list.status_code, 200)
        self.assertEqual(owned_list.json()["pagination"]["total_count"], 1)
        self.assertEqual(owned_detail.status_code, 200)

        self.case.submitted_by_user = self.preparer
        self.case.save(update_fields=["submitted_by_user"])
        self.application.current_stage = LoanApplication.STAGE_INITIAL
        self.application.save(update_fields=["current_stage"])

        unrelated_list = self.client.get("/api/v1/approval-cases/", **headers)
        unrelated_detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **headers
        )

        self.assertEqual(unrelated_list.status_code, 200)
        self.assertEqual(unrelated_list.json()["data"], [])
        self.assertEqual(unrelated_list.json()["pagination"]["total_count"], 0)
        self.assertEqual(unrelated_detail.status_code, 403)
        assert_error_envelope(self, unrelated_detail.json(), "OBJECT_ACCESS_DENIED")

    def test_active_company_secretary_grant_allows_read_only_case_access(self):
        grant_model = apps.get_model("approvals", "ApprovalCaseReadScopeGrant")
        company_secretary = self._user(
            "company_secretary", "Sanction Package Company Secretary", self.read_permission
        )
        company_secretary.primary_role.role_code = "company_secretary"
        company_secretary.primary_role.save(update_fields=["role_code"])
        grant = grant_model.objects.create(
            role=company_secretary.primary_role,
            scope_type="legal_readonly",
            status="active",
        )
        headers = self._auth(company_secretary)

        collection = self.client.get("/api/v1/approval-cases/", **headers)
        detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **headers
        )

        self.assertEqual(collection.status_code, 200)
        self.assertEqual(collection.json()["pagination"]["total_count"], 1)
        self.assertEqual(detail.status_code, 200)
        self.assertTrue(
            all(
                not action["enabled"]
                for action in detail.json()["data"]["available_actions"]
            )
        )
        self._assert_read_only_scope_never_assigns_or_mutates(company_secretary)

        company_secretary.primary_role.status = "inactive"
        company_secretary.primary_role.save(update_fields=["status"])
        inactive_role = self.client.get("/api/v1/approval-cases/", **headers)
        self.assertEqual(inactive_role.status_code, 403)
        assert_error_envelope(self, inactive_role.json(), "FORBIDDEN")
        company_secretary.primary_role.status = "active"
        company_secretary.primary_role.save(update_fields=["status"])

        grant.status = "inactive"
        grant.save(update_fields=["status"])
        inactive_list = self.client.get("/api/v1/approval-cases/", **headers)
        inactive_detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **headers
        )
        self.assertEqual(inactive_list.json()["pagination"]["total_count"], 0)
        self.assertEqual(inactive_detail.status_code, 403)
        assert_error_envelope(self, inactive_detail.json(), "OBJECT_ACCESS_DENIED")

        grant.status = "active"
        grant.save(update_fields=["status"])
        grant.delete()
        deleted_list = self.client.get("/api/v1/approval-cases/", **headers)
        deleted_detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **headers
        )
        self.assertEqual(deleted_list.json()["pagination"]["total_count"], 0)
        self.assertEqual(deleted_detail.status_code, 403)
        assert_error_envelope(self, deleted_detail.json(), "OBJECT_ACCESS_DENIED")

    def test_auditor_scope_never_assigns_or_mutates_a_case(self):
        grant_model = apps.get_model("approvals", "ApprovalCaseReadScopeGrant")
        auditor = self._user(
            "internal_auditor", "Sanction Package Auditor", self.read_permission
        )
        auditor.primary_role.role_code = "internal_auditor"
        auditor.primary_role.save(update_fields=["role_code"])
        grant_model.objects.create(
            role=auditor.primary_role,
            scope_type="audit_readonly",
            status="active",
        )
        self._assert_read_only_scope_never_assigns_or_mutates(auditor)

    def test_selector_materializes_only_credit_manager_object_scope_candidates(self):
        credit_manager = self._user(
            "credit_manager", "Selector Credit Manager", self.read_permission
        )
        credit_manager.primary_role.role_code = "credit_manager"
        credit_manager.primary_role.save(update_fields=["role_code"])
        self.case.submitted_by_user = credit_manager
        self.case.save(update_fields=["submitted_by_user"])

        unrelated_ids = []
        for _ in range(8):
            shell = self._create_unrouted_shell()
            shell.approval_matrix_rule = self.rule
            shell.sanction_committee = self.committee
            shell.decision_date = self.case.decision_date
            shell.amount = self.case.amount
            shell.related_entity_id = shell.loan_application_id
            shell.version = 2
            shell.required_approvers_json = self.case.required_approvers_json
            shell.save()
            unrelated_ids.append(shell.pk)

        queryset, persisted_scope = select_approval_case_candidates(
            actor=credit_manager
        )
        with self.assertNumQueries(1):
            candidate_ids = list(queryset.values_list("pk", flat=True))

        self.assertIsNone(persisted_scope)
        self.assertEqual(candidate_ids, [self.case.pk])
        self.assertTrue(
            ApprovalCase.objects.filter(pk__in=unrelated_ids, version=2).exists()
        )

    def test_persisted_scope_list_work_is_bounded_as_repository_grows(self):
        grant_model = apps.get_model("approvals", "ApprovalCaseReadScopeGrant")
        company_secretary = self._user(
            "company_secretary", "Bounded Query Company Secretary", self.read_permission
        )
        company_secretary.primary_role.role_code = "company_secretary"
        company_secretary.primary_role.save(update_fields=["role_code"])
        grant_model.objects.create(
            role=company_secretary.primary_role,
            scope_type="legal_readonly",
            status="active",
        )
        headers = self._auth(company_secretary)
        with CaptureQueriesContext(connection) as baseline_queries:
            baseline = self.client.get("/api/v1/approval-cases/", **headers)

        for _ in range(8):
            shell = self._create_unrouted_shell()
            shell.approval_matrix_rule = self.rule
            shell.sanction_committee = self.committee
            shell.decision_date = self.case.decision_date
            shell.amount = self.case.amount
            shell.related_entity_type = "loan_application"
            shell.related_entity_id = shell.loan_application_id
            shell.version = 2
            shell.required_approvers_json = self.case.required_approvers_json
            shell.save()

        with CaptureQueriesContext(connection) as expanded_queries:
            expanded = self.client.get("/api/v1/approval-cases/", **headers)

        self.assertEqual(baseline.json()["pagination"]["total_count"], 1)
        self.assertEqual(expanded.json()["pagination"]["total_count"], 1)
        self.assertLessEqual(len(expanded_queries), len(baseline_queries))

    def test_approval_read_dependency_flows_from_engine_to_selector(self):
        selector_tree = ast.parse(inspect.getsource(approval_case_selector))
        imported_modules = {
            alias.name
            for node in ast.walk(selector_tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        self.assertFalse(
            any("approval_case_engine" in module for module in imported_modules)
        )
        for consumer in (sanction_register, exception_register):
            source = inspect.getsource(consumer)
            self.assertIn("approval_case_engine.select_readable_approval_cases", source)
            self.assertNotIn("select_approval_case_candidates", source)
        action_source = inspect.getsource(approval_actions)
        self.assertIn("approval_case_engine.approval_case_is_readable", action_source)
        self.assertNotIn("approval_case_engine.can_read_approval_case", action_source)

    def test_required_approver_selector_uses_exact_user_id_not_json_substring(self):
        reader = self._user("json_substring_reader", "JSON Substring Reader", self.read_permission)
        self.case.required_approvers_json[0]["full_name"] = str(reader.pk)
        self.case.save(update_fields=["required_approvers_json"])

        response = self.client.get(
            "/api/v1/approval-cases/", **self._auth(reader)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], [])
        self.assertEqual(response.json()["pagination"]["total_count"], 0)

    def test_read_scope_grant_rejects_duplicate_and_unbounded_scope_values(self):
        grant_model = apps.get_model("approvals", "ApprovalCaseReadScopeGrant")
        role = self._user("scope_role", "Bounded Scope Role").primary_role
        grant_model.objects.create(
            role=role,
            scope_type="management_readonly",
            status="active",
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            grant_model.objects.create(
                role=role,
                scope_type="management_readonly",
                status="active",
            )
        with self.assertRaises(IntegrityError), transaction.atomic():
            grant_model.objects.create(
                role=role,
                scope_type="query_flag_global",
                status="active",
            )
        with self.assertRaises(IntegrityError), transaction.atomic():
            grant_model.objects.create(
                role=self.preparer.primary_role,
                scope_type="legal_readonly",
                status="revoked-by-text",
            )

    def test_assigned_approver_can_record_partial_approval_through_canonical_case_projection(self):
        entry = ExceptionRegisterEntry.objects.create(
            loan_application=self.application,
            exception_type="exceeds_loan_limit",
            description="Frozen permissible limit exceeded.",
            business_reason="Exception requires joint authority.",
            approval_case=self.case,
        )
        response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2, "comments": "Approved after reviewing the appraisal."},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-approval-partial",
            HTTP_USER_AGENT="Approval Action Contract Test",
            REMOTE_ADDR="203.0.113.17",
            **self._auth(self.cfo),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["approval_case_id"], str(self.case.pk))
        self.assertEqual(data["decision"], "approved")
        self.assertEqual(data["approval_case_status"], "pending")
        self.assertFalse(data["sanction_decision_created"])
        self.assertIsNone(data["sanction_decision_id"])
        self.assertEqual(data["current_status"], "pending")
        self.assertEqual(
            data["workbench_summary"]["current_decision_status"],
            "partially_approved",
        )
        self.assertEqual(data["version"], 3)
        self.assertEqual(
            next(
                item for item in data["required_approvers"]
                if item["user_id"] == str(self.cfo.pk)
            )["decision"],
            "approved",
        )
        self.assertTrue(all(not item["enabled"] for item in data["available_actions"]))

        action = ApprovalAction.objects.get(approval_case=self.case, approver_user=self.cfo)
        self.assertEqual(str(action.pk), data["approval_action_id"])
        self.assertEqual(action.approver_role_code, "cfo")
        self.assertEqual(action.comments, "Approved after reviewing the appraisal.")
        self.assertEqual(action.ip_address, "203.0.113.17")
        self.assertEqual(action.user_agent, "Approval Action Contract Test")
        self.case.refresh_from_db()
        self.assertEqual(self.case.current_status, "pending")
        self.assertEqual(self.case.version, 3)
        entry.refresh_from_db()
        self.assertEqual(entry.status, "pending")
        self.assertIsNone(entry.closed_at)

    def test_case_detail_projects_general_meeting_record_authority(self):
        recorder, _payload = self._general_meeting_recorder_and_payload()

        response = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **self._auth(recorder)
        )

        self.assertEqual(response.status_code, 200, response.content)
        action = next(
            item
            for item in response.json()["data"]["available_actions"]
            if item["action_code"] == "record_general_meeting_approval"
        )
        self.assertTrue(action["enabled"])
        self.assertEqual(
            action["required_permission"], "approvals.general_meeting.record"
        )

    def test_authorized_recorder_creates_approved_general_meeting_evidence(self):
        recorder, payload = self._general_meeting_recorder_and_payload()

        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/general-meeting-approval/",
            payload,
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-general-meeting-approved",
            HTTP_USER_AGENT="General Meeting Contract Test",
            REMOTE_ADDR="203.0.113.71",
            **self._auth(recorder),
        )

        self.assertEqual(response.status_code, 200, response.content)
        assert_success_envelope(self, response.json())
        data = response.json()["data"]
        self.assertEqual(data["loan_application_id"], str(self.application.pk))
        self.assertEqual(data["related_party_type"], "director_relative")
        self.assertEqual(data["related_party_user_id"], str(self.director.pk))
        self.assertEqual(data["relationship_description"], "Borrower is a relative of a Director.")
        self.assertEqual(data["meeting_date"], timezone.localdate().isoformat())
        self.assertEqual(data["notice_document_id"], payload["notice_document_id"])
        self.assertEqual(data["minutes_document_id"], payload["minutes_document_id"])
        self.assertEqual(data["resolution_document_id"], payload["resolution_document_id"])
        self.assertEqual(data["approval_status"], "approved")
        self.assertEqual(data["recorded_by_user_id"], str(recorder.pk))
        self.assertIsNone(data["supersedes_general_meeting_approval_id"])
        meeting_model = apps.get_model("approvals", "GeneralMeetingApproval")
        meeting = meeting_model.objects.get(pk=data["general_meeting_approval_id"])
        self.assertEqual(meeting.loan_application_id, self.application.pk)
        audit = AuditLog.objects.get(action="general_meeting_approval.recorded")
        self.assertEqual(audit.actor_user, recorder)
        self.assertEqual(audit.entity_id, meeting.pk)
        self.assertEqual(audit.new_value_json["approval_status"], "approved")
        self.assertEqual(audit.new_value_json["request_id"], "req-general-meeting-approved")
        workflow = WorkflowEvent.objects.get(
            workflow_name="general_meeting_approval",
            entity_id=meeting.pk,
        )
        self.assertEqual(workflow.from_state, None)
        self.assertEqual(workflow.to_state, "approved")
        self.assertEqual(workflow.triggered_by_user, recorder)

    def test_general_meeting_exact_replay_is_zero_write_and_changed_status_supersedes(self):
        recorder, payload = self._general_meeting_recorder_and_payload()
        url = (
            f"/api/v1/loan-applications/{self.application.pk}/"
            "general-meeting-approval/"
        )

        first = self.client.post(
            url,
            payload,
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-general-meeting-first",
            **self._auth(recorder),
        )
        replay = self.client.post(
            url,
            payload,
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-general-meeting-replay",
            **self._auth(recorder),
        )
        rejected = self.client.post(
            url,
            {**payload, "approval_status": "rejected"},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-general-meeting-rejected",
            **self._auth(recorder),
        )

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(rejected.status_code, 200, rejected.content)
        first_id = first.json()["data"]["general_meeting_approval_id"]
        self.assertEqual(
            replay.json()["data"]["general_meeting_approval_id"], first_id
        )
        rejected_data = rejected.json()["data"]
        self.assertNotEqual(rejected_data["general_meeting_approval_id"], first_id)
        self.assertEqual(
            rejected_data["supersedes_general_meeting_approval_id"], first_id
        )
        meeting_model = apps.get_model("approvals", "GeneralMeetingApproval")
        self.assertEqual(meeting_model.objects.count(), 2)
        self.assertEqual(meeting_model.objects.get(pk=first_id).approval_status, "approved")
        self.assertEqual(
            AuditLog.objects.filter(
                action="general_meeting_approval.recorded"
            ).count(),
            1,
        )
        status_audit = AuditLog.objects.get(
            action="general_meeting_approval.status_changed"
        )
        self.assertEqual(status_audit.old_value_json["approval_status"], "approved")
        self.assertEqual(status_audit.new_value_json["approval_status"], "rejected")
        self.assertEqual(
            status_audit.new_value_json["request_id"],
            "req-general-meeting-rejected",
        )
        workflows = WorkflowEvent.objects.filter(
            workflow_name="general_meeting_approval"
        ).order_by("created_at")
        self.assertEqual(workflows.count(), 2)
        self.assertEqual(workflows[1].from_state, "approved")
        self.assertEqual(workflows[1].to_state, "rejected")

    def test_related_party_final_approval_requires_general_meeting_evidence(self):
        self.case.general_meeting_evidence_required = True
        self.case.save(update_fields=["general_meeting_evidence_required"])
        exception_entry = ExceptionRegisterEntry.objects.create(
            loan_application=self.application,
            exception_type="waiver",
            description="Related-party case requires exceptional governance.",
            business_reason="Preserve pending exception evidence on denied sanction.",
            approval_case=self.case,
        )
        partial = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2, "comments": "CFO approval is not yet final."},
            content_type="application/json",
            **self._auth(self.cfo),
        )
        self.assertEqual(partial.status_code, 200, partial.content)
        director_headers = self._auth(self.director)
        before = self._action_ledgers()

        denied = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 3, "comments": "Director attempts final approval."},
            content_type="application/json",
            **director_headers,
        )

        self.assertEqual(denied.status_code, 409, denied.content)
        assert_error_envelope(self, denied.json(), "GENERAL_MEETING_EVIDENCE_REQUIRED")
        self.assertEqual(
            denied.json()["error"]["details"],
            {
                "approval_case_id": str(self.case.pk),
                "cycle_number": 1,
                "general_meeting_approval": None,
            },
        )
        self.assertEqual(self._action_ledgers(), before)
        self.assertFalse(
            apps.get_model("approvals", "SanctionDecision").objects.filter(
                approval_case=self.case
            ).exists()
        )
        exception_entry.refresh_from_db()
        self.assertEqual(exception_entry.status, "pending")
        self.assertIsNone(exception_entry.closed_at)

    def test_latest_general_meeting_outcome_gates_and_is_frozen_on_the_case_cycle(self):
        recorder, payload = self._general_meeting_recorder_and_payload()
        meeting_url = (
            f"/api/v1/loan-applications/{self.application.pk}/"
            "general-meeting-approval/"
        )
        rejected = self.client.post(
            meeting_url,
            {**payload, "approval_status": "rejected"},
            content_type="application/json",
            **self._auth(recorder),
        )
        self.assertEqual(rejected.status_code, 200, rejected.content)
        rejected_id = rejected.json()["data"]["general_meeting_approval_id"]
        rejected_evidence = {
            **rejected.json()["data"],
            "evidence_scope": "current_pending",
        }
        detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **self._auth(self.director)
        )
        self.assertEqual(
            detail.json()["data"]["general_meeting_approval"], rejected_evidence
        )
        partial = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2},
            content_type="application/json",
            **self._auth(self.cfo),
        )
        self.assertEqual(partial.status_code, 200, partial.content)
        self.assertEqual(
            partial.json()["data"]["general_meeting_approval"], rejected_evidence
        )
        director_headers = self._auth(self.director)
        before = self._action_ledgers()

        denied = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 3},
            content_type="application/json",
            **director_headers,
        )

        self.assertEqual(denied.status_code, 409, denied.content)
        assert_error_envelope(self, denied.json(), "GENERAL_MEETING_APPROVAL_REJECTED")
        self.assertEqual(
            denied.json()["error"]["details"]["general_meeting_approval"],
            rejected_evidence,
        )
        self.assertEqual(self._action_ledgers(), before)

        approved = self.client.post(
            meeting_url,
            payload,
            content_type="application/json",
            **self._auth(recorder),
        )
        self.assertEqual(approved.status_code, 200, approved.content)
        approved_data = approved.json()["data"]
        self.assertEqual(
            approved_data["supersedes_general_meeting_approval_id"], rejected_id
        )
        completed = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 3},
            content_type="application/json",
            **director_headers,
        )

        self.assertEqual(completed.status_code, 200, completed.content)
        completed_data = completed.json()["data"]
        self.assertEqual(completed_data["current_status"], "approved")
        self.assertTrue(completed_data["sanction_decision_created"])
        self.assertEqual(
            completed_data["general_meeting_approval"],
            {**approved_data, "evidence_scope": "cycle_frozen"},
        )
        self.case.refresh_from_db()
        self.assertEqual(
            str(self.case.general_meeting_approval_id),
            approved_data["general_meeting_approval_id"],
        )
        detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **director_headers
        )
        self.assertEqual(detail.status_code, 200, detail.content)
        self.assertEqual(
            detail.json()["data"]["general_meeting_approval"],
            {**approved_data, "evidence_scope": "cycle_frozen"},
        )

    def test_pending_general_meeting_outcome_blocks_final_sanction(self):
        recorder, payload = self._general_meeting_recorder_and_payload()
        meeting = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/general-meeting-approval/",
            {**payload, "approval_status": "pending"},
            content_type="application/json",
            **self._auth(recorder),
        )
        self.assertEqual(meeting.status_code, 200, meeting.content)
        pending_evidence = {
            **meeting.json()["data"],
            "evidence_scope": "current_pending",
        }
        detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **self._auth(self.director)
        )
        collection = self.client.get(
            "/api/v1/approval-cases/", **self._auth(self.director)
        )
        self.assertEqual(detail.status_code, 200, detail.content)
        self.assertEqual(
            detail.json()["data"]["general_meeting_approval"], pending_evidence
        )
        self.assertEqual(
            collection.json()["data"][0]["general_meeting_approval"],
            pending_evidence,
        )
        partial = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2},
            content_type="application/json",
            **self._auth(self.cfo),
        )
        self.assertEqual(partial.status_code, 200, partial.content)
        self.assertEqual(
            partial.json()["data"]["general_meeting_approval"], pending_evidence
        )
        denied = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 3},
            content_type="application/json",
            **self._auth(self.director),
        )
        self.assertEqual(denied.status_code, 409, denied.content)
        assert_error_envelope(self, denied.json(), "GENERAL_MEETING_APPROVAL_PENDING")
        self.assertEqual(
            denied.json()["error"]["details"]["general_meeting_approval"],
            pending_evidence,
        )
        self.assertFalse(
            ApprovalAction.objects.filter(
                approval_case=self.case, approver_user=self.director
            ).exists()
        )

    def test_general_meeting_document_and_permission_denials_are_zero_write(self):
        recorder, payload = self._general_meeting_recorder_and_payload()
        url = (
            f"/api/v1/loan-applications/{self.application.pk}/"
            "general-meeting-approval/"
        )
        auth = self._auth(recorder)
        meeting_model = apps.get_model("approvals", "GeneralMeetingApproval")

        missing = self.client.post(
            url,
            {**payload, "resolution_document_id": "70000000-0000-0000-0000-000000000007"},
            content_type="application/json",
            **auth,
        )

        self.assertEqual(missing.status_code, 400, missing.content)
        assert_error_envelope(self, missing.json(), "VALIDATION_ERROR")
        self.assertEqual(
            missing.json()["error"]["field_errors"]["resolution_document_id"],
            "Document file was not found or is inaccessible.",
        )
        self.assertEqual(meeting_model.objects.count(), 0)

        cross_application_document = self._upload_general_meeting_document(
            recorder,
            "other-application-notice.pdf",
            related_entity_id="70000000-0000-0000-0000-000000000008",
        )
        before_cross_application = self._general_meeting_ledgers()
        cross_application = self.client.post(
            url,
            {**payload, "notice_document_id": cross_application_document},
            content_type="application/json",
            **auth,
        )
        self.assertEqual(cross_application.status_code, 400, cross_application.content)
        assert_error_envelope(self, cross_application.json(), "VALIDATION_ERROR")
        self.assertEqual(
            cross_application.json()["error"]["field_errors"]["notice_document_id"],
            "Document file was not found or is inaccessible.",
        )
        self.assertEqual(self._general_meeting_ledgers(), before_cross_application)
        self.assertFalse(
            AuditLog.objects.filter(
                action__startswith="general_meeting_approval."
            ).exists()
        )
        self.assertFalse(
            WorkflowEvent.objects.filter(
                workflow_name="general_meeting_approval"
            ).exists()
        )

        RolePermission.objects.filter(
            role=recorder.primary_role,
            permission__permission_code="documents.file.download",
        ).delete()
        no_document_access = self.client.post(
            url, payload, content_type="application/json", **auth
        )
        self.assertEqual(no_document_access.status_code, 403, no_document_access.content)
        assert_error_envelope(self, no_document_access.json(), "FORBIDDEN")
        self.assertEqual(meeting_model.objects.count(), 0)

        document_permission = Permission.objects.get(
            permission_code="documents.file.download"
        )
        RolePermission.objects.create(
            role=recorder.primary_role, permission=document_permission
        )
        RolePermission.objects.filter(
            role=recorder.primary_role,
            permission__permission_code="approvals.general_meeting.record",
        ).delete()
        no_record_authority = self.client.post(
            url, payload, content_type="application/json", **auth
        )
        self.assertEqual(no_record_authority.status_code, 403, no_record_authority.content)
        assert_error_envelope(self, no_record_authority.json(), "FORBIDDEN")
        self.assertEqual(meeting_model.objects.count(), 0)

        unscoped = self._user(
            "unscoped_general_meeting_recorder",
            "Unscoped General Meeting Recorder",
            self.read_permission,
            Permission.objects.get(
                permission_code="approvals.general_meeting.record"
            ),
            document_permission,
        )
        no_case_scope = self.client.post(
            url,
            payload,
            content_type="application/json",
            **self._auth(unscoped),
        )
        self.assertEqual(no_case_scope.status_code, 403, no_case_scope.content)
        assert_error_envelope(self, no_case_scope.json(), "OBJECT_ACCESS_DENIED")
        self.assertEqual(meeting_model.objects.count(), 0)

        audit_reader = self._user(
            "audit_only_general_meeting_recorder",
            "Audit-only General Meeting Recorder",
            self.read_permission,
            Permission.objects.get(
                permission_code="approvals.general_meeting.record"
            ),
            document_permission,
        )
        audit_reader.primary_role.role_code = "internal_auditor"
        audit_reader.primary_role.save(update_fields=["role_code"])
        ApprovalCaseReadScopeGrant.objects.create(
            role=audit_reader.primary_role,
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
        )
        before_audit_denial = self._general_meeting_ledgers()
        audit_only = self.client.post(
            url,
            payload,
            content_type="application/json",
            **self._auth(audit_reader),
        )
        self.assertEqual(audit_only.status_code, 400, audit_only.content)
        assert_error_envelope(self, audit_only.json(), "VALIDATION_ERROR")
        self.assertEqual(
            audit_only.json()["error"]["field_errors"],
            {
                field: "Document file was not found or is inaccessible."
                for field in (
                    "notice_document_id",
                    "minutes_document_id",
                    "resolution_document_id",
                )
            },
        )
        self.assertEqual(self._general_meeting_ledgers(), before_audit_denial)

    def test_general_meeting_payload_and_related_case_scope_are_bounded(self):
        recorder, payload = self._general_meeting_recorder_and_payload()
        url = (
            f"/api/v1/loan-applications/{self.application.pk}/"
            "general-meeting-approval/"
        )
        invalid = self.client.post(
            url,
            {
                **payload,
                "related_party_type": "material_interest",
                "relationship_description": "   ",
                "meeting_date": "13/07/2026",
                "notice_document_id": "not-a-uuid",
                "approval_status": "waived",
                "unexpected": True,
            },
            content_type="application/json",
            **self._auth(recorder),
        )

        self.assertEqual(invalid.status_code, 400, invalid.content)
        assert_error_envelope(self, invalid.json(), "VALIDATION_ERROR")
        self.assertEqual(
            set(invalid.json()["error"]["field_errors"]),
            {
                "approval_status",
                "meeting_date",
                "notice_document_id",
                "related_party_type",
                "relationship_description",
                "unexpected",
            },
        )
        self.assertEqual(
            apps.get_model("approvals", "GeneralMeetingApproval").objects.count(),
            0,
        )
        self.case.general_meeting_evidence_required = False
        self.case.save(update_fields=["general_meeting_evidence_required"])
        unrelated = self.client.post(
            url, payload, content_type="application/json", **self._auth(recorder)
        )
        self.assertEqual(unrelated.status_code, 409, unrelated.content)
        assert_error_envelope(self, unrelated.json(), "INVALID_STATE")
        self.assertEqual(
            apps.get_model("approvals", "GeneralMeetingApproval").objects.count(),
            0,
        )

    def test_each_general_meeting_document_field_uses_nondisclosing_reference_scope(self):
        recorder, payload = self._general_meeting_recorder_and_payload()
        url = (
            f"/api/v1/loan-applications/{self.application.pk}/"
            "general-meeting-approval/"
        )
        corrupt_sensitivity_document = self._upload_general_meeting_document(
            recorder,
            "unsupported-sensitivity.pdf",
            sensitivity_level="public",
        )
        document_model = apps.get_model("documents", "DocumentFile")
        document_model.objects.filter(pk=corrupt_sensitivity_document).update(
            sensitivity_level="unsupported"
        )
        denied_documents = {
            "cross_application": self._upload_general_meeting_document(
                recorder,
                "cross-application.pdf",
                related_entity_id="70000000-0000-0000-0000-000000000009",
            ),
            "unrelated": self._upload_general_meeting_document(
                recorder,
                "unrelated.pdf",
                related_entity_type="",
                related_entity_id="",
            ),
            "disallowed_category": self._upload_general_meeting_document(
                recorder,
                "finance-category.pdf",
                document_category="finance",
            ),
            "disallowed_sensitivity": corrupt_sensitivity_document,
            "missing": "70000000-0000-0000-0000-000000000010",
        }
        before = self._general_meeting_ledgers()

        for field in (
            "notice_document_id",
            "minutes_document_id",
            "resolution_document_id",
        ):
            for denial, document_id in denied_documents.items():
                with self.subTest(field=field, denial=denial):
                    response = self.client.post(
                        url,
                        {**payload, field: document_id},
                        content_type="application/json",
                        **self._auth(recorder),
                    )
                    self.assertEqual(response.status_code, 400, response.content)
                    assert_error_envelope(self, response.json(), "VALIDATION_ERROR")
                    self.assertEqual(
                        response.json()["error"]["field_errors"][field],
                        "Document file was not found or is inaccessible.",
                    )
                    self.assertEqual(self._general_meeting_ledgers(), before)
    def test_returned_cycle_keeps_its_applicable_general_meeting_reference(self):
        recorder, payload = self._general_meeting_recorder_and_payload()
        meeting_url = (
            f"/api/v1/loan-applications/{self.application.pk}/"
            "general-meeting-approval/"
        )
        approved = self.client.post(
            meeting_url,
            payload,
            content_type="application/json",
            **self._auth(recorder),
        )
        self.assertEqual(approved.status_code, 200, approved.content)
        approved_data = approved.json()["data"]

        returned = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/return-for-clarification/",
            {"version": 2, "comments": "Correct the appraisal before a new cycle."},
            content_type="application/json",
            **self._auth(self.cfo),
        )

        self.assertEqual(returned.status_code, 200, returned.content)
        self.assertEqual(returned.json()["data"]["current_status"], "returned_for_clarification")
        self.assertEqual(
            returned.json()["data"]["general_meeting_approval"],
            {**approved_data, "evidence_scope": "cycle_frozen"},
        )
        rejected = self.client.post(
            meeting_url,
            {**payload, "approval_status": "rejected"},
            content_type="application/json",
            **self._auth(recorder),
        )
        self.assertEqual(rejected.status_code, 200, rejected.content)
        self.assertNotEqual(
            rejected.json()["data"]["general_meeting_approval_id"],
            approved_data["general_meeting_approval_id"],
        )

        historical = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **self._auth(self.cfo)
        )
        self.assertEqual(historical.status_code, 200, historical.content)
        self.assertEqual(
            historical.json()["data"]["general_meeting_approval"],
            {**approved_data, "evidence_scope": "cycle_frozen"},
        )

    def test_rejected_cycle_freezes_current_evidence_before_later_supersession(self):
        recorder, payload = self._general_meeting_recorder_and_payload()
        meeting_url = (
            f"/api/v1/loan-applications/{self.application.pk}/"
            "general-meeting-approval/"
        )
        pending = self.client.post(
            meeting_url,
            {**payload, "approval_status": "pending"},
            content_type="application/json",
            **self._auth(recorder),
        )
        self.assertEqual(pending.status_code, 200, pending.content)
        pending_data = pending.json()["data"]

        rejected_case = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/reject/",
            {"version": 2, "comments": "Sanction case rejected."},
            content_type="application/json",
            **self._auth(self.cfo),
        )
        self.assertEqual(rejected_case.status_code, 200, rejected_case.content)
        self.assertEqual(rejected_case.json()["data"]["current_status"], "rejected")
        self.assertEqual(
            rejected_case.json()["data"]["general_meeting_approval"],
            {**pending_data, "evidence_scope": "cycle_frozen"},
        )

        later = self.client.post(
            meeting_url,
            {**payload, "approval_status": "approved"},
            content_type="application/json",
            **self._auth(recorder),
        )
        self.assertEqual(later.status_code, 200, later.content)
        historical = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **self._auth(self.cfo)
        )
        self.assertEqual(
            historical.json()["data"]["general_meeting_approval"],
            {**pending_data, "evidence_scope": "cycle_frozen"},
        )

    def test_exception_register_is_read_only_filtered_paginated_and_object_scoped(self):
        read_permission = self._permission("approvals.exception_register.read")
        RolePermission.objects.create(
            role=self.cfo.primary_role, permission=read_permission
        )
        entry = ExceptionRegisterEntry.objects.create(
            loan_application=self.application,
            exception_type="exceeds_loan_limit",
            description="Frozen permissible limit exceeded.",
            business_reason="Exception requires joint authority.",
            risk_assessment="Seasonal cash-flow monitoring.",
            approval_case=self.case,
        )

        response = self.client.get(
            "/api/v1/exception-register/?status=pending&exception_type=exceeds_loan_limit&page=1&page_size=10",
            **self._auth(self.cfo),
        )

        self.assertEqual(response.status_code, 200, response.content)
        assert_success_envelope(self, response.json())
        assert_pagination_shape(self, response.json())
        self.assertEqual(response.json()["pagination"]["total_count"], 1)
        row = response.json()["data"][0]
        self.assertEqual(row["exception_register_entry_id"], str(entry.pk))
        self.assertEqual(row["approval_case_id"], str(self.case.pk))
        self.assertEqual(row["cycle_number"], 1)
        self.assertEqual(row["status"], "pending")
        self.assertEqual(row["exception_type"], "exceeds_loan_limit")
        self.assertEqual(row["route_approvers"], self.case.required_approvers_json)
        self.assertEqual(len(row["required_approvers"]), 2)
        self.assertEqual(row["approval_actions"], [])
        self.assertIn("CFO", row["authority_applied_summary"])
        self.assertIn("Director", row["authority_applied_summary"])

        unmatched = self.client.get(
            "/api/v1/exception-register/?status=approved", **self._auth(self.cfo)
        )
        self.assertEqual(unmatched.status_code, 200)
        self.assertEqual(unmatched.json()["data"], [])
        self.assertEqual(unmatched.json()["pagination"]["total_count"], 0)
        denied = self.client.get(
            "/api/v1/exception-register/", **self._auth(self.director)
        )
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(denied.json()["error"]["code"], "FORBIDDEN")
        unused_candidate = self._user(
            "unused_exception_reader", "Unused Exception Reader", read_permission
        )
        unused = self.client.get(
            "/api/v1/exception-register/", **self._auth(unused_candidate)
        )
        self.assertEqual(unused.status_code, 200)
        self.assertEqual(unused.json()["pagination"]["total_count"], 0)
        self.assertEqual(unused.json()["data"], [])
        mutation = self.client.post(
            "/api/v1/exception-register/",
            {"exception_type": "waiver"},
            content_type="application/json",
            **self._auth(self.cfo),
        )
        self.assertEqual(mutation.status_code, 405)

    def test_partial_action_collection_detail_and_action_share_history_aware_projection(self):
        action_response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2},
            content_type="application/json",
            **self._auth(self.cfo),
        )
        detail_response = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **self._auth(self.cfo)
        )
        collection_response = self.client.get(
            "/api/v1/approval-cases/", **self._auth(self.cfo)
        )

        self.assertEqual(action_response.status_code, 200, action_response.json())
        self.assertEqual(detail_response.status_code, 200, detail_response.json())
        self.assertEqual(collection_response.status_code, 200, collection_response.json())
        action_data = action_response.json()["data"]
        detail_data = detail_response.json()["data"]
        collection_data = collection_response.json()["data"][0]
        shared_fields = (
            "approval_case_id",
            "current_status",
            "version",
            "approval_matrix_rule_id",
            "approval_matrix_rule_version",
            "sanction_committee_id",
            "sanction_committee_version",
            "required_approvers",
            "excluded_approvers",
            "available_actions",
        )
        self.assertEqual(
            {field: action_data[field] for field in shared_fields},
            {field: detail_data[field] for field in shared_fields},
        )
        self.assertEqual(
            {field: action_data[field] for field in shared_fields},
            {field: collection_data[field] for field in shared_fields},
        )
        acted = next(
            item for item in collection_data["required_approvers"]
            if item["user_id"] == str(self.cfo.pk)
        )
        self.assertEqual(acted["decision"], "approved")
        self.assertIsNotNone(acted["acted_at"])

    def test_final_joint_approval_creates_source_shaped_sanction_and_completion_evidence(self):
        entry = ExceptionRegisterEntry.objects.create(
            loan_application=self.application,
            exception_type="exceeds_loan_limit",
            description="Frozen permissible limit exceeded.",
            business_reason="Exception requires joint authority.",
            approval_case=self.case,
        )
        self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2, "comments": "CFO approval."},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-approval-cfo",
            **self._auth(self.cfo),
        )
        response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 3, "comments": "Director approval."},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-approval-final",
            HTTP_USER_AGENT="Final Approval Contract Test",
            REMOTE_ADDR="203.0.113.18",
            **self._auth(self.director),
        )

        self.assertEqual(response.status_code, 200, response.json())
        data = response.json()["data"]
        self.assertEqual(data["approval_case_status"], "approved")
        self.assertEqual(data["current_status"], "approved")
        self.assertEqual(data["version"], 4)
        self.assertTrue(data["sanction_decision_created"])

        SanctionDecision = apps.get_model("approvals", "SanctionDecision")
        decision = SanctionDecision.objects.get(approval_case=self.case)
        self.assertEqual(str(decision.pk), data["sanction_decision_id"])
        self.assertEqual(decision.decision, "sanctioned")
        self.assertEqual(str(decision.sanctioned_amount), "500000.00")
        self.assertEqual(decision.sanctioned_tenure_months, 12)
        self.assertEqual(decision.interest_rate_type, "floating")
        self.assertIsNone(decision.interest_rate_value)
        self.assertIsNone(decision.repayment_date)
        self.assertIsNone(decision.penal_interest_rate)
        self.assertEqual(decision.charges_json, {})
        self.assertEqual(decision.security_required_summary, "Standard member security package.")
        self.assertEqual(decision.conditions_precedent, "")
        self.assertEqual(decision.decision_reason, self.case.reason_for_approval)

        self.case.refresh_from_db()
        self.application.refresh_from_db()
        self.assertEqual(self.case.current_status, "approved")
        self.assertIsNotNone(self.case.closed_at)
        self.assertEqual(self.application.application_status, "approved_by_sanction_committee")
        self.assertEqual(ApprovalAction.objects.filter(approval_case=self.case).count(), 2)
        entry.refresh_from_db()
        self.assertEqual(entry.status, "approved")
        self.assertEqual(entry.closed_at, self.case.closed_at)
        transition_audit = AuditLog.objects.get(action="exception_register.status_changed")
        self.assertEqual(transition_audit.entity_id, entry.pk)
        self.assertEqual(transition_audit.old_value_json["status"], "pending")
        self.assertEqual(transition_audit.new_value_json["status"], "approved")
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="exception_register").count(), 1
        )

        action_audits = AuditLog.objects.filter(
            action="approval_case.action_recorded", entity_id=self.case.pk
        ).order_by("created_at")
        self.assertEqual(action_audits.count(), 2)
        final_audit = action_audits.last()
        self.assertEqual(str(final_audit.actor_user_id), str(self.director.pk))
        self.assertEqual(final_audit.ip_address, "203.0.113.18")
        self.assertEqual(final_audit.user_agent, "Final Approval Contract Test")
        self.assertEqual(final_audit.new_value_json["request_id"], "req-approval-final")
        self.assertEqual(final_audit.new_value_json["decision"], "approved")
        self.assertEqual(final_audit.new_value_json["comments"], "Director approval.")
        self.assertEqual(final_audit.old_value_json, {"current_status": "pending"})
        self.assertEqual(final_audit.new_value_json["current_status"], "approved")
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="sanction_approval", entity_id=self.case.pk
            ).count(),
            2,
        )
        notification = Notification.objects.get(
            related_entity_type="approval_case", related_entity_id=self.case.pk
        )
        self.assertEqual(notification.recipient_team_code, "credit_assessment")
        self.assertEqual(notification.sender_user, self.director)
        communication = Communication.objects.get(
            related_entity_type="approval_case", related_entity_id=self.case.pk
        )
        self.assertEqual(communication.delivery_status, Communication.DELIVERY_PENDING)
        self.assertEqual(communication.recipient_party_type, "team")
        self.assertEqual(communication.recipient_address, "credit_assessment")
        self.assertEqual(communication.channel, Communication.CHANNEL_EMAIL)
        self.assertEqual(notification.communication, communication)
        communication_audit = AuditLog.objects.get(
            action="communications.communication.created",
            entity_id=communication.pk,
        )
        self.assertNotIn("body_snapshot", communication_audit.new_value_json)
        self.assertEqual(
            communication_audit.new_value_json["delivery_status"], "pending"
        )

    def test_final_approval_publishes_immutable_register_and_sanction_decision_reads(self):
        sanction_read = self._permission("approvals.sanction.read")
        register_read = self._permission("approvals.sanction_register.read")
        RolePermission.objects.create(role=self.cfo.primary_role, permission=sanction_read)
        RolePermission.objects.create(role=self.cfo.primary_role, permission=register_read)
        self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2},
            content_type="application/json",
            **self._auth(self.cfo),
        )
        final = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 3, "comments": "Approved within authority."},
            content_type="application/json",
            **self._auth(self.director),
        )

        decision = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/sanction-decision/",
            **self._auth(self.cfo),
        )
        register = self.client.get(
            "/api/v1/credit-sanction-register/", **self._auth(self.cfo)
        )

        self.assertEqual(final.status_code, 200, final.json())
        self.assertEqual(decision.status_code, 200, decision.json())
        self.assertEqual(
            decision.json()["data"],
            {
                "sanction_decision_id": final.json()["data"]["sanction_decision_id"],
                "decision": "sanctioned",
                "sanctioned_amount": "500000.00",
                "sanctioned_tenure_months": 12,
                "interest_rate_type": "floating",
                "interest_rate_value": None,
                "repayment_date": None,
                "penal_interest_rate": None,
                "charges": {},
                "security_required_summary": "Standard member security package.",
                "conditions_precedent": None,
                "decision_reason": "Reviewed appraisal recommends approval.",
            },
        )
        self.assertEqual(register.status_code, 200, register.json())
        assert_pagination_shape(self, register.json())
        self.assertEqual(register.json()["pagination"]["total_count"], 1)
        row = register.json()["data"][0]
        self.assertEqual(row["approval_case_id"], str(self.case.pk))
        self.assertEqual(row["application_number"], "LO00000701")
        self.assertEqual(row["borrower_name"], "Approval Queue Member")
        self.assertEqual(row["borrower_type"], "individual_farmer")
        self.assertEqual(row["requested_amount"], "500000.00")
        self.assertEqual(row["eligible_amount"], "500000.00")
        self.assertEqual(row["recommended_amount"], "500000.00")
        self.assertEqual(row["sanctioned_amount"], "500000.00")
        self.assertEqual(row["decision"], "sanctioned")
        self.assertEqual(row["reasons"], "Reviewed appraisal recommends approval.")
        self.assertEqual(row["exception_reference"], None)
        self.assertEqual(row["conflict_abstention_details"], [])
        self.assertEqual(row["general_meeting_approval_reference"], None)
        self.assertEqual(len(row["approver_names"]), 2)
        register_model = apps.get_model("approvals", "CreditSanctionRegisterEntry")
        entry = register_model.objects.get(approval_case=self.case)
        self.assertEqual(register_model._meta.get_field("borrower_name").max_length, 255)
        self.assertEqual(str(entry.sanction_decision_id), decision.json()["data"]["sanction_decision_id"])
        with self.assertRaises(ValidationError):
            entry.save()
        with self.assertRaises(ValidationError):
            register_model.objects.filter(pk=entry.pk).update(reasons="Rewritten")
        with self.assertRaises(ValidationError):
            register_model.objects.filter(pk=entry.pk).delete()

    def test_same_permission_unassigned_director_cannot_read_sanction_decision(self):
        sanction_read = self._permission("approvals.sanction.read")
        RolePermission.objects.create(
            role=self.committee.director_2_user.primary_role,
            permission=sanction_read,
        )
        RolePermission.objects.create(
            role=self.director.primary_role,
            permission=sanction_read,
        )
        assigned_before_decision = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/sanction-decision/",
            **self._auth(self.director),
        )
        unrelated_before_decision = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/sanction-decision/",
            **self._auth(self.committee.director_2_user),
        )
        self.assertEqual(assigned_before_decision.status_code, 404)
        self.assertEqual(unrelated_before_decision.status_code, 403)
        assert_error_envelope(
            self, unrelated_before_decision.json(), "OBJECT_ACCESS_DENIED"
        )
        self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2},
            content_type="application/json",
            **self._auth(self.cfo),
        )
        final = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 3},
            content_type="application/json",
            **self._auth(self.director),
        )
        headers = self._auth(self.committee.director_2_user)
        before = self._action_ledgers()

        response = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/sanction-decision/",
            **headers,
        )

        self.assertEqual(final.status_code, 200, final.json())
        self.assertEqual(response.status_code, 403, response.json())
        assert_error_envelope(self, response.json(), "OBJECT_ACCESS_DENIED")
        self.assertEqual(self._action_ledgers(), before)

    def test_sanction_decision_uses_its_frozen_case_when_a_newer_cycle_exists(self):
        sanction_read = self._permission("approvals.sanction.read")
        RolePermission.objects.create(
            role=self.director.primary_role,
            permission=sanction_read,
        )
        self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2},
            content_type="application/json",
            **self._auth(self.cfo),
        )
        final = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 3},
            content_type="application/json",
            **self._auth(self.director),
        )
        later_review = AppraisalReviewDecision.objects.create(
            loan_appraisal_note=self.note,
            decision="reviewed",
            review_comments="Fresh review for the later immutable cycle.",
            reviewer_user=self.preparer,
            decided_at=timezone.now(),
            from_state=LoanAppraisalNote.STATUS_REVIEW_PENDING,
            to_state=LoanAppraisalNote.STATUS_REVIEWED,
        )
        later_cycle = ApprovalCase.objects.create(
            loan_application=self.application,
            loan_appraisal_note=self.note,
            submitted_by_user=self.preparer,
            submission_remarks="Newer cycle must not replace the frozen decision owner.",
            cycle_number=2,
            appraisal_revision=2,
            appraisal_review_decision=later_review,
            approval_matrix_rule=self.rule,
            approval_matrix_rule_version=self.rule.version_number,
            sanction_committee=self.committee,
            sanction_committee_version=self.committee.version_number,
            required_approvers_json=self.case.required_approvers_json,
            excluded_approvers_json=[],
            amount="500000.00",
            related_entity_type="loan_application",
            related_entity_id=self.application.pk,
            reason_for_approval="Later cycle recommendation.",
            matrix_projection_json=self.case.matrix_projection_json,
            committee_projection_json=self.case.committee_projection_json,
            loan_limit_provenance_json=self.case.loan_limit_provenance_json,
            decision_date=self.case.decision_date,
            version=2,
        )
        later_cycle.appraisal_facts_json = {
            **self.case.appraisal_facts_json,
            "snapshot_provenance": {
                **self.case.appraisal_facts_json["snapshot_provenance"],
                "review_decision_id": str(later_review.pk),
            },
        }
        later_cycle.save(update_fields=["appraisal_facts_json"])
        self.assertTrue(refresh_approval_case_projection(later_cycle))

        response = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/sanction-decision/",
            **self._auth(self.director),
        )

        self.assertEqual(final.status_code, 200, final.json())
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(
            response.json()["data"]["sanction_decision_id"],
            final.json()["data"]["sanction_decision_id"],
        )
        self.assertEqual(
            apps.get_model("approvals", "SanctionDecision")
            .objects.get(loan_application=self.application)
            .approval_case_id,
            self.case.pk,
        )

    def test_register_filters_counts_and_page_bounds_inside_director_object_scope(self):
        register_read = self._permission("approvals.sanction_register.read")
        RolePermission.objects.create(
            role=self.committee.director_2_user.primary_role,
            permission=register_read,
        )
        self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2},
            content_type="application/json",
            **self._auth(self.cfo),
        )
        final = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 3},
            content_type="application/json",
            **self._auth(self.director),
        )
        headers = self._auth(self.committee.director_2_user)
        before = self._action_ledgers()

        response = self.client.get(
            "/api/v1/credit-sanction-register/"
            "?decision=sanctioned&page=9&page_size=1",
            **headers,
        )

        self.assertEqual(final.status_code, 200, final.json())
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(response.json()["data"], [])
        self.assertEqual(
            response.json()["pagination"],
            {
                "page": 1,
                "page_size": 1,
                "total_count": 0,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False,
            },
        )
        self.assertEqual(self._action_ledgers(), before)

    def test_two_terminal_cases_keep_director_and_persisted_reader_scopes_distinct(self):
        sanction_read = self._permission("approvals.sanction.read")
        register_read = self._permission("approvals.sanction_register.read")
        second_director = self.committee.director_2_user
        for role in (self.director.primary_role, second_director.primary_role):
            RolePermission.objects.create(role=role, permission=sanction_read)
            RolePermission.objects.create(role=role, permission=register_read)
        for permission in (
            self.read_permission,
            self.approve_permission,
            self.reject_permission,
            self.return_permission,
        ):
            RolePermission.objects.create(
                role=second_director.primary_role,
                permission=permission,
            )
        second_case = self._create_second_routed_case(second_director)
        credit_manager = self._user(
            "credit_manager_scope",
            "Scoped Credit Manager",
            self.read_permission,
            self.application_read_permission,
        )
        credit_manager.primary_role.role_code = "credit_manager"
        credit_manager.primary_role.save(update_fields=["role_code"])
        second_case.submitted_by_user = credit_manager
        second_case.save(update_fields=["submitted_by_user"])

        for case, director in ((self.case, self.director), (second_case, second_director)):
            cfo_action = self.client.post(
                f"/api/v1/approval-cases/{case.pk}/approve/",
                {"version": 2},
                content_type="application/json",
                **self._auth(self.cfo),
            )
            final = self.client.post(
                f"/api/v1/approval-cases/{case.pk}/approve/",
                {"version": 3},
                content_type="application/json",
                **self._auth(director),
            )
            self.assertEqual(cfo_action.status_code, 200, cfo_action.json())
            self.assertEqual(final.status_code, 200, final.json())

        for director, own_case, other_case in (
            (self.director, self.case, second_case),
            (second_director, second_case, self.case),
        ):
            headers = self._auth(director)
            own_decision = self.client.get(
                f"/api/v1/loan-applications/{own_case.loan_application_id}/sanction-decision/",
                **headers,
            )
            other_decision = self.client.get(
                f"/api/v1/loan-applications/{other_case.loan_application_id}/sanction-decision/",
                **headers,
            )
            register = self.client.get(
                "/api/v1/credit-sanction-register/?decision=sanctioned&page_size=1&page=7",
                **headers,
            )
            self.assertEqual(own_decision.status_code, 200, own_decision.json())
            self.assertEqual(other_decision.status_code, 403, other_decision.json())
            assert_error_envelope(self, other_decision.json(), "OBJECT_ACCESS_DENIED")
            self.assertEqual(register.status_code, 200, register.json())
            self.assertEqual(register.json()["pagination"]["total_count"], 1)
            self.assertEqual(register.json()["pagination"]["total_pages"], 1)
            self.assertEqual(register.json()["pagination"]["page"], 1)
            self.assertEqual(
                register.json()["data"][0]["approval_case_id"], str(own_case.pk)
            )

        credit_headers = self._auth(credit_manager)
        credit_detail = self.client.get(
            f"/api/v1/approval-cases/{second_case.pk}/", **credit_headers
        )
        credit_decision_forbidden = self.client.get(
            f"/api/v1/loan-applications/{second_case.loan_application_id}/sanction-decision/",
            **credit_headers,
        )
        credit_register_forbidden = self.client.get(
            "/api/v1/credit-sanction-register/", **credit_headers
        )
        self.assertEqual(credit_detail.status_code, 200, credit_detail.json())
        self.assertEqual(credit_decision_forbidden.status_code, 403)
        self.assertEqual(credit_register_forbidden.status_code, 403)
        RolePermission.objects.create(
            role=credit_manager.primary_role, permission=sanction_read
        )
        RolePermission.objects.create(
            role=credit_manager.primary_role, permission=register_read
        )
        credit_decision = self.client.get(
            f"/api/v1/loan-applications/{second_case.loan_application_id}/sanction-decision/",
            **credit_headers,
        )
        credit_register = self.client.get(
            "/api/v1/credit-sanction-register/", **credit_headers
        )
        self.assertEqual(credit_decision.status_code, 200, credit_decision.json())
        self.assertEqual(credit_register.status_code, 200, credit_register.json())
        self.assertEqual(credit_register.json()["pagination"]["total_count"], 2)
        self.assertEqual(
            {row["approval_case_id"] for row in credit_register.json()["data"]},
            {str(self.case.pk), str(second_case.pk)},
        )

        for role_code, scope_type in (
            ("company_secretary", ApprovalCaseReadScopeGrant.SCOPE_LEGAL_READONLY),
            ("internal_auditor", ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY),
            (
                "persisted_management_reader",
                ApprovalCaseReadScopeGrant.SCOPE_MANAGEMENT_READONLY,
            ),
        ):
            with self.subTest(role_code=role_code):
                scoped_reader = self._user(
                    role_code,
                    f"{role_code} reader",
                    sanction_read,
                    register_read,
                )
                scoped_reader.primary_role.role_code = role_code
                scoped_reader.primary_role.save(update_fields=["role_code"])
                ApprovalCaseReadScopeGrant.objects.create(
                    role=scoped_reader.primary_role,
                    scope_type=scope_type,
                    status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
                )
                headers = self._auth(scoped_reader)
                register = self.client.get(
                    "/api/v1/credit-sanction-register/"
                    "?decision=sanctioned&page_size=1&page=2",
                    **headers,
                )
                self.assertEqual(register.status_code, 200, register.json())
                self.assertEqual(register.json()["pagination"]["total_count"], 2)
                self.assertEqual(register.json()["pagination"]["total_pages"], 2)
                self.assertEqual(register.json()["pagination"]["page"], 2)
                self.assertEqual(len(register.json()["data"]), 1)
                self.assertEqual(
                    {
                        self.client.get(
                            f"/api/v1/loan-applications/{case.loan_application_id}/sanction-decision/",
                            **headers,
                        ).status_code
                        for case in (self.case, second_case)
                    },
                    {200},
                )
                detail = self.client.get(
                    f"/api/v1/approval-cases/{second_case.pk}/", **headers
                )
                self.assertEqual(detail.status_code, 403, detail.json())
                assert_error_envelope(self, detail.json(), "FORBIDDEN")

    def test_malformed_frozen_terminal_case_fails_closed_at_every_read_boundary(self):
        sanction_read = self._permission("approvals.sanction.read")
        register_read = self._permission("approvals.sanction_register.read")
        for role in (self.cfo.primary_role, self.director.primary_role):
            RolePermission.objects.create(role=role, permission=sanction_read)
            RolePermission.objects.create(role=role, permission=register_read)
        cfo_headers = self._auth(self.cfo)
        first = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2},
            content_type="application/json",
            **cfo_headers,
        )
        final = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 3},
            content_type="application/json",
            **self._auth(self.director),
        )
        self.assertEqual(first.status_code, 200, first.json())
        self.assertEqual(final.status_code, 200, final.json())
        self.case.refresh_from_db()
        self.assertTrue(self.case.routing_snapshot_is_coherent)
        self.assertTrue(
            ApprovalCaseRequiredApprover.objects.filter(
                approval_case=self.case, user_id=self.cfo.pk
            ).exists()
        )

        malformed = dict(self.case.loan_limit_provenance_json)
        malformed["policy_name"] = ""
        self.case.loan_limit_provenance_json = malformed
        self.case.save(update_fields=["loan_limit_provenance_json"])
        ledgers_before = self._action_ledgers()

        detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **cfo_headers
        )
        collection = self.client.get("/api/v1/approval-cases/", **cfo_headers)
        action = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": self.case.version},
            content_type="application/json",
            **cfo_headers,
        )
        decision = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/sanction-decision/",
            **cfo_headers,
        )
        register = self.client.get(
            "/api/v1/credit-sanction-register/?decision=sanctioned&page=7&page_size=1",
            **cfo_headers,
        )

        self.assertEqual(detail.status_code, 404, detail.json())
        self.assertEqual(action.status_code, 404, action.json())
        self.assertEqual(collection.json()["data"], [])
        self.assertEqual(collection.json()["pagination"]["total_count"], 0)
        self.assertEqual(decision.status_code, 403, decision.json())
        assert_error_envelope(self, decision.json(), "OBJECT_ACCESS_DENIED")
        self.assertEqual(register.status_code, 200, register.json())
        self.assertEqual(register.json()["data"], [])
        self.assertEqual(register.json()["pagination"]["total_count"], 0)
        self.assertEqual(register.json()["pagination"]["total_pages"], 1)
        self.assertEqual(register.json()["pagination"]["page"], 1)
        self.assertEqual(self._action_ledgers(), ledgers_before)

    def test_missing_frozen_review_snapshot_fails_closed_before_reads_and_actions(self):
        self.case = ApprovalCase.objects.select_related(
            "loan_application", "loan_appraisal_note__risk_assessment"
        ).get(pk=self.case.pk)
        self.case.appraisal_facts_json = _project_review_facts(self.case)
        self.case.save(update_fields=["appraisal_facts_json"])
        refresh_approval_case_projection(self.case)
        self.case.refresh_from_db()
        self.assertTrue(self.case.routing_snapshot_is_coherent)

        ApprovalCase.objects.filter(pk=self.case.pk).update(appraisal_facts_json={})
        headers = self._auth(self.cfo)
        before = self._action_ledgers()

        collection = self.client.get("/api/v1/approval-cases/", **headers)
        detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **headers
        )
        action = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": self.case.version, "comments": "Must not use live review."},
            content_type="application/json",
            **headers,
        )

        self.assertEqual(collection.status_code, 200, collection.json())
        self.assertEqual(collection.json()["data"], [])
        self.assertEqual(collection.json()["pagination"]["total_count"], 0)
        self.assertEqual(detail.status_code, 404, detail.json())
        self.assertEqual(action.status_code, 404, action.json())
        self.assertEqual(self._action_ledgers(), before)

    def test_marked_review_snapshot_without_persisted_review_link_fails_closed(self):
        ApprovalCase.objects.filter(pk=self.case.pk).update(
            appraisal_review_decision=None,
            routing_snapshot_is_coherent=True,
        )

        response = self.client.get(
            "/api/v1/approval-cases/", **self._auth(self.cfo)
        )

        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(response.json()["data"], [])
        self.assertEqual(response.json()["pagination"]["total_count"], 0)

    def test_missing_terminal_review_snapshot_is_hidden_from_every_public_boundary(self):
        sanction_read = self._permission("approvals.sanction.read")
        sanction_register_read = self._permission(
            "approvals.sanction_register.read"
        )
        exception_register_read = self._permission(
            "approvals.exception_register.read"
        )
        for permission in (
            sanction_read,
            sanction_register_read,
            exception_register_read,
        ):
            RolePermission.objects.create(
                role=self.cfo.primary_role, permission=permission
            )
        ExceptionRegisterEntry.objects.create(
            loan_application=self.application,
            exception_type=ExceptionRegisterEntry.TYPE_WAIVER,
            description="A governed policy requirement was waived.",
            business_reason="Retained terminal evidence for boundary testing.",
            approval_case=self.case,
        )
        cfo_headers = self._auth(self.cfo)
        first = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2, "comments": "First frozen decision."},
            content_type="application/json",
            **cfo_headers,
        )
        final = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 3, "comments": "Terminal frozen decision."},
            content_type="application/json",
            **self._auth(self.director),
        )
        self.assertEqual(first.status_code, 200, first.json())
        self.assertEqual(final.status_code, 200, final.json())
        self.case.refresh_from_db()
        self.assertTrue(self.case.routing_snapshot_is_coherent)

        ApprovalCase.objects.filter(pk=self.case.pk).update(appraisal_facts_json={})
        before = self._action_ledgers()

        collection = self.client.get("/api/v1/approval-cases/", **cfo_headers)
        detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **cfo_headers
        )
        action = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": self.case.version, "comments": "Must remain hidden."},
            content_type="application/json",
            **cfo_headers,
        )
        decision = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/sanction-decision/",
            **cfo_headers,
        )
        sanction_register_response = self.client.get(
            "/api/v1/credit-sanction-register/", **cfo_headers
        )
        exception_register_response = self.client.get(
            "/api/v1/exception-register/", **cfo_headers
        )

        self.assertEqual(collection.json()["pagination"]["total_count"], 0)
        self.assertEqual(detail.status_code, 404, detail.json())
        self.assertEqual(action.status_code, 404, action.json())
        self.assertEqual(decision.status_code, 403, decision.json())
        self.assertEqual(
            sanction_register_response.json()["pagination"]["total_count"], 0
        )
        self.assertEqual(
            exception_register_response.json()["pagination"]["total_count"], 0
        )
        self.assertEqual(self._action_ledgers(), before)

    def test_partial_malformed_and_case_inconsistent_review_snapshots_fail_closed(self):
        review = self.review
        self.case.appraisal_review_decision = review
        self.case.save(update_fields=["appraisal_review_decision"])
        valid = self.case.appraisal_facts_json
        valid = {
            **valid,
            "snapshot_provenance": {
                **valid["snapshot_provenance"],
                "review_decision_id": str(review.pk),
            },
        }
        variants = {
            "legacy_unproven": {
                key: value
                for key, value in valid.items()
                if key not in {"snapshot_schema_version", "snapshot_provenance"}
            },
            "partial": {key: value for key, value in valid.items() if key != "risk"},
            "malformed": {**valid, "risk": ["not", "an", "object"]},
            "malformed_borrowing_history": {
                **valid,
                "borrowing_history": ["not", "text"],
            },
            "partial_eligibility": {**valid, "eligibility": {"document_check": "pass"}},
            "case_inconsistent": {
                **valid,
                "loan_amounts": {
                    **valid["loan_amounts"],
                    "recommended_amount": "499999.99",
                },
            },
            "review_inconsistent": {
                **valid,
                "maker_checker": {
                    **valid["maker_checker"],
                    "appraisal_reviewed_by_user_id": str(self.cfo.pk),
                },
            },
            "malformed_maker_id": {
                **valid,
                "maker_checker": {
                    **valid["maker_checker"],
                    "appraisal_prepared_by_user_id": {"not": "an identifier"},
                },
            },
            "malformed_eligibility_check": {
                **valid,
                "eligibility": {
                    **valid["eligibility"],
                    "nominee_check": ["not", "a", "scalar"],
                },
            },
            "malformed_assessed_at": {
                **valid,
                "eligibility": {
                    **valid["eligibility"],
                    "assessed_at": "not-a-timestamp",
                },
            },
            "malformed_risk_rating": {
                **valid,
                "risk": {
                    **valid["risk"],
                    "overall_risk_rating": ["not", "a", "scalar"],
                },
            },
        }
        headers = self._auth(self.cfo)
        for label, snapshot in variants.items():
            with self.subTest(label=label):
                ApprovalCase.objects.filter(pk=self.case.pk).update(
                    appraisal_facts_json=snapshot,
                    routing_snapshot_is_coherent=True,
                )
                response = self.client.get("/api/v1/approval-cases/", **headers)
                self.assertEqual(response.status_code, 200, response.json())
                self.assertEqual(response.json()["data"], [])
                self.assertEqual(response.json()["pagination"]["total_count"], 0)

    def test_live_appraisal_change_preserves_terminal_detail_decision_and_register(self):
        sanction_read = self._permission("approvals.sanction.read")
        register_read = self._permission("approvals.sanction_register.read")
        for role in (self.cfo.primary_role, self.director.primary_role):
            RolePermission.objects.create(role=role, permission=sanction_read)
            RolePermission.objects.create(role=role, permission=register_read)
        self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2},
            content_type="application/json",
            **self._auth(self.cfo),
        )
        final = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 3},
            content_type="application/json",
            **self._auth(self.director),
        )
        self.assertEqual(final.status_code, 200, final.json())
        headers = self._auth(self.cfo)
        detail_before = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **headers
        ).json()["data"]
        decision_before = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/sanction-decision/",
            **headers,
        ).json()["data"]
        register_before = self.client.get(
            "/api/v1/credit-sanction-register/", **headers
        ).json()

        live_snapshot = dict(self.note.loan_limit_snapshot_json)
        live_snapshot["policy_name"] = "Policy amended after terminal decision"
        self.note.loan_limit_snapshot_json = live_snapshot
        self.note.recommended_amount = "1.00"
        self.note.borrower_summary = "Mutable appraisal changed after terminal decision."
        self.note.save(
            update_fields=[
                "loan_limit_snapshot_json",
                "recommended_amount",
                "borrower_summary",
            ]
        )
        self.application.declared_purpose = "Mutable purpose changed after decision"
        self.application.save(update_fields=["declared_purpose"])
        self.risk.overall_risk_rating = "high"
        self.risk.save(update_fields=["overall_risk_rating"])

        detail_after = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **headers
        )
        decision_after = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/sanction-decision/",
            **headers,
        )
        register_after = self.client.get(
            "/api/v1/credit-sanction-register/", **headers
        )
        self.assertEqual(detail_after.status_code, 200, detail_after.json())
        self.assertEqual(decision_after.status_code, 200, decision_after.json())
        self.assertEqual(register_after.status_code, 200, register_after.json())
        self.assertEqual(detail_after.json()["data"], detail_before)
        self.assertEqual(decision_after.json()["data"], decision_before)
        self.assertEqual(register_after.json()["data"], register_before["data"])
        self.assertEqual(
            register_after.json()["pagination"], register_before["pagination"]
        )

    def test_rejected_and_returned_cycles_do_not_leak_decision_or_register_existence(self):
        sanction_read = self._permission("approvals.sanction.read")
        register_read = self._permission("approvals.sanction_register.read")
        second_director = self.committee.director_2_user
        second_case = self._create_second_routed_case(second_director)
        for role in (
            self.cfo.primary_role,
            self.director.primary_role,
            second_director.primary_role,
        ):
            RolePermission.objects.create(role=role, permission=sanction_read)
            RolePermission.objects.create(role=role, permission=register_read)
        rejected = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/reject/",
            {"version": 2, "comments": "Rejected scoped cycle."},
            content_type="application/json",
            **self._auth(self.cfo),
        )
        returned = self.client.post(
            f"/api/v1/approval-cases/{second_case.pk}/return-for-clarification/",
            {"version": 2, "comments": "Return scoped cycle."},
            content_type="application/json",
            **self._auth(self.cfo),
        )
        self.assertEqual(rejected.status_code, 200, rejected.json())
        self.assertEqual(returned.status_code, 200, returned.json())

        for director, own_case, other_case, expected_register_count in (
            (self.director, self.case, second_case, 1),
            (second_director, second_case, self.case, 0),
        ):
            headers = self._auth(director)
            own_decision = self.client.get(
                f"/api/v1/loan-applications/{own_case.loan_application_id}/sanction-decision/",
                **headers,
            )
            other_decision = self.client.get(
                f"/api/v1/loan-applications/{other_case.loan_application_id}/sanction-decision/",
                **headers,
            )
            register = self.client.get(
                "/api/v1/credit-sanction-register/", **headers
            )
            self.assertEqual(own_decision.status_code, 404, own_decision.json())
            self.assertEqual(other_decision.status_code, 403, other_decision.json())
            assert_error_envelope(self, other_decision.json(), "OBJECT_ACCESS_DENIED")
            self.assertEqual(
                register.json()["pagination"]["total_count"], expected_register_count
            )

        cfo_headers = self._auth(self.cfo)
        self.assertEqual(
            {
                self.client.get(
                    f"/api/v1/loan-applications/{case.loan_application_id}/sanction-decision/",
                    **cfo_headers,
                ).status_code
                for case in (self.case, second_case)
            },
            {404},
        )
        cfo_register = self.client.get(
            "/api/v1/credit-sanction-register/", **cfo_headers
        )
        self.assertEqual(cfo_register.json()["pagination"]["total_count"], 1)
        self.assertEqual(
            {row["decision"] for row in cfo_register.json()["data"]}, {"rejected"}
        )

    def test_rejection_registers_once_without_inventing_a_sanction_decision(self):
        sanction_read = self._permission("approvals.sanction.read")
        RolePermission.objects.create(role=self.cfo.primary_role, permission=sanction_read)

        rejected = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/reject/",
            {"version": 2, "comments": "Repayment capacity is insufficient."},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-register-rejected",
            **self._auth(self.cfo),
        )
        retried = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/reject/",
            {"version": 2, "comments": "Repayment capacity is insufficient."},
            content_type="application/json",
            **self._auth(self.cfo),
        )
        decision = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/sanction-decision/",
            **self._auth(self.cfo),
        )

        self.assertEqual(rejected.status_code, 200, rejected.json())
        self.assertEqual(retried.status_code, 409, retried.json())
        assert_error_envelope(self, retried.json(), "STALE_VERSION")
        self.assertEqual(decision.status_code, 404, decision.json())
        assert_error_envelope(self, decision.json(), "NOT_FOUND")
        register_model = apps.get_model("approvals", "CreditSanctionRegisterEntry")
        self.assertEqual(register_model.objects.filter(approval_case=self.case).count(), 1)
        entry = register_model.objects.get(approval_case=self.case)
        self.assertEqual(entry.decision, "rejected")
        self.assertIsNone(entry.sanction_decision_id)
        self.assertEqual(entry.sanctioned_amount, None)
        self.assertEqual(entry.reasons, "Repayment capacity is insufficient.")
        audit = AuditLog.objects.get(action="credit_sanction_register.created")
        self.assertEqual(audit.entity_id, entry.pk)
        self.assertEqual(audit.new_value_json["request_id"], "req-register-rejected")
        self.assertEqual(
            audit.new_value_json["workflow_event_id"], str(entry.workflow_event_id)
        )
        self.assertEqual(entry.workflow_event.entity_id, self.case.pk)

    def test_register_freezes_same_case_exception_abstention_and_meeting_references(self):
        register_read = self._permission("approvals.sanction_register.read")
        sanction_read = self._permission("approvals.sanction.read")
        RolePermission.objects.create(role=self.cfo.primary_role, permission=register_read)
        exception = ExceptionRegisterEntry.objects.create(
            loan_application=self.application,
            exception_type="waiver",
            description="A governed policy requirement was waived.",
            business_reason="Committee approved a documented waiver.",
            approval_case=self.case,
        )
        recorder, payload = self._general_meeting_recorder_and_payload()
        meeting_response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/general-meeting-approval/",
            payload,
            content_type="application/json",
            **self._auth(recorder),
        )
        self.assertEqual(meeting_response.status_code, 200, meeting_response.json())
        meeting = meeting_response.json()["data"]
        alternate = self.committee.director_2_user
        for permission in (
            self.read_permission,
            self.approve_permission,
            self.reject_permission,
            self.return_permission,
            register_read,
            sanction_read,
        ):
            RolePermission.objects.create(role=alternate.primary_role, permission=permission)
        RolePermission.objects.create(
            role=self.director.primary_role, permission=register_read
        )
        RolePermission.objects.create(
            role=self.director.primary_role, permission=sanction_read
        )
        abstained = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/abstain/",
            {"version": 2, "comments": "Borrower is my relative."},
            content_type="application/json",
            **self._auth(self.director),
        )
        self.assertEqual(abstained.status_code, 200, abstained.json())
        self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 3},
            content_type="application/json",
            **self._auth(self.cfo),
        )
        final = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 4},
            content_type="application/json",
            **self._auth(alternate),
        )
        register = self.client.get(
            "/api/v1/credit-sanction-register/", **self._auth(self.cfo)
        )
        historical_reads = []
        for reader in (self.director, alternate):
            headers = self._auth(reader)
            historical_reads.append(
                (
                    self.client.get(
                        f"/api/v1/loan-applications/{self.application.pk}/sanction-decision/",
                        **headers,
                    ),
                    self.client.get(
                        "/api/v1/credit-sanction-register/", **headers
                    ),
                )
            )

        self.assertEqual(final.status_code, 200, final.json())
        self.assertEqual(register.status_code, 200, register.json())
        row = register.json()["data"][0]
        self.assertEqual(row["reasons"], self.case.reason_for_approval)
        self.assertNotEqual(row["reasons"], exception.business_reason)
        for decision_read, register_read_response in historical_reads:
            self.assertEqual(decision_read.status_code, 200, decision_read.json())
            self.assertEqual(
                decision_read.json()["data"]["decision_reason"],
                self.case.reason_for_approval,
            )
            self.assertEqual(register_read_response.status_code, 200)
            self.assertEqual(
                register_read_response.json()["pagination"]["total_count"], 1
            )
        self.assertIn(f"Director: {alternate.full_name} (approved)", row["approval_authority"])
        self.assertEqual(row["approver_names"], [self.cfo.full_name, alternate.full_name])
        self.assertEqual(
            row["exception_reference"],
            {
                "exception_register_entry_id": str(exception.pk),
                "exception_type": "waiver",
                "business_reason": "Committee approved a documented waiver.",
                "status": "approved",
                "cycle_number": 1,
            },
        )
        self.assertEqual(
            row["conflict_abstention_details"],
            [
                {
                    "type": "abstention",
                    "user_id": str(self.director.pk),
                    "full_name": self.director.full_name,
                    "conflict_code": "self_declared_abstention",
                    "reason": "Borrower is my relative.",
                    "approval_action_id": abstained.json()["data"]["approval_action_id"],
                    "acted_at": abstained.json()["data"]["approval_actions"][0]["acted_at"],
                }
            ],
        )
        self.assertEqual(
            row["general_meeting_approval_reference"],
            {
                "general_meeting_approval_id": meeting["general_meeting_approval_id"],
                "approval_status": "approved",
                "meeting_date": meeting["meeting_date"],
                "related_party_type": "director_relative",
                "related_party_user_id": str(self.director.pk),
                "notice_document_id": meeting["notice_document_id"],
                "minutes_document_id": meeting["minutes_document_id"],
                "resolution_document_id": meeting["resolution_document_id"],
            },
        )

    def test_register_filters_pagination_permissions_and_read_only_routes(self):
        register_read = self._permission("approvals.sanction_register.read")
        sanction_read = self._permission("approvals.sanction.read")
        RolePermission.objects.create(role=self.cfo.primary_role, permission=register_read)
        RolePermission.objects.create(role=self.cfo.primary_role, permission=sanction_read)
        rejected = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/reject/",
            {"version": 2, "comments": "Risk appetite does not permit approval."},
            content_type="application/json",
            **self._auth(self.cfo),
        )
        self.assertEqual(rejected.status_code, 200, rejected.json())
        entry = apps.get_model("approvals", "CreditSanctionRegisterEntry").objects.get()
        financial_year = (
            f"FY{entry.approval_date.year}-{str(entry.approval_date.year + 1)[-2:]}"
            if entry.approval_date.month >= 4
            else f"FY{entry.approval_date.year - 1}-{str(entry.approval_date.year)[-2:]}"
        )

        allowed = self.client.get(
            f"/api/v1/credit-sanction-register/?financial_year={financial_year}"
            "&decision=rejected&page=1&page_size=1",
            **self._auth(self.cfo),
        )
        wrong_decision = self.client.get(
            f"/api/v1/credit-sanction-register/?financial_year={financial_year}"
            "&decision=sanctioned",
            **self._auth(self.cfo),
        )
        invalid_year = self.client.get(
            "/api/v1/credit-sanction-register/?financial_year=2026-27",
            **self._auth(self.cfo),
        )
        invalid_decision = self.client.get(
            "/api/v1/credit-sanction-register/?decision=maybe",
            **self._auth(self.cfo),
        )
        invalid_year_range = self.client.get(
            "/api/v1/credit-sanction-register/?financial_year=FY0000-01",
            **self._auth(self.cfo),
        )
        forbidden_register = self.client.get(
            "/api/v1/credit-sanction-register/", **self._auth(self.director)
        )
        forbidden_decision = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/sanction-decision/",
            **self._auth(self.director),
        )
        unauthenticated = self.client.get("/api/v1/credit-sanction-register/")
        post_register = self.client.post(
            "/api/v1/credit-sanction-register/", {}, content_type="application/json",
            **self._auth(self.cfo),
        )
        put_register = self.client.put(
            f"/api/v1/credit-sanction-register/{entry.pk}/",
            {},
            content_type="application/json",
            **self._auth(self.cfo),
        )

        self.assertEqual(allowed.status_code, 200, allowed.json())
        self.assertEqual(allowed.json()["pagination"]["page_size"], 1)
        self.assertEqual(allowed.json()["pagination"]["total_count"], 1)
        self.assertEqual(allowed.json()["data"][0]["approval_date"], entry.approval_date.isoformat())
        self.assertEqual(wrong_decision.json()["pagination"]["total_count"], 0)
        self.assertEqual(invalid_year.status_code, 400, invalid_year.json())
        assert_error_envelope(self, invalid_year.json(), "VALIDATION_ERROR")
        self.assertIn("financial_year", invalid_year.json()["error"]["field_errors"])
        self.assertEqual(invalid_decision.status_code, 400, invalid_decision.json())
        assert_error_envelope(self, invalid_decision.json(), "VALIDATION_ERROR")
        self.assertIn("decision", invalid_decision.json()["error"]["field_errors"])
        self.assertEqual(invalid_year_range.status_code, 400, invalid_year_range.json())
        self.assertIn(
            "financial_year", invalid_year_range.json()["error"]["field_errors"]
        )
        self.assertEqual(forbidden_register.status_code, 403, forbidden_register.json())
        self.assertEqual(forbidden_decision.status_code, 403, forbidden_decision.json())
        self.assertEqual(unauthenticated.status_code, 401, unauthenticated.json())
        self.assertEqual(post_register.status_code, 405)
        self.assertEqual(put_register.status_code, 404)
        with self.assertRaises(ValidationError):
            entry.delete()

    def test_final_action_collection_detail_and_action_share_history_aware_projection(self):
        self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2}, content_type="application/json", **self._auth(self.cfo),
        )
        action_response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 3}, content_type="application/json", **self._auth(self.director),
        )
        detail_response = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **self._auth(self.director)
        )
        collection_response = self.client.get(
            "/api/v1/approval-cases/", **self._auth(self.director)
        )

        self.assertEqual(action_response.status_code, 200)
        action_data = action_response.json()["data"]
        detail_data = detail_response.json()["data"]
        collection_data = collection_response.json()["data"][0]
        shared_fields = (
            "current_status", "version", "approval_matrix_rule_id",
            "approval_matrix_rule_version", "sanction_committee_id",
            "sanction_committee_version", "required_approvers",
            "excluded_approvers", "available_actions",
        )
        expected = {field: action_data[field] for field in shared_fields}
        self.assertEqual({field: detail_data[field] for field in shared_fields}, expected)
        self.assertEqual({field: collection_data[field] for field in shared_fields}, expected)
        self.assertEqual(
            [item["decision"] for item in collection_data["required_approvers"]],
            ["approved", "approved"],
        )

    def test_reject_requires_comments_before_any_ledger_write(self):
        auth = self._auth(self.cfo)
        before = self._action_ledgers()
        response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/reject/",
            {"version": 2, "comments": "   "},
            content_type="application/json",
            **auth,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "VALIDATION_ERROR")
        self.assertIn("comments", response.json()["error"]["field_errors"])
        self.assertEqual(self._action_ledgers(), before)

    def test_reject_missing_comment_is_validation_error_without_writes(self):
        auth = self._auth(self.cfo)
        before = self._action_ledgers()
        response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/reject/",
            {"version": 2}, content_type="application/json", **auth,
        )
        self.assertEqual(response.status_code, 400)
        assert_error_envelope(self, response.json(), "VALIDATION_ERROR")
        self.assertEqual(self._action_ledgers(), before)

    def test_reject_closes_case_and_application_without_sanction(self):
        entry = ExceptionRegisterEntry.objects.create(
            loan_application=self.application,
            exception_type="exceeds_loan_limit",
            description="Frozen permissible limit exceeded.",
            business_reason="Exception requires joint authority.",
            approval_case=self.case,
        )
        response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/reject/",
            {"version": 2, "comments": "Eligibility evidence is insufficient."},
            content_type="application/json",
            **self._auth(self.cfo),
        )
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(response.json()["data"]["current_status"], "rejected")
        self.assertFalse(response.json()["data"]["sanction_decision_created"])
        self.case.refresh_from_db()
        self.application.refresh_from_db()
        self.assertEqual(self.case.reason_for_rejection, "Eligibility evidence is insufficient.")
        self.assertEqual(self.application.application_status, "rejected_by_sanction_committee")
        entry.refresh_from_db()
        self.assertEqual(entry.status, "rejected")
        self.assertEqual(entry.closed_at, self.case.closed_at)

    def test_return_restores_reviewed_precommittee_state_without_sanction(self):
        entry = ExceptionRegisterEntry.objects.create(
            loan_application=self.application,
            exception_type="waiver",
            description="A governed policy requirement was waived.",
            business_reason="Clarification may change exception evidence.",
            approval_case=self.case,
        )
        response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/return-for-clarification/",
            {"version": 2, "comments": "Clarify crop plan evidence."},
            content_type="application/json",
            **self._auth(self.director),
        )
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(response.json()["data"]["current_status"], "returned_for_clarification")
        self.application.refresh_from_db()
        self.note.refresh_from_db()
        self.assertEqual(self.application.application_status, "appraisal_reviewed")
        self.assertEqual(self.note.appraisal_status, "draft")
        self.assertFalse(apps.get_model("approvals", "SanctionDecision").objects.exists())
        self.case.refresh_from_db()
        entry.refresh_from_db()
        self.assertEqual(entry.status, "pending")
        self.assertEqual(entry.closed_at, self.case.closed_at)

    def test_return_correction_fresh_review_creates_immutable_second_cycle(self):
        self.note.refresh_from_db()
        self.case.refresh_from_db()
        self.case.appraisal_facts_json = _project_review_facts(self.case)
        self.case.save(update_fields=["appraisal_facts_json"])
        refresh_approval_case_projection(self.case)
        cycle_one_provenance = dict(self.case.loan_limit_provenance_json)
        cycle_one_appraisal_facts = dict(self.case.appraisal_facts_json)
        returned = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/return-for-clarification/",
            {"version": 2, "comments": "Clarify crop plan evidence."},
            content_type="application/json",
            **self._auth(self.director),
        )
        self.assertEqual(returned.status_code, 200, returned.json())
        cycle_one = ApprovalCase.objects.get(pk=self.case.pk)
        cycle_one.excluded_approvers_json = [
            {
                "user_id": str(self.director.pk),
                "conflict_code": "self_declared_abstention",
                "reason": "Cycle-one conflict history.",
            }
        ]
        cycle_one.save(update_fields=["excluded_approvers_json"])
        self.note.eligibility_snapshot_json = {
            **self.note.eligibility_snapshot_json,
            "eligibility_assessment_id": str(
                self.note.eligibility_assessment_id_snapshot
            ),
            "loan_application_id": str(self.application.pk),
        }
        self.note.save(update_fields=["eligibility_snapshot_json"])
        cycle_one_ledger = {
            "case": ApprovalCase.objects.filter(pk=cycle_one.pk).values().get(),
            "actions": list(cycle_one.actions.order_by("pk").values()),
            "audits": list(
                AuditLog.objects.filter(entity_id=cycle_one.pk).order_by("pk").values()
            ),
            "workflows": list(
                WorkflowEvent.objects.filter(entity_id=cycle_one.pk).order_by("pk").values()
            ),
            "communications": list(
                Communication.objects.filter(related_entity_id=cycle_one.pk)
                .order_by("pk")
                .values()
            ),
        }

        AppraisalWorkflow().create_or_update(
            actor=self.preparer,
            application_id=self.application.pk,
            payload={"borrower_summary": "Corrected crop plan and borrowing history."},
            partial=True,
            actor_permissions={"credit.appraisal.update"},
        )
        AppraisalWorkflow().submit_for_review(
            actor=self.preparer,
            appraisal_id=self.note.pk,
            payload={"remarks": "Corrected facts ready for independent review."},
            actor_permissions={"credit.appraisal.submit_review"},
        )
        reviewer = self._user("credit_manager", "Second-cycle Credit Manager")
        reviewer.primary_role.role_code = "credit_manager"
        reviewer.primary_role.save(update_fields=["role_code"])
        AppraisalWorkflow().review(
            actor=reviewer,
            appraisal_id=self.note.pk,
            decision="reviewed",
            comments="Corrected facts independently reviewed.",
            payload_fields={"decision": "reviewed", "review_comments": "Corrected facts independently reviewed."},
            actor_permissions={"credit.appraisal.review"},
        )
        submitted = SanctionHandoffModule().submit_reviewed_appraisal(
            actor=reviewer,
            application_id=self.application.pk,
            payload={"remarks": "Resubmit corrected appraisal."},
            actor_permissions={"credit.appraisal.submit_sanction"},
        ).snapshot
        cycle_two = ApprovalCase.objects.get(pk=submitted["approval_case_id"])
        ApprovalMatrixRule.objects.exclude(pk=self.rule.pk).update(status="inactive")
        SanctionCommittee.objects.exclude(pk=self.committee.pk).update(status="inactive")
        enriched = SanctionHandoffModule().enrich_pending(
            actor=reviewer,
            application_id=self.application.pk,
            payload={
                "approval_type": "sanction",
                "amount": "500000.00",
                "reason_for_approval": "Corrected appraisal recommends approval.",
                "force_exception_route": False,
            },
            actor_permissions={"approvals.case.create"},
        ).snapshot
        self.assertEqual(enriched["cycle_number"], 2)
        self.assertEqual(enriched["excluded_approvers"], [])
        returned_history = self.client.get(
            f"/api/v1/approval-cases/{cycle_one.pk}/", **self._auth(self.director)
        )
        current_queue = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true", **self._auth(self.cfo)
        )
        self.assertEqual(returned_history.status_code, 200, returned_history.json())
        self.assertEqual(returned_history.json()["data"]["cycle_number"], 1)
        self.assertEqual(
            returned_history.json()["data"]["loan_limit_provenance"],
            cycle_one_provenance,
        )
        self.assertEqual(
            returned_history.json()["data"]["review_facts"],
            cycle_one_appraisal_facts,
        )
        self.assertTrue(
            all(
                not action["enabled"]
                for action in returned_history.json()["data"]["available_actions"]
            )
        )
        self.assertEqual(
            [item["cycle_number"] for item in current_queue.json()["data"]], [2]
        )
        self.assertEqual(
            current_queue.json()["data"][0]["review_facts"]["borrowing_history"],
            "Corrected crop plan and borrowing history.",
        )
        self.assertNotEqual(
            current_queue.json()["data"][0]["review_facts"], cycle_one_appraisal_facts
        )
        company_secretary = self._user(
            "company_secretary", "Cycle-history Company Secretary", self.read_permission
        )
        auditor = self._user(
            "internal_auditor", "Cycle-history Auditor", self.read_permission
        )
        ApprovalCaseReadScopeGrant.objects.create(
            role=company_secretary.primary_role,
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_LEGAL_READONLY,
        )
        ApprovalCaseReadScopeGrant.objects.create(
            role=auditor.primary_role,
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
        )
        for reader in (company_secretary, auditor):
            history = self.client.get("/api/v1/approval-cases/", **self._auth(reader))
            assigned = self.client.get(
                "/api/v1/approval-cases/?assigned_to_me=true", **self._auth(reader)
            )
            self.assertEqual(
                [item["cycle_number"] for item in history.json()["data"]], [2, 1]
            )
            self.assertEqual(assigned.json()["pagination"]["total_count"], 0)
        permission_only = self._user(
            "permission_only_cycle_reader",
            "Permission-only Cycle Reader",
            self.read_permission,
        )
        excluded = self.client.get(
            "/api/v1/approval-cases/", **self._auth(permission_only)
        )
        self.assertEqual(excluded.json()["pagination"]["total_count"], 0)
        first_approval = approval_actions.approve_case(
            actor=self.cfo,
            case_id=cycle_two.pk,
            payload={"version": 2, "comments": "Corrected cycle approved."},
            actor_permissions={"approvals.case.approve", "approvals.case.read"},
        )
        self.assertEqual(first_approval["current_status"], "pending")
        self.assertEqual(first_approval["cycle_number"], 2)
        final_approval = approval_actions.approve_case(
            actor=self.director,
            case_id=cycle_two.pk,
            payload={"version": 3, "comments": "Fresh cycle jointly approved."},
            actor_permissions={"approvals.case.approve", "approvals.case.read"},
        )
        self.assertEqual(final_approval["current_status"], "approved")
        self.assertTrue(final_approval["sanction_decision_created"])
        cycle_two.refresh_from_db()
        self.assertEqual((cycle_one.cycle_number, cycle_two.cycle_number), (1, 2))
        self.assertNotEqual(cycle_one.pk, cycle_two.pk)
        self.assertEqual(cycle_two.appraisal_revision, 2)
        self.assertEqual(
            cycle_two.appraisal_review_decision_id,
            AppraisalReviewDecision.objects.latest("decided_at").pk,
        )
        self.assertEqual(cycle_two.sanction_decision.loan_application_id, self.application.pk)
        self.assertEqual(
            {
                "case": ApprovalCase.objects.filter(pk=cycle_one.pk).values().get(),
                "actions": list(cycle_one.actions.order_by("pk").values()),
                "audits": list(
                    AuditLog.objects.filter(entity_id=cycle_one.pk).order_by("pk").values()
                ),
                "workflows": list(
                    WorkflowEvent.objects.filter(entity_id=cycle_one.pk).order_by("pk").values()
                ),
                "communications": list(
                    Communication.objects.filter(related_entity_id=cycle_one.pk)
                    .order_by("pk")
                    .values()
                ),
            },
            cycle_one_ledger,
        )

    def test_fresh_review_without_correction_cannot_create_a_second_cycle(self):
        returned = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/return-for-clarification/",
            {"version": 2, "comments": "Clarify the unchanged facts."},
            content_type="application/json",
            **self._auth(self.director),
        )
        self.assertEqual(returned.status_code, 200, returned.json())
        self.note.eligibility_snapshot_json = {
            **self.note.eligibility_snapshot_json,
            "eligibility_assessment_id": str(
                self.note.eligibility_assessment_id_snapshot
            ),
            "loan_application_id": str(self.application.pk),
        }
        self.note.save(update_fields=["eligibility_snapshot_json"])
        AppraisalWorkflow().create_or_update(
            actor=self.preparer,
            application_id=self.application.pk,
            payload={"borrower_summary": self.note.borrower_summary},
            partial=True,
            actor_permissions={"credit.appraisal.update"},
        )
        AppraisalWorkflow().submit_for_review(
            actor=self.preparer,
            appraisal_id=self.note.pk,
            payload={"remarks": "No material correction was supplied."},
            actor_permissions={"credit.appraisal.submit_review"},
        )
        reviewer = self._user("credit_manager", "No-correction Credit Manager")
        reviewer.primary_role.role_code = "credit_manager"
        reviewer.primary_role.save(update_fields=["role_code"])
        AppraisalWorkflow().review(
            actor=reviewer,
            appraisal_id=self.note.pk,
            decision="reviewed",
            comments="Fresh review of unchanged facts.",
            payload_fields={
                "decision": "reviewed",
                "review_comments": "Fresh review of unchanged facts.",
            },
            actor_permissions={"credit.appraisal.review"},
        )
        before = self._action_ledgers()

        with self.assertRaisesMessage(
            DomainInvalidStateError,
            "A returned appraisal must be corrected before resubmission.",
        ):
            SanctionHandoffModule().submit_reviewed_appraisal(
                actor=reviewer,
                application_id=self.application.pk,
                payload={"remarks": "Attempt unchanged resubmission."},
                actor_permissions={"credit.appraisal.submit_sanction"},
            )

        self.assertEqual(ApprovalCase.objects.count(), 1)
        self.assertEqual(self._action_ledgers(), before)

    def test_correction_without_fresh_review_cannot_create_a_second_cycle(self):
        returned = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/return-for-clarification/",
            {"version": 2, "comments": "Correct and obtain a fresh review."},
            content_type="application/json",
            **self._auth(self.director),
        )
        self.assertEqual(returned.status_code, 200, returned.json())
        AppraisalWorkflow().create_or_update(
            actor=self.preparer,
            application_id=self.application.pk,
            payload={"borrower_summary": "Corrected but not freshly reviewed."},
            partial=True,
            actor_permissions={"credit.appraisal.update"},
        )
        reviewer = self._user("credit_manager", "Missing-fresh-review Manager")
        reviewer.primary_role.role_code = "credit_manager"
        reviewer.primary_role.save(update_fields=["role_code"])
        before = self._action_ledgers()

        with self.assertRaisesMessage(
            DomainInvalidStateError,
            "Only a reviewed appraisal note can be submitted for sanction.",
        ):
            SanctionHandoffModule().submit_reviewed_appraisal(
                actor=reviewer,
                application_id=self.application.pk,
                payload={"remarks": "Attempt without the required fresh review."},
                actor_permissions={"credit.appraisal.submit_sanction"},
            )

        self.assertEqual(ApprovalCase.objects.count(), 1)
        self.assertEqual(self._action_ledgers(), before)

    def test_pending_approved_and_rejected_cycles_deny_resubmission_without_writes(self):
        reviewer = self._user("credit_manager", "Lifecycle Credit Manager")
        reviewer.primary_role.role_code = "credit_manager"
        reviewer.primary_role.save(update_fields=["role_code"])
        reviewed_at = timezone.now()
        self.note.appraisal_status = LoanAppraisalNote.STATUS_REVIEWED
        self.note.reviewed_by_user = reviewer
        self.note.reviewed_at = reviewed_at
        self.note.review_comments = "Lifecycle matrix review."
        self.note.last_review_decision = "reviewed"
        self.note.eligibility_snapshot_json = {
            **self.note.eligibility_snapshot_json,
            "eligibility_assessment_id": str(
                self.note.eligibility_assessment_id_snapshot
            ),
            "loan_application_id": str(self.application.pk),
        }
        self.note.save()
        AppraisalReviewDecision.objects.create(
            loan_appraisal_note=self.note,
            decision="reviewed",
            review_comments=self.note.review_comments,
            reviewer_user=reviewer,
            decided_at=reviewed_at,
            from_state="review_pending",
            to_state=LoanAppraisalNote.STATUS_REVIEWED,
        )

        for status in (
            ApprovalCase.STATUS_PENDING,
            ApprovalCase.STATUS_APPROVED,
            ApprovalCase.STATUS_REJECTED,
        ):
            with self.subTest(status=status):
                self.case.current_status = status
                self.case.closed_at = (
                    None if status == ApprovalCase.STATUS_PENDING else timezone.now()
                )
                self.case.save(update_fields=["current_status", "closed_at"])
                before = self._action_ledgers()

                with self.assertRaisesMessage(
                    DomainInvalidStateError,
                    "Only a returned approval cycle can be resubmitted.",
                ):
                    SanctionHandoffModule().submit_reviewed_appraisal(
                        actor=reviewer,
                        application_id=self.application.pk,
                        payload={"remarks": f"Do not resubmit {status}."},
                        actor_permissions={"credit.appraisal.submit_sanction"},
                    )

                self.assertEqual(ApprovalCase.objects.count(), 1)
                self.assertEqual(self._action_ledgers(), before)

    def test_action_rejects_mismatched_application_transition_without_writes(self):
        self.application.application_status = LoanApplication.STATUS_APPRAISAL_REVIEWED
        self.application.save(update_fields=["application_status"])
        auth = self._auth(self.cfo)
        before = self._action_ledgers()

        response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2}, content_type="application/json", **auth,
        )

        self.assertEqual(response.status_code, 409)
        assert_error_envelope(self, response.json(), "TRANSITION_CONFLICT")
        self.assertEqual(self._action_ledgers(), before)

    def test_action_rejects_mismatched_appraisal_transition_without_writes(self):
        self.note.appraisal_status = LoanAppraisalNote.STATUS_REVIEWED
        self.note.save(update_fields=["appraisal_status"])
        auth = self._auth(self.cfo)
        before = self._action_ledgers()

        response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2}, content_type="application/json", **auth,
        )

        self.assertEqual(response.status_code, 409)
        assert_error_envelope(self, response.json(), "TRANSITION_CONFLICT")
        self.assertEqual(self._action_ledgers(), before)

    def test_stale_and_duplicate_actions_preserve_the_complete_ledger(self):
        auth = self._auth(self.cfo)
        before = self._action_ledgers()
        stale = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 1}, content_type="application/json", **auth,
        )
        self.assertEqual(stale.status_code, 409)
        self.assertEqual(stale.json()["error"]["code"], "STALE_VERSION")
        self.assertEqual(self._action_ledgers(), before)

        first = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2}, content_type="application/json", **auth,
        )
        self.assertEqual(first.status_code, 200)
        after_first = self._action_ledgers()
        duplicate = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 3}, content_type="application/json", **auth,
        )
        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(duplicate.json()["error"]["code"], "TRANSITION_CONFLICT")
        self.assertEqual(self._action_ledgers(), after_first)

    def test_stale_post_is_independently_zero_write(self):
        auth = self._auth(self.cfo)
        before = self._action_ledgers()
        response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 1}, content_type="application/json", **auth,
        )
        self.assertEqual(response.status_code, 409)
        assert_error_envelope(self, response.json(), "STALE_VERSION")
        self.assertEqual(self._action_ledgers(), before)

    def test_unassigned_reader_post_is_object_denied_without_writes(self):
        actor = self._user(
            "unassigned_reader", "Unassigned Reader", self.read_permission,
            self.approve_permission,
        )
        auth = self._auth(actor)
        before = self._action_ledgers()
        detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **auth
        )
        response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2}, content_type="application/json", **auth,
        )
        self.assertEqual(detail.status_code, 403)
        self.assertEqual(response.status_code, 403)
        assert_error_envelope(self, detail.json(), "OBJECT_ACCESS_DENIED")
        assert_error_envelope(self, response.json(), "OBJECT_ACCESS_DENIED")
        self.assertEqual(self._action_ledgers(), before)

    def test_contradictory_snapshot_detail_and_post_are_not_found_without_writes(self):
        self.case.matrix_projection_json = {
            **self.case.matrix_projection_json,
            "required_director_count": 2,
        }
        self.case.save(update_fields=["matrix_projection_json"])
        auth = self._auth(self.cfo)
        before = self._action_ledgers()
        detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **auth
        )
        response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2}, content_type="application/json", **auth,
        )
        self.assertEqual(detail.status_code, 404)
        self.assertEqual(response.status_code, 404)
        assert_error_envelope(self, detail.json(), "NOT_FOUND")
        assert_error_envelope(self, response.json(), "NOT_FOUND")
        self.assertEqual(self._action_ledgers(), before)

    def test_communication_adapter_failure_rolls_back_final_action_and_outcome(self):
        cfo_response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2}, content_type="application/json", **self._auth(self.cfo),
        )
        self.assertEqual(cfo_response.status_code, 200)
        auth = self._auth(self.director)
        before = self._action_ledgers()

        with patch(
            "sfpcl_credit.communications.services.Notification.objects.create",
            side_effect=RuntimeError("forced notification persistence failure"),
        ), self.assertRaisesRegex(RuntimeError, "forced notification persistence failure"):
            self.client.post(
                f"/api/v1/approval-cases/{self.case.pk}/approve/",
                {"version": 3}, content_type="application/json", **auth,
            )

        self.assertEqual(self._action_ledgers(), before)

    def test_acted_actor_post_matches_disabled_detail_reason_without_writes(self):
        ApprovalAction.objects.create(
            approval_case=self.case,
            approver_user=self.cfo,
            approver_role_code="cfo",
            decision="approved",
        )
        self._assert_disabled_action_post_parity(
            actor=self.cfo, action_code="approve", action_path="approve",
            expected_status=409, expected_code="TRANSITION_CONFLICT",
        )

    def test_excluded_actor_post_matches_disabled_detail_reason_without_writes(self):
        self.case.excluded_approvers_json = [{
            "user_id": str(self.director.pk),
            "conflict_code": "material_interest",
            "reason": "Director declared a material interest.",
        }]
        self.case.save(update_fields=["excluded_approvers_json"])
        before_case = ApprovalCase.objects.filter(pk=self.case.pk).values().get()
        response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2}, content_type="application/json", **self._auth(self.director),
        )
        self.assertEqual(response.status_code, 409)
        assert_error_envelope(self, response.json(), "CONFLICTED_APPROVER_NOT_ALLOWED")
        self.assertEqual(ApprovalCase.objects.filter(pk=self.case.pk).values().get(), before_case)
        self.assertFalse(ApprovalAction.objects.filter(approval_case=self.case).exists())

    def test_closed_case_post_matches_disabled_detail_reason_without_writes(self):
        self.case.current_status = ApprovalCase.STATUS_APPROVED
        self.case.save(update_fields=["current_status"])
        self._assert_disabled_action_post_parity(
            actor=self.cfo, action_code="approve", action_path="approve",
            expected_status=409, expected_code="TRANSITION_CONFLICT",
        )

    def test_missing_approve_permission_matches_disabled_detail_reason_without_writes(self):
        RolePermission.objects.filter(
            role=self.cfo.primary_role, permission=self.approve_permission
        ).delete()
        self._assert_disabled_action_post_parity(
            actor=self.cfo, action_code="approve", action_path="approve",
            expected_status=403, expected_code="FORBIDDEN",
        )

    def test_missing_reject_permission_matches_disabled_detail_reason_without_writes(self):
        RolePermission.objects.filter(
            role=self.cfo.primary_role, permission=self.reject_permission
        ).delete()
        self._assert_disabled_action_post_parity(
            actor=self.cfo, action_code="reject", action_path="reject",
            expected_status=403, expected_code="FORBIDDEN",
        )

    def test_missing_return_permission_matches_disabled_detail_reason_without_writes(self):
        RolePermission.objects.filter(
            role=self.cfo.primary_role, permission=self.return_permission
        ).delete()
        self._assert_disabled_action_post_parity(
            actor=self.cfo, action_code="return", action_path="return-for-clarification",
            expected_status=403, expected_code="FORBIDDEN",
        )

    def test_return_blank_comment_is_validation_error_without_writes(self):
        auth = self._auth(self.cfo)
        before = self._action_ledgers()
        response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/return-for-clarification/",
            {"version": 2, "comments": "  "}, content_type="application/json", **auth,
        )
        self.assertEqual(response.status_code, 400)
        assert_error_envelope(self, response.json(), "VALIDATION_ERROR")
        self.assertEqual(self._action_ledgers(), before)

    def test_return_missing_comment_is_validation_error_without_writes(self):
        auth = self._auth(self.cfo)
        before = self._action_ledgers()
        response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/return-for-clarification/",
            {"version": 2}, content_type="application/json", **auth,
        )
        self.assertEqual(response.status_code, 400)
        assert_error_envelope(self, response.json(), "VALIDATION_ERROR")
        self.assertEqual(self._action_ledgers(), before)

    def test_permission_and_snapshot_scope_denials_preserve_all_business_ledgers(self):
        outsider = self._user("custom_approver", "Unassigned Approver", self.approve_permission)
        cfo_auth = self._auth(self.cfo)
        outsider_auth = self._auth(outsider)
        RolePermission.objects.filter(
            role=self.cfo.primary_role, permission=self.approve_permission
        ).delete()
        before = self._action_ledgers()

        forbidden = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2}, content_type="application/json", **cfo_auth,
        )
        self.assertEqual(forbidden.status_code, 403)
        self.assertEqual(forbidden.json()["error"]["code"], "FORBIDDEN")
        denied = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": 2}, content_type="application/json", **outsider_auth,
        )
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(denied.json()["error"]["code"], "OBJECT_ACCESS_DENIED")
        self.assertEqual(self._action_ledgers(), before)

    def test_assigned_to_me_excludes_an_approver_with_an_immutable_action(self):
        ApprovalAction.objects.create(
            approval_case=self.case,
            approver_user=self.cfo,
            approver_role_code="cfo",
            decision="approved",
            comments="Approved after review.",
        )

        response = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true",
            **self._auth(self.cfo),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], [])
        self.assertEqual(response.json()["pagination"]["total_count"], 0)

    def test_assigned_to_me_excludes_a_case_that_is_no_longer_pending(self):
        self.case.current_status = "approved"
        self.case.save(update_fields=["current_status"])

        response = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true",
            **self._auth(self.cfo),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], [])

    def test_assigned_approver_detail_projects_snapshot_actions_and_review_facts(self):
        auth = self._auth(self.cfo)
        audits_before = AuditLog.objects.count()

        response = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/",
            **auth,
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        assert_success_envelope(self, response.json())
        self.assertEqual(data["approval_case_id"], str(self.case.pk))
        self.assertEqual(data["amount"], "500000.00")
        self.assertEqual(data["approval_matrix_rule_id"], str(self.rule.pk))
        self.assertEqual(data["approval_matrix_rule_version"], "lower-v1")
        self.assertEqual(data["sanction_committee_id"], str(self.committee.pk))
        self.assertEqual(data["sanction_committee_version"], "committee-v1")
        self.assertEqual(data["decision_date"], self.case.decision_date.isoformat())
        self.assertEqual(data["version"], 2)
        self.assertEqual(
            data["required_approvers"][0],
            {
                "role_code": "cfo",
                "user_id": str(self.cfo.pk),
                "full_name": self.cfo.full_name,
                "decision": None,
                "acted_at": None,
            },
        )
        assert_available_actions_shape(self, data["available_actions"])
        self.assertEqual(
            {action["action_code"]: action["enabled"] for action in data["available_actions"]},
            {"approve": True, "reject": True, "return": True, "abstain": True},
        )
        self.assertEqual(data["review_facts"]["eligibility"]["overall_result"], "eligible")
        self.assertEqual(
            data["review_facts"]["loan_amounts"],
            {
                "requested_amount": "500000.00",
                "eligible_amount": "500000.00",
                "recommended_amount": "500000.00",
            },
        )
        self.assertEqual(data["review_facts"]["purpose"]["category"], "crop_production")
        self.assertEqual(data["review_facts"]["risk"]["overall_risk_rating"], "low")
        self.assertEqual(
            data["review_facts"]["documentation_completeness"]["status"], "complete"
        )
        self.assertEqual(AuditLog.objects.count(), audits_before)

    def test_collection_projects_complete_frozen_s21_workbench_facts(self):
        self.case.submitted_at = timezone.now() - timedelta(days=2, hours=3, minutes=4)
        self.case.save(update_fields=["submitted_at"])
        self.member.display_name = "Changed live borrower name"
        self.member.member_type = "fpc"
        self.member.save(update_fields=["display_name", "member_type"])
        self.application.required_loan_amount = "123.00"
        self.application.save(update_fields=["required_loan_amount"])
        self.risk.overall_risk_rating = "critical"
        self.risk.save(update_fields=["overall_risk_rating"])

        response = self.client.get(
            "/api/v1/approval-cases/?current_status=pending"
            "&approval_type=sanction&assigned_to_me=true",
            **self._auth(self.cfo),
        )

        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(response.json()["pagination"]["total_count"], 1)
        row = response.json()["data"][0]["workbench_summary"]
        elapsed_seconds = row["pending_age"].pop("elapsed_seconds")
        self.assertGreaterEqual(elapsed_seconds, 183840)
        self.assertLess(elapsed_seconds, 183845)
        self.assertEqual(
            row,
            {
                "borrower_name": "Approval Queue Member",
                "member_type": "individual_farmer",
                "requested_amount": "500000.00",
                "recommended_amount": "500000.00",
                "eligible_amount": "500000.00",
                "approval_path": "CFO + one Director",
                "exception_flag": False,
                "related_party_flag": False,
                "risk_rating": "low",
                "submitted_at": self.case.submitted_at.isoformat().replace("+00:00", "Z"),
                "current_decision_status": "pending",
                "pending_age": {
                    "label": "Elapsed pending time",
                    "display": "2d 3h",
                },
            },
        )

    def test_list_filters_are_strict_and_preserve_the_exact_threshold_route(self):
        response = self.client.get(
            "/api/v1/approval-cases/?current_status=pending&approval_type=sanction"
            "&assigned_to_me=false&page=1&page_size=1",
            **self._auth(self.cfo),
        )

        self.assertEqual(response.status_code, 200)
        assert_pagination_shape(self, response.json())
        self.assertEqual(response.json()["data"][0]["amount"], "500000.00")
        self.assertEqual(response.json()["pagination"]["page_size"], 1)

        invalid = self.client.get(
            "/api/v1/approval-cases/?live_committee=true",
            **self._auth(self.cfo),
        )
        self.assertEqual(invalid.status_code, 400)
        assert_error_envelope(self, invalid.json(), "VALIDATION_ERROR")
        self.assertEqual(
            invalid.json()["error"]["field_errors"],
            {"live_committee": "Unknown query parameter."},
        )

    def test_excluded_or_incompletely_routed_snapshots_never_enter_the_queue(self):
        self.case.excluded_approvers_json = [
            {
                "user_id": str(self.cfo.pk),
                "conflict_code": "material_interest",
                "reason": "Conflict fixture",
            }
        ]
        self.case.save(update_fields=["excluded_approvers_json"])
        excluded = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true",
            **self._auth(self.cfo),
        )
        self.assertEqual(excluded.status_code, 200)
        self.assertEqual(excluded.json()["data"], [])

        self.case.excluded_approvers_json = []
        self.case.approval_matrix_rule_version = ""
        self.case.save(
            update_fields=["excluded_approvers_json", "approval_matrix_rule_version"]
        )
        unrouted_list = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true",
            **self._auth(self.cfo),
        )
        unrouted_detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/",
            **self._auth(self.cfo),
        )
        self.assertEqual(unrouted_list.json()["data"], [])
        self.assertEqual(unrouted_detail.status_code, 404)
        assert_error_envelope(self, unrouted_detail.json(), "NOT_FOUND")

    def test_missing_loan_limit_provenance_cannot_be_inferred_from_amount(self):
        self.case.loan_limit_provenance_json = {}
        self.case.save(update_fields=["loan_limit_provenance_json"])

        response = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true",
            **self._auth(self.cfo),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], [])

    def test_arbitrary_user_injected_into_required_snapshot_is_not_routable(self):
        injected = self._user(
            "injected_reader", "Injected Reader", self.read_permission
        )
        self.case.required_approvers_json[1] = {
            "role_code": "director",
            "user_id": str(injected.pk),
            "full_name": injected.full_name,
        }
        self.case.save(update_fields=["required_approvers_json"])

        self._assert_snapshot_is_hidden_without_writes(injected)

    def test_duplicate_required_approver_is_not_routable(self):
        self.case.required_approvers_json[1]["user_id"] = str(self.cfo.pk)
        self.case.save(update_fields=["required_approvers_json"])

        self._assert_snapshot_is_hidden_without_writes(self.cfo)

    def test_required_approver_with_wrong_role_is_not_routable(self):
        self.case.required_approvers_json[1]["role_code"] = "cfo"
        self.case.save(update_fields=["required_approvers_json"])

        self._assert_snapshot_is_hidden_without_writes(self.cfo)

    def test_required_approver_count_disagrees_with_matrix_projection(self):
        self.case.matrix_projection_json["required_director_count"] = 2
        self.case.save(update_fields=["matrix_projection_json"])

        self._assert_snapshot_is_hidden_without_writes(self.cfo)

    def test_case_amount_disagrees_with_matrix_projection(self):
        self.case.matrix_projection_json["amount"] = "499999.99"
        self.case.save(update_fields=["matrix_projection_json"])

        self._assert_snapshot_is_hidden_without_writes(self.cfo)

    def test_case_condition_disagrees_with_matrix_projection(self):
        self.case.matrix_projection_json[
            "condition_code"
        ] = "exceeds_permissible_limit"
        self.case.save(update_fields=["matrix_projection_json"])

        self._assert_snapshot_is_hidden_without_writes(self.cfo)

    def test_incomplete_joint_approval_projection_is_not_routable(self):
        del self.case.matrix_projection_json["joint_approval_required"]
        self.case.save(update_fields=["matrix_projection_json"])

        self._assert_snapshot_is_hidden_without_writes(self.cfo)

    def test_incomplete_register_projection_is_not_routable(self):
        self.case.matrix_projection_json["register_required"] = None
        self.case.save(update_fields=["matrix_projection_json"])

        self._assert_snapshot_is_hidden_without_writes(self.cfo)

    def test_read_permission_without_snapshot_scope_cannot_list_or_retrieve_the_case(self):
        reader = self._user("approval_reader", "Approval Reader", self.read_permission)
        unassigned_director = self._user(
            "unassigned_director", "Unassigned Director", self.read_permission
        )
        RolePermission.objects.create(
            role=self.preparer.primary_role, permission=self.read_permission
        )
        actor_headers = {
            actor.pk: self._auth(actor)
            for actor in (reader, unassigned_director, self.preparer)
        }
        ledger_before = {
            "case": ApprovalCase.objects.filter(pk=self.case.pk).values().get(),
            "actions": list(ApprovalAction.objects.filter(approval_case=self.case).values()),
            "audits": list(AuditLog.objects.order_by("pk").values()),
            "workflows": list(WorkflowEvent.objects.order_by("pk").values()),
        }

        for actor in (reader, unassigned_director, self.preparer):
            ordinary_list = self.client.get(
                "/api/v1/approval-cases/", **actor_headers[actor.pk]
            )
            self.assertEqual(ordinary_list.status_code, 200)
            self.assertEqual(ordinary_list.json()["data"], [])
            self.assertEqual(ordinary_list.json()["pagination"]["total_count"], 0)

            detail = self.client.get(
                f"/api/v1/approval-cases/{self.case.pk}/", **actor_headers[actor.pk]
            )
            self.assertEqual(detail.status_code, 403)
            assert_error_envelope(self, detail.json(), "OBJECT_ACCESS_DENIED")

        self.assertEqual(
            {
                "case": ApprovalCase.objects.filter(pk=self.case.pk).values().get(),
                "actions": list(ApprovalAction.objects.filter(approval_case=self.case).values()),
                "audits": list(AuditLog.objects.order_by("pk").values()),
                "workflows": list(WorkflowEvent.objects.order_by("pk").values()),
            },
            ledger_before,
        )

    def test_assigned_approver_can_retrieve_own_acted_history(self):
        ApprovalAction.objects.create(
            approval_case=self.case,
            approver_user=self.cfo,
            approver_role_code="cfo",
            decision="approved",
            comments="Approved after review.",
        )

        ordinary_list = self.client.get(
            "/api/v1/approval-cases/", **self._auth(self.cfo)
        )
        detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **self._auth(self.cfo)
        )

        self.assertEqual(ordinary_list.status_code, 200)
        self.assertEqual(ordinary_list.json()["pagination"]["total_count"], 1)
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(
            detail.json()["data"]["required_approvers"][0]["decision"], "approved"
        )

    def test_missing_case_read_permission_is_denied_before_object_scope(self):
        unrelated = self._user("unrelated", "Unrelated User")

        denied = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/",
            **self._auth(unrelated),
        )
        self.assertEqual(denied.status_code, 403)
        assert_error_envelope(self, denied.json(), "FORBIDDEN")

        maker_denied = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/",
            **self._auth(self.preparer),
        )
        self.assertEqual(maker_denied.status_code, 403)
        assert_error_envelope(self, maker_denied.json(), "FORBIDDEN")

    def test_assignment_does_not_replace_each_action_specific_permission(self):
        RolePermission.objects.filter(
            role=self.cfo.primary_role,
            permission=self.reject_permission,
        ).delete()

        response = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/",
            **self._auth(self.cfo),
        )

        actions = {
            item["action_code"]: item for item in response.json()["data"]["available_actions"]
        }
        self.assertTrue(actions["approve"]["enabled"])
        self.assertFalse(actions["reject"]["enabled"])
        self.assertEqual(
            actions["reject"]["disabled_reason"],
            "Required permission is not granted.",
        )
        self.assertTrue(actions["return"]["enabled"])

    def test_detail_projects_acted_decisions_without_changing_the_required_snapshot(self):
        frozen_required = list(self.case.required_approvers_json)
        action = ApprovalAction.objects.create(
            approval_case=self.case,
            approver_user=self.cfo,
            approver_role_code="cfo",
            decision="approved",
            comments="Approved after review.",
        )

        response = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/",
            **self._auth(self.director),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["required_approvers"][0]["decision"], "approved")
        self.assertEqual(
            data["required_approvers"][0]["acted_at"],
            action.acted_at.isoformat().replace("+00:00", "Z"),
        )
        self.assertTrue(all(item["enabled"] for item in data["available_actions"]))
        self.case.refresh_from_db()
        self.assertEqual(self.case.required_approvers_json, frozen_required)

    def test_detail_is_unchanged_when_live_configuration_rows_change(self):
        first = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/",
            **self._auth(self.cfo),
        ).json()["data"]

        ApprovalMatrixRule.objects.filter(pk=self.rule.pk).update(
            version_number="live-rule-v99",
            required_director_count=2,
        )
        SanctionCommittee.objects.filter(pk=self.committee.pk).update(
            version_number="live-committee-v99",
            committee_name="Changed Live Committee",
        )
        second = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/",
            **self._auth(self.cfo),
        ).json()["data"]

        self.assertEqual(second, first)
        self.assertEqual(second["approval_matrix_rule_version"], "lower-v1")
        self.assertEqual(second["sanction_committee_version"], "committee-v1")

    def test_routed_historical_case_wins_over_same_amount_unrouted_shell_after_live_change(self):
        shell = self._create_unrouted_shell()
        first_queue = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true",
            **self._auth(self.cfo),
        ).json()["data"]
        self.assertEqual(
            [item["approval_case_id"] for item in first_queue],
            [str(self.case.pk)],
        )
        self.assertEqual(f"{shell.loan_application.required_loan_amount:.2f}", "500000.00")
        self.assertEqual(shell.current_status, self.case.current_status)

        current_cfo = self._user(
            "current_cfo",
            "Current CFO",
            self.read_permission,
            self.approve_permission,
            self.reject_permission,
            self.return_permission,
        )
        current_director_1 = self._user(
            "current_director_1", "Current Director 1", self.read_permission
        )
        current_director_2 = self._user(
            "current_director_2", "Current Director 2", self.read_permission
        )
        current_date = self.case.decision_date + timedelta(days=1)
        current_rule = ApprovalMatrixRule.objects.create(
            decision_type="loan_sanction",
            amount_min="0.00",
            amount_max="500000.00",
            required_approver_roles_json=["cfo", "director"],
            required_director_count=1,
            joint_approval_required_flag=True,
            register_required="credit_sanction_register",
            effective_from=current_date,
            status="active",
            version_number="current-rule-v2",
        )
        current_committee = SanctionCommittee.objects.create(
            committee_name="Current Committee",
            cfo_user=current_cfo,
            director_1_user=current_director_1,
            director_2_user=current_director_2,
            board_meeting_reference="BM-CURRENT-2026",
            effective_from=current_date,
            status="active",
            version_number="current-committee-v2",
        )
        shell.approval_matrix_rule = current_rule
        shell.approval_matrix_rule_version = current_rule.version_number
        shell.sanction_committee = current_committee
        shell.sanction_committee_version = current_committee.version_number
        shell.required_approvers_json = [
            {"role_code": "cfo", "user_id": str(current_cfo.pk), "full_name": current_cfo.full_name},
            {
                "role_code": "director",
                "user_id": str(current_director_1.pk),
                "full_name": current_director_1.full_name,
            },
        ]
        shell.excluded_approvers_json = []
        shell.amount = "500000.00"
        shell.related_entity_type = "loan_application"
        shell.related_entity_id = shell.loan_application_id
        shell.reason_for_approval = "Current independently routed case."
        shell.matrix_projection_json = {
            "approval_matrix_rule_id": str(current_rule.pk),
            "version_number": current_rule.version_number,
            "decision_type": "loan_sanction",
            "amount": "500000.00",
            "amount_min": "0.00",
            "amount_max": "500000.00",
            "condition_code": None,
            "decision_date": current_date.isoformat(),
            "required_approver_roles": ["cfo", "director"],
            "required_director_count": 1,
            "joint_approval_required": True,
            "register_required": "credit_sanction_register",
        }
        shell.committee_projection_json = {
            "sanction_committee_id": str(current_committee.pk),
            "version_number": current_committee.version_number,
            "decision_date": current_date.isoformat(),
            "cfo_user_id": str(current_cfo.pk),
            "director_user_ids": [str(current_director_1.pk), str(current_director_2.pk)],
        }
        current_provenance = {
            "loan_limit_assessment_id": str(shell.loan_appraisal_note.loan_limit_assessment_id_snapshot),
            "loan_application_id": str(shell.loan_application_id),
            "final_eligible_loan_amount": "500000.00",
            "exception_required_flag": False,
            "calculation_rule_version": "current-limit-v2",
            "policy_config_id": "60000000-0000-0000-0000-000000000006",
            "policy_name": "Current Board Loan Policy",
            "calculated_at": timezone.now().isoformat(),
        }
        shell.loan_limit_provenance_json = current_provenance
        shell.decision_date = current_date
        shell.version = 2
        shell.save()
        shell.loan_appraisal_note.reviewed_at += timedelta(days=1)
        shell.loan_appraisal_note.loan_limit_snapshot_json = {
            **shell.loan_appraisal_note.loan_limit_snapshot_json,
            **current_provenance,
        }
        shell.loan_appraisal_note.save(
            update_fields=[
                "reviewed_at",
                "loan_limit_snapshot_json",
            ]
        )
        shell = ApprovalCase.objects.select_related(
            "loan_application", "loan_appraisal_note__risk_assessment"
        ).get(pk=shell.pk)
        shell.appraisal_facts_json = _project_review_facts(shell)
        shell.save(update_fields=["appraisal_facts_json"])
        unprojected_current_queue = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true",
            **self._auth(current_cfo),
        ).json()["data"]
        refresh_approval_case_projection(shell)

        historical_queue = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true",
            **self._auth(self.cfo),
        ).json()["data"]
        current_queue = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true",
            **self._auth(current_cfo),
        ).json()["data"]

        self.assertEqual(historical_queue, first_queue)
        self.assertEqual(unprojected_current_queue, [])
        self.assertEqual(
            [item["approval_case_id"] for item in current_queue],
            [str(shell.pk)],
        )

    def test_review_facts_remain_frozen_after_live_owning_records_change(self):
        frozen_facts = dict(self.case.appraisal_facts_json)
        self.application.declared_purpose = "Updated owning application purpose"
        self.application.completeness_status = LoanApplication.COMPLETENESS_INCOMPLETE
        self.application.save(update_fields=["declared_purpose", "completeness_status"])
        self.risk.overall_risk_rating = "medium"
        self.risk.save(update_fields=["overall_risk_rating"])

        response = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/",
            **self._auth(self.cfo),
        )

        facts = response.json()["data"]["review_facts"]
        self.assertEqual(facts, frozen_facts)
        self.assertEqual(facts["purpose"]["description"], "Crop production")
        self.assertEqual(facts["documentation_completeness"]["status"], "complete")
        self.assertEqual(facts["risk"]["overall_risk_rating"], "low")
        self.assertEqual(
            facts["source_references"]["appraisal"],
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
        )

    @staticmethod
    def _permission(code):
        return Permission.objects.create(
            permission_code=code,
            permission_name=code,
            module_name="approvals",
            risk_level="high",
        )

    def _general_meeting_recorder_and_payload(self):
        record_permission = self._permission("approvals.general_meeting.record")
        document_permission = self._permission("documents.file.download")
        upload_permission = self._permission("documents.file.upload")
        recorder = self._user(
            "general_meeting_recorder",
            "General Meeting Recorder",
            self.read_permission,
            record_permission,
            document_permission,
            upload_permission,
        )
        recorder.primary_role.role_code = "company_secretary"
        recorder.primary_role.save(update_fields=["role_code"])
        ApprovalCaseReadScopeGrant.objects.create(
            role=recorder.primary_role,
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_LEGAL_READONLY,
        )
        document_ids = [
            self._upload_general_meeting_document(recorder, file_name)
            for file_name in ("notice.pdf", "minutes.pdf", "resolution.pdf")
        ]
        self.case.general_meeting_evidence_required = True
        self.case.save(update_fields=["general_meeting_evidence_required"])
        return recorder, {
            "related_party_type": "director_relative",
            "related_party_user_id": str(self.director.pk),
            "relationship_description": "Borrower is a relative of a Director.",
            "meeting_date": timezone.localdate().isoformat(),
            "notice_document_id": document_ids[0],
            "minutes_document_id": document_ids[1],
            "resolution_document_id": document_ids[2],
            "approval_status": "approved",
        }

    def _upload_general_meeting_document(
        self,
        recorder,
        file_name,
        *,
        related_entity_id=None,
        related_entity_type="application",
        document_category="legal",
        sensitivity_level="restricted",
    ):
        response = self.client.post(
            "/api/v1/document-files/",
            {
                "file": SimpleUploadedFile(
                    file_name,
                    f"evidence:{file_name}".encode(),
                    content_type="application/pdf",
                ),
                "document_category": document_category,
                "sensitivity_level": sensitivity_level,
                "related_entity_type": related_entity_type,
                "related_entity_id": (
                    str(self.application.pk)
                    if related_entity_id is None
                    else related_entity_id
                ),
            },
            **self._auth(recorder),
        )
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()["data"]["document_id"]

    def _general_meeting_ledgers(self):
        return {
            "meetings": list(
                apps.get_model("approvals", "GeneralMeetingApproval").objects.values()
            ),
            "cases": list(ApprovalCase.objects.values()),
            "exceptions": list(ExceptionRegisterEntry.objects.values()),
            "meeting_audits": list(
                AuditLog.objects.filter(
                    action__startswith="general_meeting_approval."
                ).values()
            ),
            "meeting_workflows": list(
                WorkflowEvent.objects.filter(
                    workflow_name="general_meeting_approval"
                ).values()
            ),
            "download_audits": list(
                AuditLog.objects.filter(action="documents.file.downloaded").values()
            ),
        }

    def _action_ledgers(self):
        return {
            "case": ApprovalCase.objects.filter(pk=self.case.pk).values().get(),
            "actions": list(ApprovalAction.objects.order_by("pk").values()),
            "sanctions": list(apps.get_model("approvals", "SanctionDecision").objects.order_by("pk").values()),
            "audits": list(AuditLog.objects.order_by("pk").values()),
            "workflows": list(WorkflowEvent.objects.order_by("pk").values()),
            "communications": list(Communication.objects.order_by("pk").values()),
            "notifications": list(Notification.objects.order_by("pk").values()),
        }

    def _assert_read_only_scope_never_assigns_or_mutates(self, actor):
        headers = self._auth(actor)
        ordinary = self.client.get("/api/v1/approval-cases/", **headers)
        assigned = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true", **headers
        )
        detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **headers
        )

        self.assertEqual(ordinary.json()["pagination"]["total_count"], 1)
        self.assertEqual(assigned.json()["pagination"]["total_count"], 0)
        self.assertTrue(
            all(
                not action["enabled"]
                for action in detail.json()["data"]["available_actions"]
            )
        )
        before = self._action_ledgers()
        for action_path in ("approve", "reject", "return-for-clarification"):
            with self.subTest(actor=actor.email, action_path=action_path):
                denied = self.client.post(
                    f"/api/v1/approval-cases/{self.case.pk}/{action_path}/",
                    {"version": 2, "comments": "Read-only review cannot decide."},
                    content_type="application/json",
                    **headers,
                )
                self.assertEqual(denied.status_code, 403)
                assert_error_envelope(self, denied.json(), "FORBIDDEN")
                self.assertEqual(self._action_ledgers(), before)

    def _assert_public_two_director_conflict_block(self, excluded_director):
        self.application.required_loan_amount = "600000.00"
        self.application.save(update_fields=["required_loan_amount"])
        self.note.recommended_amount = "600000.00"
        self.note.loan_limit_snapshot_json = {
            **self.note.loan_limit_snapshot_json,
            "final_eligible_loan_amount": "600000.00",
        }
        self.note.save(
            update_fields=["recommended_amount", "loan_limit_snapshot_json"]
        )
        upper_rule = ApprovalMatrixRule.objects.create(
            decision_type="loan_sanction",
            amount_min="500000.01",
            amount_max=None,
            required_approver_roles_json=["cfo", "director"],
            required_director_count=2,
            joint_approval_required_flag=True,
            register_required="credit_sanction_register",
            effective_from=self.case.decision_date,
            status="active",
            version_number="upper-conflict-v1",
        )
        ApprovalMatrixRule.objects.exclude(pk=upper_rule.pk).update(status="inactive")
        SanctionCommittee.objects.exclude(pk=self.committee.pk).update(status="inactive")
        review = self.review
        self._reset_case_to_unrouted(review)
        ApprovalConflictDeclaration.objects.create(
            loan_application=self.application,
            user=excluded_director,
            conflict_type="director_relative",
            reason="Borrower is relative of the routed Director.",
            declared_by_user=self.preparer,
        )

        snapshot = SanctionHandoffModule().enrich_pending(
            actor=self.preparer,
            application_id=self.application.pk,
            payload={
                "approval_type": "sanction",
                "amount": "600000.00",
                "reason_for_approval": "Upper route conflict acceptance.",
                "force_exception_route": False,
            },
            actor_permissions={"approvals.case.create"},
        ).snapshot

        self.case.refresh_from_db()
        effective = ConflictOfInterestModule.effective_approvers(self.case)
        self.assertEqual(snapshot["current_status"], "blocked_by_conflict")
        self.assertEqual(
            snapshot["conflict_block_reason"],
            "Required Director approval authority is unavailable after conflict exclusion.",
        )
        self.assertEqual(len(effective), 2)
        self.assertEqual(len({item["user_id"] for item in effective}), 2)
        self.assertEqual(
            {item["role_code"] for item in effective}, {"cfo", "director"}
        )
        self.assertFalse(
            ApprovalAction.objects.filter(approval_case=self.case).exists()
        )
        self.assertFalse(
            apps.get_model("approvals", "SanctionDecision").objects.filter(
                approval_case=self.case
            ).exists()
        )
        self.assertEqual(
            AuditLog.objects.filter(
                action="approval_case.enriched", entity_id=self.case.pk
            ).count(),
            1,
        )

    def _assert_public_conflict_class(
        self,
        *,
        actor,
        expected_code,
        expected_general_meeting,
        conflict_type=None,
        source_fact=None,
    ):
        if source_fact == "application_created_by_user":
            self.application.created_by_user = actor
            self.application.save(update_fields=["created_by_user"])
        elif source_fact == "appraisal_prepared_by_user":
            self.note.prepared_by_user = actor
            self.note.save(update_fields=["prepared_by_user"])
        review = self.review
        self._reset_case_to_unrouted(review)
        ApprovalMatrixRule.objects.exclude(pk=self.rule.pk).update(status="inactive")
        SanctionCommittee.objects.exclude(pk=self.committee.pk).update(status="inactive")
        if conflict_type:
            ApprovalConflictDeclaration.objects.create(
                loan_application=self.application,
                user=actor,
                conflict_type=conflict_type,
                reason=f"Public {conflict_type} conflict evidence.",
                declared_by_user=self.preparer,
            )

        snapshot = SanctionHandoffModule().enrich_pending(
            actor=self.preparer,
            application_id=self.application.pk,
            payload={
                "approval_type": "sanction",
                "amount": "500000.00",
                "reason_for_approval": "Public conflict matrix acceptance.",
                "force_exception_route": False,
            },
            actor_permissions={"approvals.case.create"},
        ).snapshot
        self.case.refresh_from_db()
        exclusion = next(
            item
            for item in self.case.excluded_approvers_json
            if item["user_id"] == str(actor.pk)
        )
        headers = self._auth(actor)
        queue = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true", **headers
        )
        detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **headers
        )
        denied = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/approve/",
            {"version": self.case.version, "comments": "Conflicted public attempt."},
            content_type="application/json",
            HTTP_X_REQUEST_ID=f"req-{expected_code}",
            **headers,
        )

        self.assertEqual(exclusion["conflict_code"], expected_code)
        self.assertEqual(
            snapshot["general_meeting_evidence_required"],
            expected_general_meeting,
        )
        self.assertEqual(queue.status_code, 200, queue.json())
        self.assertEqual(queue.json()["pagination"]["total_count"], 0)
        self.assertEqual(detail.status_code, 200, detail.json())
        self.assertEqual(denied.status_code, 409, denied.json())
        self.assertEqual(
            denied.json()["error"]["code"], "CONFLICTED_APPROVER_NOT_ALLOWED"
        )
        self.assertEqual(
            denied.json()["error"]["details"]["conflict_reason"],
            exclusion["reason"],
        )
        self.assertEqual(
            AuditLog.objects.filter(
                action="approval_case.conflicted_action_denied",
                entity_id=self.case.pk,
                actor_user=actor,
            ).count(),
            1,
        )
        self.assertFalse(
            ApprovalAction.objects.filter(approval_case=self.case).exists()
        )

    def _reset_case_to_unrouted(self, review):
        self.case.approval_matrix_rule = None
        self.case.approval_matrix_rule_version = ""
        self.case.sanction_committee = None
        self.case.sanction_committee_version = ""
        self.case.required_approvers_json = {}
        self.case.excluded_approvers_json = []
        self.case.general_meeting_evidence_required = False
        self.case.conflict_block_reason = ""
        self.case.amount = None
        self.case.related_entity_type = ""
        self.case.related_entity_id = None
        self.case.reason_for_approval = ""
        self.case.reason_for_rejection = ""
        self.case.matrix_projection_json = {}
        self.case.committee_projection_json = {}
        self.case.loan_limit_provenance_json = {}
        self.case.appraisal_facts_json = {}
        self.case.decision_date = None
        self.case.appraisal_review_decision = review
        self.case.current_status = ApprovalCase.STATUS_PENDING
        self.case.closed_at = None
        self.case.version = 1
        self.case.save()
        refresh_approval_case_projection(self.case)

    def _assert_disabled_action_post_parity(
        self, *, actor, action_code, action_path, expected_status, expected_code
    ):
        headers = self._auth(actor)
        detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **headers
        )
        self.assertEqual(detail.status_code, 200, detail.json())
        action = next(
            item for item in detail.json()["data"]["available_actions"]
            if item["action_code"] == action_code
        )
        self.assertFalse(action["enabled"])
        before = self._action_ledgers()
        response = self.client.post(
            f"/api/v1/approval-cases/{self.case.pk}/{action_path}/",
            {"version": self.case.version, "comments": "Public denial parity."},
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, expected_status, response.json())
        assert_error_envelope(self, response.json(), expected_code)
        self.assertEqual(response.json()["error"]["message"], action["disabled_reason"])
        self.assertEqual(self._action_ledgers(), before)

    @staticmethod
    def _user(role_code, full_name, *permissions):
        role = Role.objects.create(
            role_code=f"{role_code}-{Role.objects.count()}",
            role_name=full_name,
            is_system_role=True,
            status="active",
        )
        for permission in permissions:
            RolePermission.objects.create(role=role, permission=permission)
        user = User.objects.create(
            full_name=full_name,
            email=f"{role.role_code}@sfpcl.example",
            status="active",
            primary_role=role,
        )
        user.set_password("ApprovalQueue123!")
        user.save()
        return user

    def _auth(self, user):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "ApprovalQueue123!"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return {"HTTP_AUTHORIZATION": f"Bearer {response.json()['data']['access_token']}"}


    def _postgres_different_remaining_approvers_same_version_have_one_serial_winner(self):
        before = self._race_ledger()
        results = self._race((self.cfo.pk, self.director.pk), version=2)

        self.assertEqual(sorted(code for code, _ in results), ["STALE_VERSION", "won"])
        after = self._race_ledger()
        self.assertEqual(after["case"]["version"], 3)
        self.assertEqual(after["case"]["current_status"], ApprovalCase.STATUS_PENDING)
        self.assertEqual(len(after["actions"]), len(before["actions"]) + 1)
        self.assertEqual(len(after["sanctions"]), len(before["sanctions"]))
        self.assertEqual(len(after["communications"]), len(before["communications"]))
        self.assertEqual(len(after["notifications"]), len(before["notifications"]))
        self._assert_single_attributable_action_delta(before, after)

    def _postgres_final_remaining_approver_duplicate_submission_has_one_serial_winner(self):
        approval_actions.approve_case(
            actor=self.cfo,
            case_id=self.case.pk,
            payload={"version": 2, "comments": "Seed the final approval race."},
            actor_permissions=effective_permission_codes(self.cfo),
            request_meta={"request_id": "race-seed"},
        )
        before = self._race_ledger()
        results = self._race((self.director.pk, self.director.pk), version=3)

        self.assertEqual(sorted(code for code, _ in results), ["STALE_VERSION", "won"])
        after = self._race_ledger()
        self.assertEqual(after["case"]["version"], 4)
        self.assertEqual(after["case"]["current_status"], ApprovalCase.STATUS_APPROVED)
        self.assertEqual(len(after["actions"]), len(before["actions"]) + 1)
        self.assertEqual(len(after["sanctions"]), len(before["sanctions"]) + 1)
        self.assertEqual(len(after["communications"]), len(before["communications"]) + 1)
        self.assertEqual(len(after["notifications"]), len(before["notifications"]) + 1)
        self._assert_single_attributable_action_delta(before, after)
        communication = Communication.objects.get(related_entity_id=self.case.pk)
        notification = Notification.objects.get(communication=communication)
        self.assertEqual(communication.delivery_status, "pending")
        self.assertEqual(notification.recipient_team_code, "credit_assessment")
        self.assertEqual(
            AuditLog.objects.filter(
                action="communications.communication.created",
                entity_id=communication.pk,
            ).count(),
            1,
        )

    def _race(self, actor_ids, *, version):
        gate = Barrier(2)

        def act(actor_id):
            close_old_connections()
            try:
                actor = User.objects.get(pk=actor_id)
                gate.wait(timeout=10)
                result = approval_actions.approve_case(
                    actor=actor,
                    case_id=self.case.pk,
                    payload={"version": version, "comments": "Concurrent approval."},
                    actor_permissions=effective_permission_codes(actor),
                    request_meta={"request_id": f"race-{actor_id}"},
                )
                return "won", result
            except approval_actions.ApprovalActionConflict as exc:
                return exc.code, {"message": exc.message, "status": exc.status}
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(act, actor_id) for actor_id in actor_ids]
            return [future.result(timeout=15) for future in futures]

    def _race_ledger(self):
        return {
            "case": ApprovalCase.objects.filter(pk=self.case.pk).values().get(),
            "actions": list(ApprovalAction.objects.filter(approval_case=self.case).values()),
            "sanctions": list(apps.get_model("approvals", "SanctionDecision").objects.filter(approval_case=self.case).values()),
            "audits": list(AuditLog.objects.filter(entity_id=self.case.pk, action="approval_case.action_recorded").values()),
            "workflows": list(WorkflowEvent.objects.filter(entity_id=self.case.pk, workflow_name="sanction_approval").values()),
            "communications": list(Communication.objects.filter(related_entity_id=self.case.pk).values()),
            "notifications": list(Notification.objects.filter(related_entity_id=self.case.pk).values()),
        }

    def _assert_single_attributable_action_delta(self, before, after):
        before_action_ids = {row["approval_action_id"] for row in before["actions"]}
        new_actions = [row for row in after["actions"] if row["approval_action_id"] not in before_action_ids]
        self.assertEqual(len(new_actions), 1)
        action = new_actions[0]
        self.assertEqual(action["decision"], "approved")
        self.assertEqual(action["comments"], "Concurrent approval.")
        self.assertEqual(
            ApprovalAction.objects.filter(
                approval_case=self.case, approver_user_id=action["approver_user_id"]
            ).count(),
            1,
        )
        self.assertEqual(len(after["audits"]), len(before["audits"]) + 1)
        self.assertEqual(len(after["workflows"]), len(before["workflows"]) + 1)
        audit = next(
            row for row in after["audits"]
            if row["new_value_json"]["approval_action_id"] == str(action["approval_action_id"])
        )
        self.assertEqual(audit["actor_user_id"], action["approver_user_id"])
        self.assertEqual(audit["new_value_json"]["decision"], "approved")
        self.assertEqual(audit["new_value_json"]["comments"], "Concurrent approval.")

    def _assert_snapshot_is_hidden_without_writes(self, actor):
        refresh_approval_case_projection(self.case)
        headers = self._auth(actor)
        before = {
            "case": ApprovalCase.objects.filter(pk=self.case.pk).values().get(),
            "actions": list(ApprovalAction.objects.filter(approval_case=self.case).values()),
            "audits": list(AuditLog.objects.order_by("pk").values()),
            "workflows": list(WorkflowEvent.objects.order_by("pk").values()),
        }

        collection = self.client.get("/api/v1/approval-cases/", **headers)
        detail = self.client.get(
            f"/api/v1/approval-cases/{self.case.pk}/", **headers
        )

        self.assertEqual(collection.status_code, 200)
        self.assertEqual(collection.json()["data"], [])
        self.assertEqual(collection.json()["pagination"]["total_count"], 0)
        self.assertEqual(detail.status_code, 404)
        assert_error_envelope(self, detail.json(), "NOT_FOUND")
        self.assertEqual(
            {
                "case": ApprovalCase.objects.filter(pk=self.case.pk).values().get(),
                "actions": list(ApprovalAction.objects.filter(approval_case=self.case).values()),
                "audits": list(AuditLog.objects.order_by("pk").values()),
                "workflows": list(WorkflowEvent.objects.order_by("pk").values()),
            },
            before,
        )

    def _create_unrouted_shell(self):
        application = LoanApplication.objects.create(
            application_reference_number=f"LO{LoanApplication.objects.count() + 702:08d}",
            member=self.member,
            borrower_type=self.member.member_type,
            received_by_user=self.preparer,
            required_loan_amount="500000.00",
            declared_purpose="Same-amount contradictory shell",
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
            assessed_by_user=self.preparer,
        )
        note = LoanAppraisalNote.objects.create(
            loan_application=application,
            prepared_by_user=self.preparer,
            reviewed_by_user=self.preparer,
            reviewed_at=timezone.now(),
            last_review_decision="reviewed",
            tat_due_at=timezone.now() + timedelta(days=1),
            tat_status=LoanAppraisalNote.TAT_WITHIN,
            eligibility_assessment_id_snapshot="40000000-0000-0000-0000-000000000004",
            loan_limit_assessment_id_snapshot="50000000-0000-0000-0000-000000000005",
            eligibility_snapshot_json={
                "eligibility_assessment_id": "40000000-0000-0000-0000-000000000004",
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
                "assessed_at": timezone.now().isoformat(),
            },
            loan_limit_snapshot_json={"final_eligible_loan_amount": "500000.00"},
            prerequisite_provenance="verified",
            borrower_summary="Unrouted shell borrower summary.",
            eligibility_summary="Eligible.",
            loan_limit_summary="Within limit.",
            recommended_amount="500000.00",
            recommended_security_summary="Standard security.",
            repayment_capacity_notes="Adequate.",
            risk_assessment=risk,
            recommendation="approve",
            appraisal_status=LoanAppraisalNote.STATUS_SUBMITTED_TO_SANCTION,
        )
        review = AppraisalReviewDecision.objects.create(
            loan_appraisal_note=note,
            decision="reviewed",
            review_comments="Immutable review for unrouted shell.",
            reviewer_user=self.preparer,
            decided_at=note.reviewed_at,
            from_state=LoanAppraisalNote.STATUS_REVIEW_PENDING,
            to_state=LoanAppraisalNote.STATUS_REVIEWED,
        )
        return ApprovalCase.objects.create(
            loan_application=application,
            loan_appraisal_note=note,
            appraisal_review_decision=review,
            submitted_by_user=self.preparer,
            submission_remarks="Unrouted version-one shell.",
        )

    def _create_second_routed_case(self, director):
        committee = SanctionCommittee.objects.create(
            committee_name="Second Historical Committee",
            cfo_user=self.cfo,
            director_1_user=director,
            director_2_user=self.director,
            board_meeting_reference="BM-2026-07-B",
            effective_from=self.case.decision_date,
            status="active",
            version_number="committee-v2",
        )
        application = LoanApplication.objects.create(
            application_reference_number="LO00000702",
            member=self.member,
            borrower_type=self.member.member_type,
            received_by_user=self.preparer,
            required_loan_amount="500000.00",
            requested_tenure_months=12,
            declared_purpose="Second scoped sanction case",
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
            risk_mitigation_notes="Second case monitoring.",
            assessed_by_user=self.preparer,
        )
        calculated_at = timezone.now() - timedelta(minutes=30)
        note = LoanAppraisalNote.objects.create(
            loan_application=application,
            prepared_by_user=self.preparer,
            reviewed_by_user=self.preparer,
            reviewed_at=timezone.now(),
            last_review_decision="reviewed",
            tat_due_at=timezone.now() + timedelta(days=1),
            tat_status=LoanAppraisalNote.TAT_WITHIN,
            eligibility_assessment_id_snapshot="60000000-0000-0000-0000-000000000006",
            loan_limit_assessment_id_snapshot="70000000-0000-0000-0000-000000000007",
            eligibility_snapshot_json={
                "eligibility_assessment_id": "60000000-0000-0000-0000-000000000006",
                "loan_application_id": str(application.pk),
                "overall_result": "eligible",
                "member_active_check": "pass",
                "default_check": "pass",
                "document_check": "pass",
                "terms_acceptance_check": "pass",
                "purpose_check": "pass",
                "nominee_check": "pass",
                "assessment_notes": "Eligible.",
                "active_member_snapshot": {},
                "assessed_by_user_id": str(self.preparer.pk),
                "assessed_at": calculated_at.isoformat(),
            },
            loan_limit_snapshot_json={
                "loan_limit_assessment_id": "70000000-0000-0000-0000-000000000007",
                "loan_application_id": str(application.pk),
                "final_eligible_loan_amount": "500000.00",
                "exception_required_flag": False,
                "calculation_rule_version": "limit-v7",
                "policy_config_id": "30000000-0000-0000-0000-000000000003",
                "policy_name": "Board Loan Policy",
                "calculated_at": calculated_at.isoformat(),
            },
            prerequisite_provenance="verified",
            borrower_summary="Independent scoped case.",
            eligibility_summary="All eligibility checks passed.",
            loan_limit_summary="Recommended amount is within the verified limit.",
            recommended_amount="500000.00",
            recommended_tenure_months=12,
            recommended_interest_type="floating",
            recommended_security_summary="Standard member security package.",
            repayment_capacity_notes="Projected proceeds cover instalments.",
            risk_assessment=risk,
            recommendation="approve",
            appraisal_status=LoanAppraisalNote.STATUS_SUBMITTED_TO_SANCTION,
        )
        review = AppraisalReviewDecision.objects.create(
            loan_appraisal_note=note,
            decision="reviewed",
            review_comments="Immutable review for second scoped case.",
            reviewer_user=self.preparer,
            decided_at=note.reviewed_at,
            from_state=LoanAppraisalNote.STATUS_REVIEW_PENDING,
            to_state=LoanAppraisalNote.STATUS_REVIEWED,
        )
        case = ApprovalCase.objects.create(
            loan_application=application,
            loan_appraisal_note=note,
            appraisal_review_decision=review,
            submitted_by_user=self.preparer,
            submission_remarks="Second scoped case ready for review.",
            approval_matrix_rule=self.rule,
            approval_matrix_rule_version=self.rule.version_number,
            sanction_committee=committee,
            sanction_committee_version=committee.version_number,
            required_approvers_json=[
                {
                    "role_code": "cfo",
                    "user_id": str(self.cfo.pk),
                    "full_name": self.cfo.full_name,
                },
                {
                    "role_code": "director",
                    "user_id": str(director.pk),
                    "full_name": director.full_name,
                },
            ],
            excluded_approvers_json=[],
            amount="500000.00",
            related_entity_type="loan_application",
            related_entity_id=application.pk,
            reason_for_approval="Second case sanction reason.",
            matrix_projection_json={
                **self.case.matrix_projection_json,
                "amount": "500000.00",
            },
            committee_projection_json={
                "sanction_committee_id": str(committee.pk),
                "version_number": committee.version_number,
                "decision_date": self.case.decision_date.isoformat(),
                "cfo_user_id": str(self.cfo.pk),
                "director_user_ids": [str(director.pk), str(self.director.pk)],
            },
            loan_limit_provenance_json={
                **note.loan_limit_snapshot_json,
                "loan_limit_assessment_id": str(note.loan_limit_assessment_id_snapshot),
            },
            decision_date=self.case.decision_date,
            version=2,
        )
        case = ApprovalCase.objects.select_related(
            "loan_application", "loan_appraisal_note__risk_assessment"
        ).get(pk=case.pk)
        case.appraisal_facts_json = _project_review_facts(case)
        case.save(update_fields=["appraisal_facts_json"])
        refresh_approval_case_projection(case)
        return case


@skipUnless(connection.vendor == "postgresql", "Authoritative approval action race requires PostgreSQL.")
class ApprovalActionConcurrencyTests(TransactionTestCase):
    reset_sequences = True
    setUp = ApprovalCaseRoutingApiTests.setUp
    _permission = staticmethod(ApprovalCaseRoutingApiTests._permission)
    _user = staticmethod(ApprovalCaseRoutingApiTests._user)
    _race = ApprovalCaseRoutingApiTests._race
    _race_ledger = ApprovalCaseRoutingApiTests._race_ledger
    _assert_single_attributable_action_delta = (
        ApprovalCaseRoutingApiTests._assert_single_attributable_action_delta
    )
    test_different_remaining_approvers_same_version_have_one_serial_winner = (
        ApprovalCaseRoutingApiTests._postgres_different_remaining_approvers_same_version_have_one_serial_winner
    )
    test_final_remaining_approver_duplicate_submission_has_one_serial_winner = (
        ApprovalCaseRoutingApiTests._postgres_final_remaining_approver_duplicate_submission_has_one_serial_winner
    )
