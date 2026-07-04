from django.core.management import call_command
from django.test import Client, TestCase

from sfpcl_credit.identity.models import Permission, RolePermission, User


TRACER_PERMISSION = "tracer.lifecycle.run"
TRACER_EMAIL = "e2e.tracer@sfpcl.example"
ZERO_EMAIL = "e2e.zero@sfpcl.example"
E2E_PASSWORD = "E2eTracer123!"


class SeedE2eUsersTests(TestCase):
    """The Playwright suite needs deterministic staff users created by backend
    dev/test setup (slice 002EY req 8, 9, 14), not by frontend fixtures."""

    def _login_access_token(self, email):
        client = Client()
        response = client.post(
            "/api/v1/auth/login/",
            data={"email": email, "password": E2E_PASSWORD},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return client, response.json()["data"]["access_token"]

    def test_seed_creates_active_tracer_staff_with_single_tracer_permission(self):
        call_command("seed_e2e_users")

        tracer_user = User.objects.get(email=TRACER_EMAIL)
        self.assertEqual(tracer_user.status, "active")
        self.assertTrue(tracer_user.check_password(E2E_PASSWORD))
        self.assertEqual(tracer_user.primary_role.status, "active")

        permission_codes = list(
            Permission.objects.filter(
                role_permissions__role=tracer_user.primary_role
            ).values_list("permission_code", flat=True)
        )
        self.assertEqual(permission_codes, [TRACER_PERMISSION])

    def test_seed_creates_zero_permission_staff(self):
        call_command("seed_e2e_users")

        zero_user = User.objects.get(email=ZERO_EMAIL)
        self.assertEqual(zero_user.status, "active")
        self.assertEqual(zero_user.primary_role.role_code, "it_head")
        self.assertFalse(
            RolePermission.objects.filter(role=zero_user.primary_role).exists()
        )

    def test_seed_is_idempotent(self):
        call_command("seed_e2e_users")
        call_command("seed_e2e_users")

        self.assertEqual(User.objects.filter(email=TRACER_EMAIL).count(), 1)
        self.assertEqual(User.objects.filter(email=ZERO_EMAIL).count(), 1)
        self.assertEqual(
            RolePermission.objects.filter(
                role__role_code="e2e_tracer",
                permission__permission_code=TRACER_PERMISSION,
            ).count(),
            1,
        )

    def test_me_exposes_exactly_the_tracer_permission_for_the_tracer_user(self):
        call_command("seed_e2e_users")
        client, access_token = self._login_access_token(TRACER_EMAIL)

        response = client.get(
            "/api/v1/auth/me/",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["permissions"], [TRACER_PERMISSION])
        self.assertEqual(data["available_actions"], [TRACER_PERMISSION])

    def test_me_exposes_no_permissions_for_the_zero_permission_user(self):
        call_command("seed_e2e_users")
        client, access_token = self._login_access_token(ZERO_EMAIL)

        response = client.get(
            "/api/v1/auth/me/",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["permissions"], [])
        self.assertEqual(data["available_actions"], [])
