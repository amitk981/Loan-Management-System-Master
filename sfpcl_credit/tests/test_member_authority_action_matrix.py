from django.test import TestCase

from sfpcl_credit.identity.models import Permission, Role, RolePermission, User
from sfpcl_credit.members.models import Member, MemberScopeAssignment
from sfpcl_credit.members.modules.active_member_status import ActiveMemberStatusModule
from sfpcl_credit.members.modules.member_authority import evaluate_member_authority


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


class MemberAuthorityActionMatrixTests(TestCase):
    """Executable permission-versus-persisted-scope rows for every public member action."""

    def setUp(self):
        role = Role.objects.create(
            role_code="member_action_matrix",
            role_name="Member Action Matrix",
            is_system_role=False,
            status="active",
        )
        for code in sorted(set(ACTION_PERMISSIONS.values())):
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
            member_type="individual_farmer",
            legal_name="Other Matrix Member",
            display_name="Other Matrix Member",
            folio_number="MATRIX-2",
            membership_status="active",
            kyc_status="verified",
            default_status="no_default",
        )

    def _assert_action_row(self, action):
        permission = ACTION_PERMISSIONS[action]
        before = self._ledger()

        denied = evaluate_member_authority(
            actor_user=self.actor,
            member=self.member,
            permission=permission,
        )

        self.assertEqual(
            (denied.allowed, denied.reason, denied.error_code),
            (False, "object_scope_denied", "OBJECT_ACCESS_DENIED"),
        )
        self.assertEqual(self._ledger(), before)

        assignment = MemberScopeAssignment.objects.create(
            user=self.actor,
            permission_code=permission,
            scope_type="assigned",
            member=self.member,
        )
        allowed = evaluate_member_authority(
            actor_user=self.actor,
            member=self.member,
            permission=permission,
        )
        unrelated = evaluate_member_authority(
            actor_user=self.actor,
            member=self.other_member,
            permission=permission,
        )
        different_permission = next(
            code for code in sorted(set(ACTION_PERMISSIONS.values())) if code != permission
        )
        differently_permissioned = evaluate_member_authority(
            actor_user=self.actor,
            member=self.member,
            permission=different_permission,
        )

        self.assertTrue(allowed.allowed)
        self.assertFalse(unrelated.allowed)
        self.assertFalse(differently_permissioned.allowed)
        self.assertEqual(
            self._ledger(),
            {**before, "scope_assignments": before["scope_assignments"] + 1},
        )
        assignment.delete()

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

        return {
            "members": Member.objects.count(),
            "scope_assignments": MemberScopeAssignment.objects.count(),
            "supply": ProduceSupplyRecord.objects.count(),
            "service_evidence": MemberServiceEvidence.objects.count(),
            "active_status": ActiveMemberStatus.objects.count(),
            "history": MemberChangeHistory.objects.count(),
            "audit": AuditLog.objects.count(),
            "workflow": WorkflowEvent.objects.count(),
        }

    def test_list_authority_row(self): self._assert_action_row("list")
    def test_detail_authority_row(self): self._assert_action_row("detail")
    def test_update_authority_row(self): self._assert_action_row("update")
    def test_identity_approval_authority_row(self): self._assert_action_row("identity_approval")
    def test_supply_capture_authority_row(self): self._assert_action_row("supply_capture")
    def test_supply_verification_authority_row(self): self._assert_action_row("supply_verification")
    def test_service_evidence_create_authority_row(self): self._assert_action_row("service_evidence_create")
    def test_service_evidence_update_authority_row(self): self._assert_action_row("service_evidence_update")
    def test_active_status_calculation_authority_row(self): self._assert_action_row("active_status_calculation")
    def test_active_status_verification_authority_row(self): self._assert_action_row("active_status_verification")

    def test_actorless_calculator_exposes_no_unused_actor_authority_interface(self):
        self.assertFalse(hasattr(ActiveMemberStatusModule, "calculate_for_actor"))
