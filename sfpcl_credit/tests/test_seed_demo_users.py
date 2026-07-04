from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from sfpcl_credit.identity.models import (
    AuditLog,
    Permission,
    RolePermission,
    User,
    UserTeamMembership,
)
from sfpcl_credit.tests.api_contracts import (
    assert_error_envelope,
    assert_pagination_shape,
    assert_success_envelope,
)


SYSTEM_ADMIN_EMAIL = "demo.system_admin@sfpcl.example"
TRACER_EMAIL = "demo.tracer@sfpcl.example"
ZERO_EMAIL = "demo.zero@sfpcl.example"
DEMO_PASSWORD = "DemoStaff123!"
TRACER_PERMISSION = "tracer.lifecycle.run"
DEMO_EMAILS = [
    SYSTEM_ADMIN_EMAIL,
    "demo.credit_manager@sfpcl.example",
    "demo.compliance@sfpcl.example",
    "demo.treasury@sfpcl.example",
    "demo.internal_auditor@sfpcl.example",
    TRACER_EMAIL,
    ZERO_EMAIL,
]


class SeedDemoUsersTests(TestCase):
    """Local demo users must be deterministic without weakening production guards."""

    def test_seed_refuses_without_explicit_demo_guard(self):
        with self.assertRaisesMessage(CommandError, "SFPCL_ALLOW_DEMO_SEED=true"):
            call_command("seed_demo_users")

        self.assertFalse(User.objects.filter(email=SYSTEM_ADMIN_EMAIL).exists())

    def test_seed_refuses_when_debug_is_true_but_demo_flag_is_missing(self):
        with patch.dict("os.environ", {"SFPCL_DEBUG": "true"}, clear=False):
            with self.assertRaisesMessage(CommandError, "SFPCL_ALLOW_DEMO_SEED=true"):
                call_command("seed_demo_users")

        self.assertFalse(User.objects.filter(email=SYSTEM_ADMIN_EMAIL).exists())

    def _seed_demo_users(self):
        with patch.dict(
            "os.environ",
            {"SFPCL_DEBUG": "true", "SFPCL_ALLOW_DEMO_SEED": "true"},
            clear=False,
        ):
            call_command("seed_demo_users")

    def _login_access_token(self, email):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": email, "password": DEMO_PASSWORD},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        assert_success_envelope(self, response.json())
        return response.json()["data"]["access_token"]

    def test_guarded_seed_creates_expected_demo_users_and_active_memberships(self):
        self._seed_demo_users()

        users = {
            user.email: user
            for user in User.objects.filter(email__in=DEMO_EMAILS).select_related(
                "primary_role"
            )
        }
        self.assertEqual(set(users), set(DEMO_EMAILS))
        self.assertEqual(users[SYSTEM_ADMIN_EMAIL].primary_role.role_code, "system_admin")
        self.assertEqual(
            users["demo.credit_manager@sfpcl.example"].primary_role.role_code,
            "credit_manager",
        )
        self.assertEqual(
            users["demo.compliance@sfpcl.example"].primary_role.role_code,
            "compliance_team_member",
        )
        self.assertEqual(
            users["demo.treasury@sfpcl.example"].primary_role.role_code,
            "senior_manager_finance",
        )
        self.assertEqual(
            users["demo.internal_auditor@sfpcl.example"].primary_role.role_code,
            "internal_auditor",
        )
        self.assertEqual(users[TRACER_EMAIL].primary_role.role_code, "sales_team_user")
        self.assertEqual(users[ZERO_EMAIL].primary_role.role_code, "management_viewer")
        for user in users.values():
            self.assertEqual(user.status, "active")
            self.assertEqual(user.primary_role.status, "active")
            self.assertTrue(user.check_password(DEMO_PASSWORD))

        self.assertEqual(
            users[SYSTEM_ADMIN_EMAIL].team_codes(),
            ["it"],
        )
        self.assertEqual(
            users["demo.credit_manager@sfpcl.example"].team_codes(),
            ["credit_assessment"],
        )
        self.assertEqual(
            users["demo.compliance@sfpcl.example"].team_codes(),
            ["compliance"],
        )
        self.assertEqual(
            users["demo.treasury@sfpcl.example"].team_codes(),
            ["treasury"],
        )
        self.assertEqual(
            users["demo.internal_auditor@sfpcl.example"].team_codes(),
            ["audit"],
        )
        self.assertEqual(users[TRACER_EMAIL].team_codes(), ["sales"])
        self.assertEqual(users[ZERO_EMAIL].team_codes(), [])

    def test_seed_is_idempotent_and_does_not_touch_e2e_users(self):
        self._seed_demo_users()
        User.objects.filter(email=SYSTEM_ADMIN_EMAIL).update(status="suspended")
        UserTeamMembership.objects.filter(user__email=SYSTEM_ADMIN_EMAIL).update(
            status="inactive"
        )

        self._seed_demo_users()

        self.assertEqual(User.objects.filter(email__in=DEMO_EMAILS).count(), 7)
        self.assertFalse(User.objects.filter(email__startswith="e2e.").exists())
        self.assertEqual(User.objects.filter(email=SYSTEM_ADMIN_EMAIL).count(), 1)
        self.assertEqual(
            UserTeamMembership.objects.filter(
                user__email=SYSTEM_ADMIN_EMAIL,
                team__team_code="it",
            ).count(),
            1,
        )
        admin = User.objects.get(email=SYSTEM_ADMIN_EMAIL)
        self.assertEqual(admin.status, "active")
        self.assertEqual(admin.team_codes(), ["it"])
        self.assertEqual(
            RolePermission.objects.filter(
                role__role_code="sales_team_user",
                permission__permission_code=TRACER_PERMISSION,
            ).count(),
            1,
        )

    def test_seeded_system_admin_logs_in_and_satisfies_auth_me_and_admin_list_contracts(self):
        self._seed_demo_users()
        access_token = self._login_access_token(SYSTEM_ADMIN_EMAIL)

        me = self.client.get(
            "/api/v1/auth/me/",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        self.assertEqual(me.status_code, 200, me.content)
        assert_success_envelope(self, me.json())
        data = me.json()["data"]
        self.assertEqual(data["role_codes"], ["system_admin"])
        self.assertEqual(data["team_codes"], ["it"])
        self.assertIn("users.user.create", data["permissions"])
        self.assertIn("users.user.update", data["permissions"])
        self.assertIn("users.user.disable", data["permissions"])
        self.assertNotIn("manage_users", data["permissions"])

        users = self.client.get(
            "/api/v1/admin/users/?page=1&page_size=20",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        self.assertEqual(users.status_code, 200, users.content)
        assert_pagination_shape(self, users.json())

    def test_seeded_tracer_only_user_has_exact_tracer_permission(self):
        self._seed_demo_users()
        access_token = self._login_access_token(TRACER_EMAIL)

        response = self.client.get(
            "/api/v1/auth/me/",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        self.assertEqual(response.status_code, 200, response.content)
        assert_success_envelope(self, response.json())
        data = response.json()["data"]
        self.assertEqual(data["permissions"], [TRACER_PERMISSION])
        self.assertEqual(data["available_actions"], [TRACER_PERMISSION])
        self.assertNotIn("users.user.update", data["permissions"])
        self.assertNotIn("manage_users", data["permissions"])

    def test_seeded_zero_permission_user_has_neutral_auth_me_payload(self):
        self._seed_demo_users()
        access_token = self._login_access_token(ZERO_EMAIL)

        response = self.client.get(
            "/api/v1/auth/me/",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        self.assertEqual(response.status_code, 200, response.content)
        assert_success_envelope(self, response.json())
        data = response.json()["data"]
        self.assertEqual(data["permissions"], [])
        self.assertEqual(data["available_actions"], [])
        self.assertEqual(data["team_codes"], [])

    def test_login_and_logout_use_existing_auth_audit_path(self):
        self._seed_demo_users()
        login = self.client.post(
            "/api/v1/auth/login/",
            data={"email": SYSTEM_ADMIN_EMAIL, "password": DEMO_PASSWORD},
            content_type="application/json",
        )
        self.assertEqual(login.status_code, 200, login.content)

        logout = self.client.post(
            "/api/v1/auth/logout/",
            data={"refresh_token": login.json()["data"]["refresh_token"]},
            content_type="application/json",
        )

        self.assertEqual(logout.status_code, 200, logout.content)
        self.assertEqual(
            list(
                AuditLog.objects.filter(actor_user__email=SYSTEM_ADMIN_EMAIL)
                .order_by("created_at")
                .values_list("action", flat=True)
            ),
            ["auth.login.succeeded", "auth.logout.succeeded"],
        )

    def test_read_only_demo_user_gets_standard_permission_denied_for_admin_update(self):
        self._seed_demo_users()
        read_only_token = self._login_access_token("demo.internal_auditor@sfpcl.example")
        target = User.objects.get(email=ZERO_EMAIL)

        response = self.client.post(
            f"/api/v1/admin/users/{target.user_id}/roles/",
            data={"role_code": "credit_manager"},
            content_type="application/json",
            headers={"Authorization": f"Bearer {read_only_token}"},
        )

        self.assertEqual(response.status_code, 403, response.content)
        assert_error_envelope(self, response.json(), "PERMISSION_DENIED")
        target.refresh_from_db()
        self.assertEqual(target.primary_role.role_code, "management_viewer")
