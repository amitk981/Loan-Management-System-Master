import os
import uuid

import django
import jwt
from django.conf import settings
from django.test import RequestFactory, SimpleTestCase
from django.utils import timezone


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sfpcl_credit.config.settings")
django.setup()

from django.db import connection

from sfpcl_credit.identity.models import (
    AuditLog,
    Role,
    Team,
    User,
    UserSession,
    UserTeamMembership,
)
from sfpcl_credit.identity.modules import auth_service, tokens


IDENTITY_MODELS = [Role, Team, User, UserTeamMembership, UserSession, AuditLog]


def ensure_identity_tables():
    existing_tables = set(connection.introspection.table_names())
    with connection.schema_editor() as schema_editor:
        for model in IDENTITY_MODELS:
            if model._meta.db_table not in existing_tables:
                schema_editor.create_model(model)


class AuthModuleTests(SimpleTestCase):
    databases = {"default"}

    def setUp(self):
        ensure_identity_tables()
        AuditLog.objects.all().delete()
        UserSession.objects.all().delete()
        UserTeamMembership.objects.all().delete()
        User.objects.all().delete()
        Team.objects.all().delete()
        Role.objects.all().delete()
        self.factory = RequestFactory()
        self.role = Role.objects.create(
            role_code="credit_manager",
            role_name="Credit Manager",
            description="Credit workflow owner",
            is_system_role=True,
            status="active",
        )
        self.user = User.objects.create(
            full_name="Credit Manager",
            email="credit.manager@sfpcl.example",
            status="active",
            primary_role=self.role,
        )
        self.user.set_password("CorrectHorse123!")
        self.user.save()

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
