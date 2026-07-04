import uuid

from django.test import SimpleTestCase

from sfpcl_credit.identity.models import (
    Permission,
    RolePermission,
    Team,
    UserTeamMembership,
)
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.identity.modules import object_permissions
from sfpcl_credit.tests.base import IdentityTestCase


class ObjectPermissionHelperTests(SimpleTestCase):
    def test_owner_with_required_permission_is_allowed(self):
        actor_id = uuid.uuid4()

        result = object_permissions.evaluate_object_access(
            actor_user_id=actor_id,
            actor_team_codes=[],
            actor_permission_codes={"loan_application.read"},
            required_permission="loan_application.read",
            object_owner_user_id=actor_id,
            object_team_code=None,
        )

        self.assertTrue(result.allowed)
        self.assertEqual(result.reason, object_permissions.ACCESS_ALLOWED_OWNER)
        self.assertEqual(result.error_code, None)

    def test_team_member_with_required_permission_is_allowed(self):
        result = object_permissions.evaluate_object_access(
            actor_user_id=uuid.uuid4(),
            actor_team_codes=["credit_assessment", "treasury"],
            actor_permission_codes={"loan_application.read"},
            required_permission="loan_application.read",
            object_owner_user_id=uuid.uuid4(),
            object_team_code="credit_assessment",
        )

        self.assertTrue(result.allowed)
        self.assertEqual(result.reason, object_permissions.ACCESS_ALLOWED_TEAM)
        self.assertEqual(result.error_code, None)

    def test_missing_required_permission_is_denied_before_scope(self):
        actor_id = uuid.uuid4()

        result = object_permissions.evaluate_object_access(
            actor_user_id=actor_id,
            actor_team_codes=["credit_assessment"],
            actor_permission_codes={"loan_application.update"},
            required_permission="loan_application.read",
            object_owner_user_id=actor_id,
            object_team_code="credit_assessment",
        )

        self.assertFalse(result.allowed)
        self.assertEqual(result.reason, object_permissions.ACCESS_MISSING_PERMISSION)
        self.assertEqual(result.error_code, object_permissions.PERMISSION_DENIED)

    def test_owner_mismatch_with_no_matching_team_is_denied(self):
        result = object_permissions.evaluate_object_access(
            actor_user_id=uuid.uuid4(),
            actor_team_codes=[],
            actor_permission_codes={"loan_application.read"},
            required_permission="loan_application.read",
            object_owner_user_id=uuid.uuid4(),
            object_team_code=None,
        )

        self.assertFalse(result.allowed)
        self.assertEqual(result.reason, object_permissions.ACCESS_OWNER_MISMATCH)
        self.assertEqual(result.error_code, object_permissions.OBJECT_ACCESS_DENIED)

    def test_team_mismatch_with_no_owner_fact_is_denied(self):
        result = object_permissions.evaluate_object_access(
            actor_user_id=uuid.uuid4(),
            actor_team_codes=["treasury"],
            actor_permission_codes={"loan_application.read"},
            required_permission="loan_application.read",
            object_owner_user_id=None,
            object_team_code="credit_assessment",
        )

        self.assertFalse(result.allowed)
        self.assertEqual(result.reason, object_permissions.ACCESS_TEAM_MISMATCH)
        self.assertEqual(result.error_code, object_permissions.OBJECT_ACCESS_DENIED)

    def test_unknown_scope_is_denied_without_explicit_global_override(self):
        result = object_permissions.evaluate_object_access(
            actor_user_id=uuid.uuid4(),
            actor_team_codes=["credit_assessment"],
            actor_permission_codes={"loan_application.read"},
            required_permission="loan_application.read",
            object_owner_user_id=None,
            object_team_code=None,
        )

        self.assertFalse(result.allowed)
        self.assertEqual(result.reason, object_permissions.ACCESS_SCOPE_UNKNOWN)
        self.assertEqual(result.error_code, object_permissions.OBJECT_ACCESS_DENIED)
        self.assertTrue(result.approval_required)

    def test_explicit_global_override_allows_when_permission_is_present(self):
        result = object_permissions.evaluate_object_access(
            actor_user_id=uuid.uuid4(),
            actor_team_codes=[],
            actor_permission_codes={"loan_application.read"},
            required_permission="loan_application.read",
            object_owner_user_id=None,
            object_team_code=None,
            allow_global=True,
        )

        self.assertTrue(result.allowed)
        self.assertEqual(result.reason, object_permissions.ACCESS_ALLOWED_GLOBAL)
        self.assertEqual(result.error_code, None)
        self.assertFalse(result.approval_required)

    def test_global_override_does_not_bypass_missing_permission(self):
        result = object_permissions.evaluate_object_access(
            actor_user_id=uuid.uuid4(),
            actor_team_codes=[],
            actor_permission_codes=[],
            required_permission="loan_application.read",
            object_owner_user_id=None,
            object_team_code=None,
            allow_global=True,
        )

        self.assertFalse(result.allowed)
        self.assertEqual(result.reason, object_permissions.ACCESS_MISSING_PERMISSION)
        self.assertEqual(result.error_code, object_permissions.PERMISSION_DENIED)


class ObjectPermissionHarnessIntegrationTests(IdentityTestCase):
    def test_auth_service_permissions_and_user_team_codes_feed_object_access(self):
        permission = Permission.objects.create(
            permission_code="loan_application.read",
            permission_name="Read loan application",
            module_name="applications",
            risk_level="medium",
        )
        RolePermission.objects.create(role=self.role, permission=permission)
        team = Team.objects.create(
            team_code="credit_assessment",
            team_name="Credit Assessment",
            status="active",
        )
        UserTeamMembership.objects.create(user=self.user, team=team, status="active")

        result = object_permissions.evaluate_object_access(
            actor_user_id=self.user.user_id,
            actor_team_codes=self.user.team_codes(),
            actor_permission_codes=auth_service.effective_permission_codes(self.user),
            required_permission="loan_application.read",
            object_owner_user_id=uuid.uuid4(),
            object_team_code=auth_service.team_payload(self.user)[0]["team_code"],
        )

        self.assertTrue(result.allowed)
        self.assertEqual(result.reason, object_permissions.ACCESS_ALLOWED_TEAM)
