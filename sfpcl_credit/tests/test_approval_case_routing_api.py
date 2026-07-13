from datetime import timedelta

from django.apps import apps
from django.db import IntegrityError, connection, transaction
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import (
    ApprovalAction,
    ApprovalCase,
    ApprovalMatrixRule,
    SanctionCommittee,
)
from sfpcl_credit.approvals.modules.approval_case_selector import (
    select_approval_case_candidates,
)
from sfpcl_credit.credit.models import LoanAppraisalNote, RiskAssessment
from sfpcl_credit.communications.models import Notification
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
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
        self.assertEqual(self.note.appraisal_status, "reviewed")
        self.assertFalse(apps.get_model("approvals", "SanctionDecision").objects.exists())

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
            {"approve": True, "reject": True, "return": True},
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
            {"user_id": str(self.cfo.pk), "reason": "Conflict fixture"}
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

    def _assert_snapshot_is_hidden_without_writes(self, actor):
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
