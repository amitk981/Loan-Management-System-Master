import os

import django
from django.test import Client, SimpleTestCase


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


STANDARD_META_KEYS = {"request_id", "timestamp", "api_version"}
HEALTH_ENDPOINTS = [
    "/api/v1/health/live/",
    "/api/v1/health/ready/",
    "/api/v1/health/deep/",
]
IDENTITY_MODELS = [Role, Team, User, UserTeamMembership, UserSession, AuditLog]


def ensure_identity_tables():
    existing_tables = set(connection.introspection.table_names())
    with connection.schema_editor() as schema_editor:
        for model in IDENTITY_MODELS:
            if model._meta.db_table not in existing_tables:
                schema_editor.create_model(model)


class ApiEnvelopeTests(SimpleTestCase):
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

    def _login(self):
        return Client().post(
            "/api/v1/auth/login/",
            data={
                "email": "credit.manager@sfpcl.example",
                "password": "CorrectHorse123!",
            },
            content_type="application/json",
        )

    def test_all_health_endpoints_include_api_version_v1(self):
        for endpoint in HEALTH_ENDPOINTS:
            response = Client().get(endpoint)
            self.assertEqual(response.status_code, 200, endpoint)
            meta = response.json()["meta"]
            self.assertEqual(meta.get("api_version"), "v1", endpoint)

    def test_health_and_auth_share_the_same_standard_meta_keys(self):
        metas = []
        for endpoint in HEALTH_ENDPOINTS:
            metas.append(Client().get(endpoint).json()["meta"])

        login_response = self._login()
        self.assertEqual(login_response.status_code, 200)
        refresh_token = login_response.json()["data"]["refresh_token"]
        metas.append(login_response.json()["meta"])

        refresh_response = Client().post(
            "/api/v1/auth/refresh/",
            data={"refresh_token": refresh_token},
            content_type="application/json",
        )
        rotated_refresh_token = refresh_response.json()["data"]["refresh_token"]
        metas.append(refresh_response.json()["meta"])

        logout_response = Client().post(
            "/api/v1/auth/logout/",
            data={"refresh_token": rotated_refresh_token},
            content_type="application/json",
        )
        metas.append(logout_response.json()["meta"])

        for meta in metas:
            self.assertEqual(set(meta.keys()), STANDARD_META_KEYS)
            self.assertEqual(meta["api_version"], "v1")

    def test_error_envelope_uses_the_same_standard_meta_keys(self):
        response = Client().post(
            "/api/v1/auth/login/",
            data={"email": "credit.manager@sfpcl.example", "password": "nope"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        payload = response.json()
        self.assertEqual(payload["success"], False)
        self.assertEqual(set(payload["meta"].keys()), STANDARD_META_KEYS)
        self.assertEqual(payload["meta"]["api_version"], "v1")

    def test_shared_helper_is_the_single_production_envelope_source(self):
        # Health (ops) and auth (identity.views) must both delegate to the one
        # shared envelope helper rather than defining their own success_response.
        import sfpcl_credit.api as shared_api
        import sfpcl_credit.identity.views as auth_views
        import sfpcl_credit.ops as ops

        self.assertIs(ops.success_response, shared_api.success_response)
        self.assertIs(auth_views.success_response, shared_api.success_response)
