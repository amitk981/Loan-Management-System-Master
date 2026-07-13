import ast
from datetime import date
import inspect
import textwrap

from django.core.exceptions import PermissionDenied
from django.test import Client, TestCase
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.credit.models import EligibilityAssessment
from sfpcl_credit.identity.models import (
    Permission,
    Role,
    RolePermission,
    Team,
    User,
    UserTeamMembership,
)
from sfpcl_credit.members.models import (
    Member,
    MemberIdentityChangeRequest,
    MemberScopeAssignment,
    MemberServiceEvidence,
    ProduceSupplyRecord,
)
from sfpcl_credit.members.modules.active_member_status import (
    ActiveMemberObjectAccessDenied,
    ActiveMemberStatusModule,
)
from sfpcl_credit.members.modules.member_registry import MemberRegistry
from sfpcl_credit.members.protected_identity import identity_hash


ACTION_PERMISSIONS = {
    "list": "members.member.read",
    "detail": "members.member.read",
    "update": "members.member.update",
    "identity_approval": "members.member.identity_change.approve",
    "supply_capture": "members.active_status.calculate",
    "supply_verification": "members.active_status.verify",
    "service_evidence_create": "members.active_status.verify",
    "service_evidence_update": "members.active_status.verify",
    "active_status_calculation": "members.active_status.calculate",
    "active_status_verification": "members.active_status.verify",
}
ELIGIBILITY_RUN_PERMISSION = "credit.eligibility.run"
PUBLIC_ACTION_ROW_NAMES = {
    "test_list_authority_row",
    "test_detail_authority_row",
    "test_update_authority_row",
    "test_identity_approval_authority_row",
    "test_supply_capture_authority_row",
    "test_supply_verification_authority_row",
    "test_service_evidence_create_authority_row",
    "test_service_evidence_update_authority_row",
    "test_active_status_calculation_authority_row",
    "test_active_status_verification_authority_row",
}


