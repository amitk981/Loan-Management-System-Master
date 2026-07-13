from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from unittest import skipUnless
from unittest.mock import patch

from django.apps import apps
from django.db import IntegrityError, close_old_connections, connection, connections, transaction
from django.test import Client, TestCase, TransactionTestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import (
    ApprovalAction,
    ApprovalCase,
    ApprovalCaseRequiredApprover,
    ApprovalCaseReadScopeGrant,
    ApprovalConflictDeclaration,
    ApprovalMatrixRule,
    SanctionCommittee,
)
from sfpcl_credit.approvals.modules.approval_case_selector import (
    select_approval_case_candidates,
)
from sfpcl_credit.approvals.modules import approval_actions, approval_case_engine
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
                "overall_result": "eligible",
                "member_active_check": "pass",
                "default_check": "pass",
                "document_check": "pass",
                "terms_acceptance_check": "pass",
                "purpose_check": "pass",
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
                "exception_required_flag": False,
                "calculation_rule_version": "limit-v7",
                "policy_config_id": "30000000-0000-0000-0000-000000000003",
                "policy_name": "Board Loan Policy",
                "calculated_at": calculated_at.isoformat(),
            },
            decision_date=decision_date,
            version=2,
        )
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
            **approval_case_engine.serialize_case_review_facts(self.case),
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
        review = AppraisalReviewDecision.objects.create(
            loan_appraisal_note=self.note,
            decision="reviewed",
            review_comments="Reviewed for conflict enrichment.",
            reviewer_user=self.preparer,
            decided_at=self.note.reviewed_at,
            from_state=LoanAppraisalNote.STATUS_REVIEW_PENDING,
            to_state=LoanAppraisalNote.STATUS_REVIEWED,
        )
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
        self.case.save(update_fields=["excluded_approvers_json"])
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
            data["conflict_block_reason"],
            "Required CFO approval authority is unavailable after conflict exclusion.",
        )
        self.case.refresh_from_db()
        self.assertEqual(self.case.current_status, "blocked_by_conflict")
        self.assertIsNotNone(self.case.closed_at)
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

    def test_persisted_scope_list_query_count_is_bounded_as_repository_grows(self):
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
        case_queries = [
            query["sql"]
            for query in expanded_queries.captured_queries
            if 'FROM "approval_cases"' in query["sql"]
        ]
        self.assertEqual(len(case_queries), 2)
        paginated_query = next(query for query in case_queries if " LIMIT " in query)
        count_query = next(query for query in case_queries if " LIMIT " not in query)
        self.assertIn("COUNT(", count_query)
        self.assertIn(
            '"approval_cases"."approval_type" = \'sanction\'', paginated_query
        )
        self.assertNotIn('JOIN "approval_actions"', paginated_query)

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

    def test_return_restores_reviewed_precommittee_state_without_sanction(self):
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

    def test_return_correction_fresh_review_creates_immutable_second_cycle(self):
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
        self.assertTrue(
            all(
                not action["enabled"]
                for action in returned_history.json()["data"]["available_actions"]
            )
        )
        self.assertEqual(
            [item["cycle_number"] for item in current_queue.json()["data"]], [2]
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
            update_fields=["reviewed_at", "loan_limit_snapshot_json"]
        )

        historical_queue = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true",
            **self._auth(self.cfo),
        ).json()["data"]
        current_queue = self.client.get(
            "/api/v1/approval-cases/?assigned_to_me=true",
            **self._auth(current_cfo),
        ).json()["data"]

        self.assertEqual(historical_queue, first_queue)
        self.assertEqual(
            [item["approval_case_id"] for item in current_queue],
            [str(shell.pk)],
        )

    def test_review_facts_are_read_through_projections_from_the_owning_records(self):
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
        self.assertEqual(facts["purpose"]["description"], "Updated owning application purpose")
        self.assertEqual(facts["documentation_completeness"]["status"], "incomplete")
        self.assertEqual(facts["risk"]["overall_risk_rating"], "medium")
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
        review = AppraisalReviewDecision.objects.create(
            loan_appraisal_note=self.note,
            decision="reviewed",
            review_comments="Reviewed for two-Director conflict acceptance.",
            reviewer_user=self.preparer,
            decided_at=self.note.reviewed_at,
            from_state=LoanAppraisalNote.STATUS_REVIEW_PENDING,
            to_state=LoanAppraisalNote.STATUS_REVIEWED,
        )
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
        review = AppraisalReviewDecision.objects.create(
            loan_appraisal_note=self.note,
            decision="reviewed",
            review_comments="Reviewed for the public conflict matrix.",
            reviewer_user=self.preparer,
            decided_at=self.note.reviewed_at,
            from_state=LoanAppraisalNote.STATUS_REVIEW_PENDING,
            to_state=LoanAppraisalNote.STATUS_REVIEWED,
        )
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
            eligibility_snapshot_json={"overall_result": "eligible"},
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
        return ApprovalCase.objects.create(
            loan_application=application,
            loan_appraisal_note=note,
            submitted_by_user=self.preparer,
            submission_remarks="Unrouted version-one shell.",
        )


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
