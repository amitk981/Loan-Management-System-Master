import inspect
import uuid

import jwt
from django.conf import settings
from django.test import RequestFactory
from django.utils import timezone

from sfpcl_credit.identity.models import (
    AuditLog,
    Permission,
    Role,
    RolePermission,
    Team,
    UserTeamMembership,
)
from sfpcl_credit.identity import views
from sfpcl_credit.identity.modules import auth_service, tokens
from sfpcl_credit.tests.base import IdentityTestCase


class AuthModuleTests(IdentityTestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()

    def _request(self):
        return self.factory.post(
            "/api/v1/auth/login/",
            HTTP_X_REQUEST_ID="req-module-001",
            HTTP_USER_AGENT="module-test",
            REMOTE_ADDR="10.9.9.9",
        )

    def test_authenticate_user_returns_active_user(self):
        user = auth_service.authenticate_user(
            "credit.manager@sfpcl.example", "CorrectHorse123!"
        )
        self.assertEqual(user.user_id, self.user.user_id)

    def test_authenticate_user_rejects_wrong_password_as_invalid_credentials(self):
        with self.assertRaises(auth_service.CredentialError) as error:
            auth_service.authenticate_user("credit.manager@sfpcl.example", "wrong")
        self.assertEqual(error.exception.outcome, "invalid_credentials")
        self.assertIsNone(error.exception.user)

    def test_authenticate_user_rejects_inactive_user(self):
        self.user.status = "suspended"
        self.user.save(update_fields=["status"])
        with self.assertRaises(auth_service.CredentialError) as error:
            auth_service.authenticate_user(
                "credit.manager@sfpcl.example", "CorrectHorse123!"
            )
        self.assertEqual(error.exception.outcome, "inactive_user")
        self.assertEqual(error.exception.user.user_id, self.user.user_id)

    def test_issue_login_tokens_and_session_creates_active_session_and_payload(self):
        session, payload = auth_service.issue_login_tokens_and_session(
            self.user, self._request()
        )
        self.assertEqual(session.session_status, "active")
        self.assertEqual(session.ip_address, "10.9.9.9")
        self.assertEqual(session.user_agent, "module-test")
        self.assertNotEqual(session.refresh_token_hash, "")
        self.assertEqual(payload["token_type"], "Bearer")
        self.assertIn("access_token", payload)
        self.assertIn("refresh_token", payload)
        self.assertEqual(payload["user"]["email"], self.user.email)
        self.assertEqual(payload["user"]["role_codes"], ["credit_manager"])
        # The issued access token decodes and carries the session binding.
        claims = auth_service.validate_access_token(payload["access_token"])
        self.assertEqual(claims["session_id"], str(session.user_session_id))

    def test_rotate_refresh_token_replaces_previous_token(self):
        session, payload = auth_service.issue_login_tokens_and_session(
            self.user, self._request()
        )
        original = payload["refresh_token"]
        validated = auth_service.validate_refresh_session(original)
        rotated = auth_service.rotate_refresh_token(validated)
        self.assertNotEqual(rotated, original)
        # Replaying the original refresh token is rejected after rotation.
        with self.assertRaises(tokens.TokenError):
            auth_service.validate_refresh_session(original)
        # The rotated token validates.
        self.assertEqual(
            auth_service.validate_refresh_session(rotated).user_session_id,
            session.user_session_id,
        )

    def test_revoke_session_for_logout_blocks_future_refresh(self):
        session, payload = auth_service.issue_login_tokens_and_session(
            self.user, self._request()
        )
        refresh_token = payload["refresh_token"]
        validated = auth_service.validate_refresh_session(refresh_token)
        auth_service.revoke_session_for_logout(validated)
        session.refresh_from_db()
        self.assertEqual(session.session_status, "revoked")
        self.assertEqual(session.revoked_reason, "logout")
        with self.assertRaises(tokens.TokenError):
            auth_service.validate_refresh_session(refresh_token)

    def test_validate_refresh_session_rejects_access_token_type(self):
        session, payload = auth_service.issue_login_tokens_and_session(
            self.user, self._request()
        )
        with self.assertRaises(tokens.TokenError):
            auth_service.validate_refresh_session(payload["access_token"])

    def test_validate_access_token_rejects_expired_token(self):
        expired_at = timezone.now() - timezone.timedelta(minutes=1)
        token = jwt.encode(
            {
                "token_type": "access",
                "user_id": str(self.user.user_id),
                "session_id": str(uuid.uuid4()),
                "iat": int((expired_at - timezone.timedelta(minutes=1)).timestamp()),
                "exp": int(expired_at.timestamp()),
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        with self.assertRaises(tokens.TokenError) as error:
            auth_service.validate_access_token(token)
        self.assertEqual(error.exception.code, "TOKEN_EXPIRED")

    def test_validate_access_token_rejects_wrong_token_type(self):
        session, payload = auth_service.issue_login_tokens_and_session(
            self.user, self._request()
        )
        with self.assertRaises(tokens.TokenError):
            auth_service.validate_access_token(payload["refresh_token"])

    def test_validate_access_session_rejects_revoked_session(self):
        session, payload = auth_service.issue_login_tokens_and_session(
            self.user, self._request()
        )
        session.revoke("logout")

        with self.assertRaises(tokens.TokenError) as error:
            auth_service.validate_access_session(payload["access_token"])

        self.assertEqual(error.exception.code, "INVALID_TOKEN")

    def test_validate_access_session_rejects_inactive_user_and_revokes_session(self):
        session, payload = auth_service.issue_login_tokens_and_session(
            self.user, self._request()
        )
        self.user.status = "suspended"
        self.user.save(update_fields=["status"])

        with self.assertRaises(tokens.TokenError) as error:
            auth_service.validate_access_session(payload["access_token"])

        self.assertEqual(error.exception.code, "INVALID_TOKEN")
        session.refresh_from_db()
        self.assertEqual(session.session_status, "revoked")
        self.assertEqual(session.revoked_reason, "user_status_changed")

    def test_effective_permission_codes_are_sorted_for_active_primary_role(self):
        later = Permission.objects.create(
            permission_code="credit.appraisal.review",
            permission_name="Review appraisal",
            module_name="credit",
            risk_level="medium",
        )
        earlier = Permission.objects.create(
            permission_code="approvals.case.create",
            permission_name="Create approval case",
            module_name="approvals",
            risk_level="high",
        )
        RolePermission.objects.create(role=self.role, permission=later)
        RolePermission.objects.create(role=self.role, permission=earlier)

        self.assertEqual(
            auth_service.effective_permission_codes(self.user),
            ["approvals.case.create", "credit.appraisal.review"],
        )

    def test_effective_permission_codes_empty_for_inactive_role(self):
        Permission.objects.create(
            permission_code="credit.appraisal.review",
            permission_name="Review appraisal",
            module_name="credit",
            risk_level="medium",
        )
        self.role.status = "inactive"
        self.role.save(update_fields=["status"])

        self.assertEqual(auth_service.effective_permission_codes(self.user), [])

    def test_effective_permission_codes_empty_for_zero_link_role(self):
        zero_link_role = Role.objects.create(
            role_code="sales_team_user",
            role_name="Sales Team User",
            is_system_role=True,
            status="active",
        )
        self.user.primary_role = zero_link_role
        self.user.save(update_fields=["primary_role"])

        self.assertEqual(auth_service.effective_permission_codes(self.user), [])

    def test_role_payload_is_empty_for_inactive_primary_role(self):
        self.role.status = "inactive"
        self.role.save(update_fields=["status"])

        self.assertEqual(auth_service.role_payload(self.user), [])

    def test_team_payload_is_sorted_and_excludes_inactive_memberships_and_teams(self):
        treasury = Team.objects.create(
            team_code="treasury",
            team_name="Treasury Team",
            status="active",
        )
        credit = Team.objects.create(
            team_code="credit_assessment",
            team_name="Credit Assessment Team",
            status="active",
        )
        inactive_team = Team.objects.create(
            team_code="audit",
            team_name="Audit Team",
            status="inactive",
        )
        inactive_membership_team = Team.objects.create(
            team_code="compliance",
            team_name="Compliance Team",
            status="active",
        )
        UserTeamMembership.objects.create(user=self.user, team=treasury, status="active")
        UserTeamMembership.objects.create(user=self.user, team=credit, status="active")
        UserTeamMembership.objects.create(
            user=self.user, team=inactive_team, status="active"
        )
        UserTeamMembership.objects.create(
            user=self.user,
            team=inactive_membership_team,
            status="inactive",
        )

        self.assertEqual(
            auth_service.team_payload(self.user),
            [
                {
                    "team_code": "credit_assessment",
                    "team_name": "Credit Assessment Team",
                },
                {"team_code": "treasury", "team_name": "Treasury Team"},
            ],
        )

    def test_current_user_payload_uses_effective_permissions_for_available_actions(self):
        permission = Permission.objects.create(
            permission_code="credit.appraisal.review",
            permission_name="Review appraisal",
            module_name="credit",
            risk_level="medium",
        )
        RolePermission.objects.create(role=self.role, permission=permission)

        payload = auth_service.current_user_payload(self.user)

        self.assertEqual(payload["role_codes"], ["credit_manager"])
        self.assertEqual(
            payload["roles"],
            [{"role_code": "credit_manager", "role_name": "Credit Manager"}],
        )
        self.assertEqual(payload["permissions"], ["credit.appraisal.review"])
        self.assertEqual(payload["available_actions"], ["credit.appraisal.review"])

    def test_current_user_view_delegates_auth_orchestration_to_service_boundary(self):
        view_source = inspect.getsource(views.me)
        module_source = inspect.getsource(views)

        self.assertIn("current_user_payload_for_access_token", view_source)
        self.assertNotIn("UserSession", module_source)
        self.assertNotIn("Permission", module_source)

    def test_record_auth_event_writes_audit_row(self):
        request = self._request()
        session, _ = auth_service.issue_login_tokens_and_session(self.user, request)
        AuditLog.objects.all().delete()
        auth_service.record_auth_event(
            request,
            "auth.login.succeeded",
            user=self.user,
            session=session,
            outcome="success",
        )
        audit = AuditLog.objects.get(action="auth.login.succeeded")
        self.assertEqual(audit.actor_user, self.user)
        self.assertEqual(audit.entity_type, "user_session")
        self.assertEqual(audit.entity_id, session.user_session_id)
        self.assertEqual(audit.ip_address, "10.9.9.9")
        self.assertEqual(audit.user_agent, "module-test")