class MemberAuthorityActionMatrixTests(TestCase):
    """Executable permission-versus-persisted-scope rows for every public member action."""

    def setUp(self):
        self.client = Client()
        role = Role.objects.create(
            role_code="member_action_matrix",
            role_name="Member Action Matrix",
            is_system_role=False,
            status="active",
        )
        for code in sorted({*ACTION_PERMISSIONS.values(), ELIGIBILITY_RUN_PERMISSION}):
            permission = Permission.objects.create(
                permission_code=code,
                permission_name=code,
                module_name="members",
                risk_level="high",
            )
            RolePermission.objects.create(role=role, permission=permission)
        self.actor = User.objects.create(
            full_name="Matrix Actor",
            email="member-matrix@example.test",
            status="active",
            primary_role=role,
        )
        self.actor.set_password("MatrixPass123!")
        self.actor.save(update_fields=["password_hash"])
        self.member = Member.objects.create(
            member_type="individual_farmer",
            legal_name="Matrix Member",
            display_name="Matrix Member",
            folio_number="MATRIX-1",
            membership_status="active",
            kyc_status="verified",
            default_status="no_default",
        )
        self.other_member = Member.objects.create(
            member_type="fpc",
            legal_name="Other Matrix Member",
            display_name="Other Matrix Member",
            folio_number="MATRIX-2",
            membership_status="active",
            kyc_status="verified",
            default_status="no_default",
        )

    def _headers(self):
        login = self.client.post(
            "/api/v1/auth/login/",
            data={"email": self.actor.email, "password": "MatrixPass123!"},
            content_type="application/json",
        )
        self.assertEqual(login.status_code, 200)
        return {"HTTP_AUTHORIZATION": f"Bearer {login.json()['data']['access_token']}"}

    def _assign(self, permission, member=None, scope_type="assigned", team=None):
        return MemberScopeAssignment.objects.create(
            user=self.actor,
            permission_code=permission,
            scope_type=scope_type,
            member=member,
            team=team,
        )

    def _assert_object_denied(self, response):
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "OBJECT_ACCESS_DENIED")

    def _assert_different_update_denied(self, headers):
        response = self.client.patch(
            f"/api/v1/members/{self.member.member_id}/",
            data={"email": "must-not-change@example.test", "version": self.member.version},
            content_type="application/json",
            **headers,
        )
        self._assert_object_denied(response)

    def _assert_ledger_change(self, before, *, changed=(), deltas=None):
        after = self._ledger()
        deltas = deltas or {}
        changed = set(changed) | set(deltas)
        for name in before:
            if name in deltas:
                self.assertEqual(len(after[name]), len(before[name]) + deltas[name], name)
            elif name not in changed:
                self.assertEqual(after[name], before[name], name)
        return after

    def _assert_denied_phase(self, action, before):
        self.assertIn(action, ACTION_PERMISSIONS)
        self.assertEqual(self._ledger(), before)

    def _assert_success_phase(self, action, outcome):
        self.assertIn(action, ACTION_PERMISSIONS)
        self.assertIsNotNone(outcome)
        if action == "list":
            self.assertEqual(outcome.status_code, 200)
            self.assertEqual(outcome.json()["data"][0]["member_id"], str(self.member.member_id))
        elif action == "detail":
            self.assertEqual(outcome.json()["data"]["member_id"], str(self.member.member_id))
        elif action == "update":
            self.assertEqual(outcome.json()["data"]["email"], "matrix-updated@example.test")
        elif action == "identity_approval":
            self.assertEqual(outcome.json()["data"]["kyc_status"], "pending")
            self.assertEqual(outcome.json()["data"]["member_id"], str(self.member.member_id))
        elif action == "supply_capture":
            self.assertEqual(outcome.json()["data"]["evidence_reference"], "MATRIX-SUPPLY-1")
        elif action == "supply_verification":
            self.assertTrue(outcome.json()["data"]["verified_flag"])
        elif action == "service_evidence_create":
            self.assertEqual(outcome.evidence_reference, "MATRIX-SERVICE-CREATE")
            self.assertEqual(outcome.member_id, self.member.member_id)
        elif action == "service_evidence_update":
            self.assertEqual(outcome.evidence_reference, "MATRIX-SERVICE-UPDATED")
        elif action == "active_status_calculation":
            snapshot = outcome.json()["data"]["active_member_snapshot"]
            self.assertEqual(snapshot["member_type"], self.member.member_type)
        elif action == "active_status_verification":
            self.assertEqual(outcome.json()["data"]["decision"], "inactive")
            self.assertEqual(outcome.json()["data"]["member_id"], str(self.member.member_id))
        else:  # pragma: no cover - the completeness guard constrains the action set.
            self.fail(f"Missing success assertion for public member action {action}")

    @staticmethod
    def _ledger():
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.members.models import (
            ActiveMemberStatus,
            MemberChangeHistory,
            MemberServiceEvidence,
            ProduceSupplyRecord,
        )
        from sfpcl_credit.workflows.models import WorkflowEvent

        def rows(model, pk):
            return list(model.objects.order_by(pk).values())

        return {
            "members": rows(Member, "member_id"),
            "scope_assignments": rows(MemberScopeAssignment, "member_scope_assignment_id"),
            "identity_requests": rows(MemberIdentityChangeRequest, "identity_change_request_id"),
            "supply": rows(ProduceSupplyRecord, "produce_supply_record_id"),
            "service_evidence": rows(MemberServiceEvidence, "member_service_evidence_id"),
            "service_makers": list(MemberServiceEvidence.maker_users.through.objects.order_by("pk").values()),
            "active_status": rows(ActiveMemberStatus, "active_member_status_id"),
            "eligibility": rows(EligibilityAssessment, "eligibility_assessment_id"),
            "history": rows(MemberChangeHistory, "member_change_history_id"),
            "audit": rows(AuditLog, "audit_log_id"),
            "workflow": rows(WorkflowEvent, "workflow_event_id"),
        }

    def test_list_authority_row(self):
        headers = self._headers()
        before = self._ledger()
        denied = self.client.get("/api/v1/members/", **headers)
        self.assertEqual(denied.status_code, 200)
        self.assertEqual(denied.json()["data"], [])
        self.assertEqual(denied.json()["pagination"]["total_count"], 0)
        self._assert_denied_phase("list", before)

        self._assign(ACTION_PERMISSIONS["list"], self.member)
        allowed = self.client.get("/api/v1/members/", **headers)
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(allowed.json()["pagination"]["total_count"], 1)
        self.assertEqual(allowed.json()["data"][0]["member_id"], str(self.member.member_id))
        self._assert_ledger_change(before, deltas={"scope_assignments": 1})
        self._assert_success_phase("list", allowed)
        self._assert_different_update_denied(headers)

    def test_detail_authority_row(self):
        headers = self._headers()
        before = self._ledger()
        denied = self.client.get(f"/api/v1/members/{self.member.member_id}/", **headers)
        self._assert_object_denied(denied)
        self._assert_denied_phase("detail", before)

        self._assign(ACTION_PERMISSIONS["detail"], self.member)
        allowed = self.client.get(f"/api/v1/members/{self.member.member_id}/", **headers)
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(allowed.json()["data"]["member_id"], str(self.member.member_id))
        self._assert_ledger_change(before, deltas={"scope_assignments": 1})
        self._assert_success_phase("detail", allowed)
        unrelated = self.client.get(f"/api/v1/members/{self.other_member.member_id}/", **headers)
        self._assert_object_denied(unrelated)
        self._assert_different_update_denied(headers)

    def test_update_authority_row(self):
        headers = self._headers()
        before = self._ledger()
        payload = {"email": "matrix-updated@example.test", "version": self.member.version}
        denied = self.client.patch(
            f"/api/v1/members/{self.member.member_id}/",
            data=payload,
            content_type="application/json",
            **headers,
        )
        self._assert_object_denied(denied)
        self._assert_denied_phase("update", before)

        self._assign(ACTION_PERMISSIONS["update"], self.member)
        allowed = self.client.patch(
            f"/api/v1/members/{self.member.member_id}/",
            data=payload,
            content_type="application/json",
            **headers,
        )
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(allowed.json()["data"]["email"], "matrix-updated@example.test")
        self.member.refresh_from_db()
        self.assertEqual(self.member.email, "matrix-updated@example.test")
        self._assert_ledger_change(
            before,
            changed={"members"},
            deltas={"scope_assignments": 1, "history": 1, "audit": 1},
        )
        self._assert_success_phase("update", allowed)
        different = self.client.get(f"/api/v1/members/{self.member.member_id}/", **headers)
        self._assert_object_denied(different)

    def test_identity_approval_authority_row(self):
        requester = User.objects.create(
            full_name="Identity Requester",
            email="identity-requester@example.test",
            status="active",
            primary_role=self.actor.primary_role,
        )
        change = MemberIdentityChangeRequest.objects.create(
            member=self.member,
            requester_user=requester,
            proposed_pan_encrypted="enc:new",
            proposed_pan_hash=identity_hash("PQRST6789U"),
            reason="Correct synthetic identity",
            member_version=self.member.version,
        )
        headers = self._headers()
        before = self._ledger()
        url = f"/api/v1/member-identity-change-requests/{change.identity_change_request_id}/approve/"
        denied = self.client.post(url, data={}, content_type="application/json", **headers)
        self._assert_object_denied(denied)
        self._assert_denied_phase("identity_approval", before)

        self._assign(ACTION_PERMISSIONS["identity_approval"], self.member)
        allowed = self.client.post(url, data={}, content_type="application/json", **headers)
        self.assertEqual(allowed.status_code, 200)
        change.refresh_from_db()
        self.member.refresh_from_db()
        self.assertEqual(change.status, "approved")
        self.assertEqual(change.approver_user, self.actor)
        self.assertEqual(self.member.kyc_status, "pending")
        self._assert_ledger_change(
            before,
            changed={"members", "identity_requests"},
            deltas={"scope_assignments": 1, "history": 1, "audit": 1},
        )
        self._assert_success_phase("identity_approval", allowed)
        self._assert_different_update_denied(headers)

    def test_supply_capture_authority_row(self):
        headers = self._headers()
        before = self._ledger()
        response = self.client.post(
            f"/api/v1/members/{self.member.member_id}/produce-supply-records/",
            data={
                "financial_year": "2025-26",
                "supplied_to_entity_type": "sfpcl",
                "supply_route": "direct",
                "evidence_reference": "MATRIX-SUPPLY-1",
                "version": self.member.version,
            },
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "OBJECT_ACCESS_DENIED")
        self._assert_denied_phase("supply_capture", before)

        MemberScopeAssignment.objects.create(
            user=self.actor,
            permission_code=ACTION_PERMISSIONS["supply_capture"],
            scope_type="assigned",
            member=self.member,
        )
        allowed = self.client.post(
            f"/api/v1/members/{self.member.member_id}/produce-supply-records/",
            data={
                "financial_year": "2025-26",
                "supplied_to_entity_type": "sfpcl",
                "supply_route": "direct",
                "evidence_reference": "MATRIX-SUPPLY-1",
                "version": self.member.version,
            },
            content_type="application/json",
            **headers,
        )
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(allowed.json()["data"]["member_id"], str(self.member.member_id))
        self.assertEqual(allowed.json()["data"]["evidence_reference"], "MATRIX-SUPPLY-1")
        self._assert_ledger_change(
            before,
            changed={"members"},
            deltas={"scope_assignments": 1, "supply": 1, "history": 1, "audit": 1},
        )
        self._assert_success_phase("supply_capture", allowed)
        differently_scoped = self.client.get(
            f"/api/v1/members/{self.member.member_id}/", **headers
        )
        self.assertEqual(differently_scoped.status_code, 403)
        self.assertEqual(
            differently_scoped.json()["error"]["code"], "OBJECT_ACCESS_DENIED"
        )
    def test_supply_verification_authority_row(self):
        maker = User.objects.create(
            full_name="Supply Maker", email="supply-maker@example.test",
            status="active", primary_role=self.actor.primary_role,
        )
        record = ProduceSupplyRecord.objects.create(
            member=self.member, financial_year="2025-26",
            supplied_to_entity_type="sfpcl", supply_route="direct",
            evidence_reference="MATRIX-VERIFY-1", captured_by_user=maker,
        )
        headers = self._headers()
        before = self._ledger()
        url = f"/api/v1/produce-supply-records/{record.produce_supply_record_id}/verify/"
        denied = self.client.post(
            url, data={"version": record.version}, content_type="application/json", **headers
        )
        self._assert_object_denied(denied)
        self._assert_denied_phase("supply_verification", before)

        self._assign(ACTION_PERMISSIONS["supply_verification"], self.member)
        allowed = self.client.post(
            url, data={"version": record.version}, content_type="application/json", **headers
        )
        self.assertEqual(allowed.status_code, 200)
        record.refresh_from_db()
        self.assertTrue(record.verified_flag)
        self.assertEqual(record.verified_by_user, self.actor)
        self._assert_ledger_change(
            before,
            changed={"members", "supply"},
            deltas={"scope_assignments": 1, "history": 1, "audit": 1},
        )
        self._assert_success_phase("supply_verification", allowed)
        self._assert_different_update_denied(headers)

    def test_service_evidence_create_authority_row(self):
        module = ActiveMemberStatusModule()
        before = self._ledger()
        kwargs = {
            "actor": self.actor,
            "member_id": self.member.member_id,
            "version": self.member.version,
            "service_type": "service",
            "recipient_entity_type": "sfpcl",
            "service_from": date(2022, 1, 1),
            "service_to": date(2026, 12, 31),
            "evidence_reference": "MATRIX-SERVICE-CREATE",
        }
        with self.assertRaises(ActiveMemberObjectAccessDenied):
            module.create_service_evidence(**kwargs)
        self._assert_denied_phase("service_evidence_create", before)

        self._assign(ACTION_PERMISSIONS["service_evidence_create"], self.member)
        evidence = module.create_service_evidence(**kwargs)
        self.assertEqual(evidence.member_id, self.member.member_id)
        self.assertEqual(evidence.evidence_reference, "MATRIX-SERVICE-CREATE")
        self.assertEqual(list(evidence.maker_users.all()), [self.actor])
        self._assert_ledger_change(
            before,
            changed={"members"},
            deltas={
                "scope_assignments": 1,
                "service_evidence": 1,
                "service_makers": 1,
                "history": 1,
                "audit": 1,
            },
        )
        self._assert_success_phase("service_evidence_create", evidence)
        with self.assertRaises(PermissionDenied):
            MemberRegistry.get(self.member.member_id, self.actor)

    def test_service_evidence_update_authority_row(self):
        maker = User.objects.create(
            full_name="Evidence Maker", email="evidence-maker@example.test",
            status="active", primary_role=self.actor.primary_role,
        )
        evidence = MemberServiceEvidence.objects.create(
            member=self.member, service_type="service", recipient_entity_type="sfpcl",
            service_from=date(2022, 1, 1), service_to=date(2026, 12, 31),
            evidence_reference="MATRIX-SERVICE-OLD", verified_by_user=maker,
            verified_at=timezone.now(),
        )
        evidence.maker_users.add(maker)
        module = ActiveMemberStatusModule()
        before = self._ledger()
        kwargs = {
            "actor": self.actor,
            "evidence_id": evidence.member_service_evidence_id,
            "version": self.member.version,
            "evidence_reference": "MATRIX-SERVICE-UPDATED",
        }
        with self.assertRaises(ActiveMemberObjectAccessDenied):
            module.update_service_evidence(**kwargs)
        self._assert_denied_phase("service_evidence_update", before)

        self._assign(ACTION_PERMISSIONS["service_evidence_update"], self.member)
        updated = module.update_service_evidence(**kwargs)
        self.assertEqual(updated.evidence_reference, "MATRIX-SERVICE-UPDATED")
        self.assertEqual(set(updated.maker_users.all()), {maker, self.actor})
        self._assert_ledger_change(
            before,
            changed={"members", "service_evidence"},
            deltas={"scope_assignments": 1, "service_makers": 1, "history": 1, "audit": 1},
        )
        self._assert_success_phase("service_evidence_update", updated)
        with self.assertRaises(PermissionDenied):
            MemberRegistry.get(self.member.member_id, self.actor)

    def test_active_status_calculation_authority_row(self):
        owner = User.objects.create(
            full_name="Application Owner", email="application-owner@example.test",
            status="active", primary_role=self.actor.primary_role,
        )
        application = LoanApplication.objects.create(
            application_reference_number="LO-MATRIX-1",
            member=self.member,
            borrower_type=self.member.member_type,
            received_by_user=owner,
            created_by_user=owner,
            application_status=LoanApplication.STATUS_REFERENCE_GENERATED,
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
            purpose_category="crop_production",
            terms_acceptance_flag=True,
        )
        headers = self._headers()
        before = self._ledger()
        url = f"/api/v1/loan-applications/{application.loan_application_id}/eligibility-assessment/run/?member_id={self.other_member.member_id}"
        denied = self.client.post(
            url,
            data={"member_id": str(self.other_member.member_id)},
            content_type="application/json",
            **headers,
        )
        self._assert_object_denied(denied)
        self._assert_denied_phase("active_status_calculation", before)

        application.created_by_user = self.actor
        application.received_by_user = self.actor
        application.save(update_fields=["created_by_user", "received_by_user"])
        owned_before = self._ledger()
        query_substituted = self.client.post(
            url,
            data={},
            content_type="application/json",
            **headers,
        )
        self._assert_object_denied(query_substituted)
        self.assertEqual(self._ledger(), owned_before)
        body_substituted = self.client.post(
            f"/api/v1/loan-applications/{application.loan_application_id}/eligibility-assessment/run/",
            data={"member_id": str(self.other_member.member_id)},
            content_type="application/json",
            **headers,
        )
        self._assert_object_denied(body_substituted)
        self.assertEqual(self._ledger(), owned_before)

        allowed = self.client.post(
            f"/api/v1/loan-applications/{application.loan_application_id}/eligibility-assessment/run/",
            data={}, content_type="application/json", **headers,
        )
        self.assertEqual(allowed.status_code, 200)
        snapshot = allowed.json()["data"]["active_member_snapshot"]
        self.assertEqual(snapshot["member_type"], self.member.member_type)
        self.assertNotEqual(snapshot["member_type"], self.other_member.member_type)
        self.assertNotIn(str(self.other_member.member_id), str(allowed.json()))
        self.assertEqual(EligibilityAssessment.objects.get().loan_application, application)
        self._assert_ledger_change(
            owned_before,
            deltas={"eligibility": 1, "audit": 1, "workflow": 1},
        )
        self._assert_success_phase("active_status_calculation", allowed)
        self._assert_different_update_denied(headers)

    def test_active_status_verification_authority_row(self):
        result = ActiveMemberStatusModule().calculate(member_id=self.member.member_id)
        headers = self._headers()
        before = self._ledger()
        url = f"/api/v1/members/{self.member.member_id}/active-status/verify/"
        payload = {
            "result_id": result.result_id,
            "as_of_date": result.calculated_as_of_date,
            "decision": "inactive",
            "reason": "Synthetic matrix verification",
            "version": self.member.version,
        }
        denied = self.client.post(url, data=payload, content_type="application/json", **headers)
        self._assert_object_denied(denied)
        self._assert_denied_phase("active_status_verification", before)

        self._assign(ACTION_PERMISSIONS["active_status_verification"], self.member)
        allowed = self.client.post(url, data=payload, content_type="application/json", **headers)
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(allowed.json()["data"]["member_id"], str(self.member.member_id))
        self.assertEqual(allowed.json()["data"]["decision"], "inactive")
        self.member.refresh_from_db()
        self.assertEqual(self.member.active_member_status, "inactive")
        self._assert_ledger_change(
            before,
            changed={"members"},
            deltas={"scope_assignments": 1, "active_status": 1, "history": 1, "audit": 1},
        )
        self._assert_success_phase("active_status_verification", allowed)
        self._assert_different_update_denied(headers)

    def test_real_list_and_detail_boundaries_cover_every_persisted_scope_kind(self):
        headers = self._headers()
        read_permission = ACTION_PERMISSIONS["list"]

        self._assign(read_permission, scope_type="global")
        global_rows = self.client.get("/api/v1/members/", **headers)
        self.assertEqual(global_rows.json()["pagination"]["total_count"], 2)
        self.assertEqual(
            self.client.get(f"/api/v1/members/{self.other_member.member_id}/", **headers).status_code,
            200,
        )
        MemberScopeAssignment.objects.all().delete()

        self.member.created_by_user = self.actor
        self.member.save(update_fields=["created_by_user"])
        self._assign(read_permission, scope_type="created_by")
        created_rows = self.client.get("/api/v1/members/", **headers)
        self.assertEqual([row["member_id"] for row in created_rows.json()["data"]], [str(self.member.member_id)])
        self.assertEqual(
            self.client.get(f"/api/v1/members/{self.member.member_id}/", **headers).status_code,
            200,
        )
        MemberScopeAssignment.objects.all().delete()
        self._assign(ACTION_PERMISSIONS["update"], scope_type="created_by")
        created_mutation = self.client.patch(
            f"/api/v1/members/{self.member.member_id}/",
            data={"email": "created-scope@example.test", "version": self.member.version},
            content_type="application/json",
            **headers,
        )
        self.assertEqual(created_mutation.status_code, 200)
        self.assertEqual(created_mutation.json()["data"]["email"], "created-scope@example.test")
        MemberScopeAssignment.objects.all().delete()
        self.member.created_by_user = None
        self.member.save(update_fields=["created_by_user"])

        active_team = Team.objects.create(team_code="matrix-active", team_name="Matrix Active", status="active")
        inactive_team = Team.objects.create(team_code="matrix-inactive", team_name="Matrix Inactive", status="inactive")
        unrelated_team = Team.objects.create(team_code="matrix-other", team_name="Matrix Other", status="active")
        UserTeamMembership.objects.create(user=self.actor, team=active_team, status="active")
        self._assign(read_permission, self.member, scope_type="team", team=active_team)
        active_rows = self.client.get("/api/v1/members/", **headers)
        self.assertEqual([row["member_id"] for row in active_rows.json()["data"]], [str(self.member.member_id)])
        self.assertEqual(
            self.client.get(f"/api/v1/members/{self.member.member_id}/", **headers).status_code,
            200,
        )
        MemberScopeAssignment.objects.all().delete()

        self._assign(read_permission, self.member, scope_type="team", team=inactive_team)
        self.assertEqual(self.client.get("/api/v1/members/", **headers).json()["data"], [])
        self._assert_object_denied(
            self.client.get(f"/api/v1/members/{self.member.member_id}/", **headers)
        )
        MemberScopeAssignment.objects.all().delete()
        self._assign(read_permission, self.member, scope_type="team", team=unrelated_team)
        self.assertEqual(self.client.get("/api/v1/members/", **headers).json()["data"], [])
        self._assert_object_denied(
            self.client.get(f"/api/v1/members/{self.member.member_id}/", **headers)
        )
        MemberScopeAssignment.objects.all().delete()

        self._assign(read_permission, self.member)
        unrelated = self.client.get(f"/api/v1/members/{self.other_member.member_id}/", **headers)
        self._assert_object_denied(unrelated)

    def test_actorless_calculator_exposes_no_unused_actor_authority_interface(self):
        self.assertFalse(hasattr(ActiveMemberStatusModule, "calculate_for_actor"))

    def test_public_action_matrix_has_exact_independently_selectable_rows(self):
        actual = {
            name
            for name in vars(type(self))
            if name.endswith("_authority_row") and name.startswith("test_")
        }
        self.assertEqual(actual, PUBLIC_ACTION_ROW_NAMES)
        for name in PUBLIC_ACTION_ROW_NAMES:
            method = getattr(type(self), name)
            self.assertTrue(callable(method))
            tree = ast.parse(textwrap.dedent(inspect.getsource(method)))
            action = name.removeprefix("test_").removesuffix("_authority_row")
            public_calls = []
            assertion_calls = []
            phase_calls = {"_assert_denied_phase": [], "_assert_success_phase": []}
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                    continue
                if node.func.attr.startswith("assert") or node.func.attr.startswith("_assert"):
                    assertion_calls.append(node.func.attr)
                if node.func.attr in phase_calls:
                    phase_calls[node.func.attr].append(node)
                owner = node.func.value
                if (
                    isinstance(owner, ast.Attribute)
                    and isinstance(owner.value, ast.Name)
                    and owner.value.id == "self"
                    and owner.attr == "client"
                    and node.func.attr in {"get", "post", "patch"}
                ) or node.func.attr in {"create_service_evidence", "update_service_evidence"}:
                    public_calls.append(node)
            identifiers = {
                node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
            }
            self.assertNotIn("evaluate_member_authority", identifiers, name)
            self.assertGreaterEqual(len(public_calls), 2, name)
            self.assertGreaterEqual(len(assertion_calls), 3, name)
            denied_calls = phase_calls["_assert_denied_phase"]
            success_calls = phase_calls["_assert_success_phase"]
            self.assertEqual(len(denied_calls), 1, name)
            self.assertEqual(len(success_calls), 1, name)
            denied_call, success_call = denied_calls[0], success_calls[0]
            for phase_call in (denied_call, success_call):
                self.assertIsInstance(phase_call.args[0], ast.Constant, name)
                self.assertEqual(phase_call.args[0].value, action, name)
            self.assertLess(denied_call.lineno, success_call.lineno, name)
            self.assertTrue(
                any(call.lineno < denied_call.lineno for call in public_calls), name
            )
            self.assertTrue(
                any(
                    denied_call.lineno < call.lineno < success_call.lineno
                    for call in public_calls
                ),
                name,
            )
