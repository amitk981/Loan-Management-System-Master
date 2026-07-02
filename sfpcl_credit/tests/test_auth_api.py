import os

import django
from django.db import connection
from django.test import Client, SimpleTestCase


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sfpcl_credit.config.settings")
django.setup()

from sfpcl_credit.identity.models import (
    AuditLog,
    Role,
    Team,
    User,
    UserSession,
    UserTeamMembership,
)


IDENTITY_MODELS = [Role, Team, User, UserTeamMembership, UserSession, AuditLog]


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
        UserSession.objects.all().delete()
        UserTeamMembership.objects.all().delete()
        User.objects.all().delete()
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
