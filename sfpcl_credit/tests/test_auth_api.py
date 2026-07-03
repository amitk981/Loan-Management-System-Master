import hashlib
import os
import subprocess
import sys
import uuid
from pathlib import Path

import django
import jwt
from django.conf import settings
from django.db import connection
from django.test import Client, SimpleTestCase
from django.utils import timezone


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sfpcl_credit.config.settings")
django.setup()

from sfpcl_credit.identity.models import (
    AuditLog,
    Permission,
    Role,
    RolePermission,
    Team,
    User,
    UserSession,
    UserTeamMembership,
)
from sfpcl_credit.identity.views import TokenError, decode_token


IDENTITY_MODELS = [
    Role,
    Team,
    Permission,
    User,
    UserTeamMembership,
    UserSession,
    RolePermission,
    AuditLog,
]


def ensure_identity_tables():
    existing_tables = set(connection.introspection.table_names())
    with connection.schema_editor() as schema_editor:
        for model in IDENTITY_MODELS:
            if model._meta.db_table not in existing_tables:
                schema_editor.create_model(model)


class AuthApiTests(SimpleTestCase):
    databases = {"default"}

    def setUp(self):
        ensure_identity_tables()
        AuditLog.objects.all().delete()
        RolePermission.objects.all().delete()
        UserSession.objects.all().delete()
        UserTeamMembership.objects.all().delete()
        User.objects.all().delete()
        Permission.objects.all().delete()
        Team.objects.all().delete()
        Role.objects.all().delete()
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

    def test_current_user_endpoint_returns_profile_permissions_and_actions(self):
        team = Team.objects.create(
            team_code="credit_assessment",
            team_name="Credit Assessment",
            status="active",
        )
        UserTeamMembership.objects.create(user=self.user, team=team, status="active")
        first_permission = Permission.objects.create(
            permission_code="credit.appraisal.review",
            permission_name="Review appraisal",
            module_name="credit",
            risk_level="medium",
        )
        second_permission = Permission.objects.create(
            permission_code="approvals.case.create",
            permission_name="Create approval case",
            module_name="approvals",
            risk_level="high",
        )
        RolePermission.objects.create(role=self.role, permission=first_permission)
        RolePermission.objects.create(role=self.role, permission=second_permission)
        client = Client()
        login_response = client.post(
            "/api/v1/auth/login/",
            data={
                "email": "credit.manager@sfpcl.example",
                "password": "CorrectHorse123!",
            },
            content_type="application/json",
        )
        access_token = login_response.json()["data"]["access_token"]

        response = client.get(
            "/api/v1/auth/me/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Request-ID": "req-me-001",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["success"], True)
        self.assertEqual(payload["meta"]["request_id"], "req-me-001")
        self.assertEqual(payload["meta"]["api_version"], "v1")
        self.assertEqual(payload["data"]["user_id"], str(self.user.user_id))
        self.assertEqual(payload["data"]["full_name"], "Credit Manager")
        self.assertEqual(payload["data"]["email"], "credit.manager@sfpcl.example")
        self.assertEqual(payload["data"]["status"], "active")
        self.assertEqual(payload["data"]["role_codes"], ["credit_manager"])
        self.assertEqual(payload["data"]["team_codes"], ["credit_assessment"])
        self.assertEqual(
            payload["data"]["permissions"],
            ["approvals.case.create", "credit.appraisal.review"],
        )
        self.assertEqual(
            payload["data"]["available_actions"],
            ["approvals.case.create", "credit.appraisal.review"],
        )

    def _login_tokens(self):
        response = Client().post(
            "/api/v1/auth/login/",
            data={
                "email": "credit.manager@sfpcl.example",
                "password": "CorrectHorse123!",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]

    def test_current_user_requires_bearer_token(self):
        response = Client().get("/api/v1/auth/me/")

        self.assertEqual(response.status_code, 401)
        payload = response.json()
        self.assertEqual(payload["success"], False)
        self.assertEqual(payload["error"]["code"], "AUTH_REQUIRED")
        self.assertEqual(payload["meta"]["api_version"], "v1")

    def test_current_user_rejects_expired_access_token(self):
        expired_at = timezone.now() - timezone.timedelta(minutes=1)
        session = UserSession.objects.create(
            user=self.user,
            refresh_token_hash="unused",
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )
        token = jwt.encode(
            {
                "token_type": "access",
                "user_id": str(self.user.user_id),
                "session_id": str(session.user_session_id),
                "email": self.user.email,
                "role_codes": ["credit_manager"],
                "team_codes": [],
                "permissions_version": self.user.permissions_version(),
                "iat": int((expired_at - timezone.timedelta(minutes=1)).timestamp()),
                "exp": int(expired_at.timestamp()),
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        response = Client().get(
            "/api/v1/auth/me/",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "TOKEN_EXPIRED")

    def test_current_user_rejects_refresh_token(self):
        tokens = self._login_tokens()

        response = Client().get(
            "/api/v1/auth/me/",
            headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "INVALID_TOKEN")

    def test_current_user_rejects_inactive_user(self):
        tokens = self._login_tokens()
        self.user.status = "suspended"
        self.user.save(update_fields=["status"])

        response = Client().get(
            "/api/v1/auth/me/",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "INVALID_TOKEN")
        session = UserSession.objects.get(user=self.user)
        self.assertEqual(session.session_status, "revoked")
        self.assertEqual(session.revoked_reason, "user_status_changed")

    def test_current_user_rejects_revoked_session(self):
        tokens = self._login_tokens()
        logout_response = Client().post(
            "/api/v1/auth/logout/",
            data={"refresh_token": tokens["refresh_token"]},
            content_type="application/json",
        )
        self.assertEqual(logout_response.status_code, 200)

        response = Client().get(
            "/api/v1/auth/me/",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "INVALID_TOKEN")

    def test_active_user_can_login_and_receives_tokens(self):
        response = Client().post(
            "/api/v1/auth/login/",
            data={
                "email": "credit.manager@sfpcl.example",
                "password": "CorrectHorse123!",
            },
            content_type="application/json",
            headers={
                "X-Request-ID": "req-login-001",
                "User-Agent": "Django test client",
            },
            REMOTE_ADDR="10.0.0.1",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["success"], True)
        self.assertEqual(payload["meta"]["request_id"], "req-login-001")
        self.assertEqual(payload["data"]["token_type"], "Bearer")
        self.assertIn("access_token", payload["data"])
        self.assertIn("refresh_token", payload["data"])
        self.assertEqual(payload["data"]["user"]["email"], self.user.email)
        self.assertEqual(payload["data"]["user"]["role_codes"], ["credit_manager"])

        session = UserSession.objects.get(user=self.user)
        self.assertEqual(session.session_status, "active")
        self.assertEqual(session.ip_address, "10.0.0.1")
        self.assertEqual(session.user_agent, "Django test client")

        audit = AuditLog.objects.get(action="auth.login.succeeded")
        self.assertEqual(audit.actor_user, self.user)
        self.assertEqual(audit.entity_type, "user_session")
        self.assertEqual(audit.entity_id, session.user_session_id)

    def test_invalid_credentials_do_not_issue_tokens_and_are_audited(self):
        response = Client().post(
            "/api/v1/auth/login/",
            data={
                "email": "credit.manager@sfpcl.example",
                "password": "WrongPassword123!",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        payload = response.json()
        self.assertEqual(payload["success"], False)
        self.assertEqual(payload["error"]["code"], "INVALID_CREDENTIALS")
        self.assertEqual(UserSession.objects.count(), 0)

        audit = AuditLog.objects.get(action="auth.login.failed")
        self.assertEqual(audit.actor_user, None)
        self.assertEqual(audit.new_value_json["outcome"], "invalid_credentials")

    def test_inactive_user_cannot_login(self):
        self.user.status = "suspended"
        self.user.save(update_fields=["status"])

        response = Client().post(
            "/api/v1/auth/login/",
            data={
                "email": "credit.manager@sfpcl.example",
                "password": "CorrectHorse123!",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "INVALID_CREDENTIALS")
        self.assertEqual(UserSession.objects.count(), 0)

        audit = AuditLog.objects.get(action="auth.login.failed")
        self.assertEqual(audit.actor_user, self.user)
        self.assertEqual(audit.new_value_json["outcome"], "inactive_user")

    def test_refresh_rotates_refresh_token_and_rejects_old_token(self):
        login_response = Client().post(
            "/api/v1/auth/login/",
            data={
                "email": "credit.manager@sfpcl.example",
                "password": "CorrectHorse123!",
            },
            content_type="application/json",
        )
        original_refresh_token = login_response.json()["data"]["refresh_token"]

        refresh_response = Client().post(
            "/api/v1/auth/refresh/",
            data={"refresh_token": original_refresh_token},
            content_type="application/json",
        )

        self.assertEqual(refresh_response.status_code, 200)
        rotated_refresh_token = refresh_response.json()["data"]["refresh_token"]
        self.assertNotEqual(rotated_refresh_token, original_refresh_token)
        self.assertEqual(UserSession.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="auth.refresh.succeeded").count(), 1
        )

        replay_response = Client().post(
            "/api/v1/auth/refresh/",
            data={"refresh_token": original_refresh_token},
            content_type="application/json",
        )
        self.assertEqual(replay_response.status_code, 401)
        self.assertEqual(replay_response.json()["error"]["code"], "INVALID_TOKEN")

    def test_refresh_token_signed_with_wrong_secret_is_rejected(self):
        client = Client()
        login_response = client.post(
            "/api/v1/auth/login/",
            data={
                "email": "credit.manager@sfpcl.example",
                "password": "CorrectHorse123!",
            },
            content_type="application/json",
        )
        refresh_token = login_response.json()["data"]["refresh_token"]
        claims = jwt.decode(refresh_token, options={"verify_signature": False})
        wrong_secret_token = jwt.encode(claims, "wrong-test-secret", algorithm="HS256")
        session = UserSession.objects.get(user=self.user)
        session.refresh_token_hash = hashlib.sha256(
            wrong_secret_token.encode("utf-8")
        ).hexdigest()
        session.save(update_fields=["refresh_token_hash"])

        response = client.post(
            "/api/v1/auth/refresh/",
            data={"refresh_token": wrong_secret_token},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "INVALID_TOKEN")

    def test_expired_access_token_is_rejected(self):
        expired_at = timezone.now() - timezone.timedelta(minutes=1)
        token = jwt.encode(
            {
                "token_type": "access",
                "user_id": str(self.user.user_id),
                "session_id": str(uuid.uuid4()),
                "email": self.user.email,
                "role_codes": ["credit_manager"],
                "team_codes": [],
                "permissions_version": self.user.permissions_version(),
                "iat": int((expired_at - timezone.timedelta(minutes=1)).timestamp()),
                "exp": int(expired_at.timestamp()),
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        with self.assertRaises(TokenError) as error:
            decode_token(token, expected_type="access")

        self.assertEqual(error.exception.code, "TOKEN_EXPIRED")

    def test_logout_revokes_session_and_blocks_future_refresh(self):
        login_response = Client().post(
            "/api/v1/auth/login/",
            data={
                "email": "credit.manager@sfpcl.example",
                "password": "CorrectHorse123!",
            },
            content_type="application/json",
        )
        refresh_token = login_response.json()["data"]["refresh_token"]

        logout_response = Client().post(
            "/api/v1/auth/logout/",
            data={"refresh_token": refresh_token},
            content_type="application/json",
        )

        self.assertEqual(logout_response.status_code, 200)
        self.assertEqual(logout_response.json()["data"], {"logged_out": True})
        session = UserSession.objects.get(user=self.user)
        self.assertEqual(session.session_status, "revoked")
        self.assertEqual(session.revoked_reason, "logout")
        self.assertEqual(AuditLog.objects.filter(action="auth.logout.succeeded").count(), 1)

        refresh_response = Client().post(
            "/api/v1/auth/refresh/",
            data={"refresh_token": refresh_token},
            content_type="application/json",
        )
        self.assertEqual(refresh_response.status_code, 401)
        self.assertEqual(refresh_response.json()["error"]["code"], "INVALID_TOKEN")

    def test_secret_key_comes_from_environment_with_dev_fallback(self):
        env = os.environ.copy()
        env["SFPCL_SECRET_KEY"] = "test-env-secret-key"
        repo_root = Path(__file__).resolve().parents[2]

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import os; "
                    "os.environ.setdefault('DJANGO_SETTINGS_MODULE', "
                    "'sfpcl_credit.config.settings'); "
                    "from django.conf import settings; "
                    "print(settings.SECRET_KEY)"
                ),
            ],
            cwd=repo_root,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertEqual(result.stdout.strip(), "test-env-secret-key")
