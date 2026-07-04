from django.test import Client, TestCase

from sfpcl_credit.identity.models import Permission, Role, RolePermission, User
from sfpcl_credit.tests.api_contracts import (
    assert_available_actions_shape,
    assert_error_envelope,
    assert_pagination_shape,
    assert_success_envelope,
)
from sfpcl_credit.tests.base import IdentityTestCase


class ApiContractHarnessUnitTests(TestCase):
    def test_success_envelope_reports_missing_meta_field(self):
        incomplete_payload = {
            "success": True,
            "data": {},
            "meta": {"request_id": "req-contract", "api_version": "v1"},
        }

        with self.assertRaisesRegex(AssertionError, "meta.timestamp"):
            assert_success_envelope(self, incomplete_payload)

    def test_available_actions_shape_reports_missing_item_field(self):
        with self.assertRaisesRegex(
            AssertionError,
            "available_actions\\[0\\].required_permission",
        ):
            assert_available_actions_shape(
                self,
                [
                    {
                        "action_code": "submit",
                        "label": "Submit Application",
                        "enabled": True,
                        "disabled_reason": None,
                    }
                ],
            )

    def test_available_actions_shape_accepts_target_contract_sample(self):
        assert_available_actions_shape(
            self,
            [
                {
                    "action_code": "submit",
                    "label": "Submit Application",
                    "enabled": False,
                    "disabled_reason": "Nominee Aadhaar document is missing.",
                    "required_permission": "loan_application.submit",
                },
                {
                    "action_code": "return_with_deficiencies",
                    "label": "Return with Deficiencies",
                    "enabled": True,
                    "disabled_reason": None,
                    "required_permission": "loan_application.return_deficiency",
                },
            ],
        )


class ApiContractEndpointRegressionTests(IdentityTestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()
        self.system_admin_role = Role.objects.create(
            role_code="system_admin",
            role_name="System Administrator",
            is_system_role=True,
            status="active",
        )
        self.accounts_role = Role.objects.create(
            role_code="accounts_head",
            role_name="Accounts Head",
            is_system_role=True,
            status="active",
        )
        self._create_user(
            full_name="System Admin",
            email="system.admin.contract@sfpcl.example",
            role=self.system_admin_role,
            password="AdminPass123!",
        )
        self.target = self._create_user(
            full_name="Target User",
            email="target.contract@sfpcl.example",
            role=self.role,
            password="TargetPass123!",
        )
        self._grant_permissions(
            self.system_admin_role,
            [
                "users.user.create",
                "users.user.update",
                "users.user.disable",
                "tracer.lifecycle.run",
            ],
        )
        self._grant_permissions(self.role, ["tracer.lifecycle.run"])

    def _create_user(self, full_name, email, role, password):
        user = User.objects.create(
            full_name=full_name,
            email=email,
            mobile_number="+917111111111",
            status="active",
            primary_role=role,
        )
        user.set_password(password)
        user.save()
        return user

    def _grant_permissions(self, role, permission_codes):
        for code in permission_codes:
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": code.split(".", 1)[0],
                    "risk_level": "high",
                },
            )
            RolePermission.objects.get_or_create(role=role, permission=permission)

    def _access_token(self, email, password):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": email, "password": password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        return data["access_token"], data["refresh_token"]

    def _admin_headers(self):
        access_token, _refresh_token = self._access_token(
            "system.admin.contract@sfpcl.example", "AdminPass123!"
        )
        return {"Authorization": f"Bearer {access_token}"}

    def _partial_admin_headers(self, role_code, permission_codes):
        role = Role.objects.create(
            role_code=role_code,
            role_name=role_code.replace("_", " ").title(),
            is_system_role=True,
            status="active",
        )
        self._grant_permissions(role, permission_codes)
        email = f"{role_code}@contract.sfpcl.example"
        self._create_user(
            full_name=role_code.replace("_", " ").title(),
            email=email,
            role=role,
            password="PartialPass123!",
        )
        access_token, _refresh_token = self._access_token(email, "PartialPass123!")
        return {"Authorization": f"Bearer {access_token}"}

    def test_auth_me_success_satisfies_success_envelope_contract(self):
        access_token, _refresh_token = self._access_token(
            "credit.manager@sfpcl.example", "CorrectHorse123!"
        )

        response = self.client.get(
            "/api/v1/auth/me/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Request-ID": "req-auth-me-contract",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_success_envelope(self, payload)
        self.assertEqual(payload["meta"]["request_id"], "req-auth-me-contract")
        self.assertIsInstance(payload["data"]["available_actions"], list)

    def test_protected_endpoint_unauthenticated_satisfies_auth_required_contract(self):
        response = self.client.get("/api/v1/admin/users/")

        self.assertEqual(response.status_code, 401)
        assert_error_envelope(self, response.json(), expected_code="AUTH_REQUIRED")

    def test_revoked_access_token_satisfies_invalid_token_contract(self):
        access_token, refresh_token = self._access_token(
            "credit.manager@sfpcl.example", "CorrectHorse123!"
        )
        logout = self.client.post(
            "/api/v1/auth/logout/",
            data={"refresh_token": refresh_token},
            content_type="application/json",
        )
        self.assertEqual(logout.status_code, 200)

        response = self.client.get(
            "/api/v1/auth/me/",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        self.assertEqual(response.status_code, 401)
        assert_error_envelope(self, response.json(), expected_code="INVALID_TOKEN")

    def test_admin_users_without_permission_satisfies_permission_denied_contract(self):
        access_token, _refresh_token = self._access_token(
            "credit.manager@sfpcl.example", "CorrectHorse123!"
        )

        response = self.client.get(
            "/api/v1/admin/users/",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        self.assertEqual(response.status_code, 403)
        assert_error_envelope(self, response.json(), expected_code="PERMISSION_DENIED")

    def test_partial_admin_denied_write_satisfies_permission_denied_contract(self):
        headers = self._partial_admin_headers(
            "contract_user_creator",
            ["users.user.create"],
        )

        response = self.client.post(
            f"/api/v1/admin/users/{self.target.user_id}/roles/",
            data={"role_code": "accounts_head"},
            content_type="application/json",
            headers=headers,
        )

        self.assertEqual(response.status_code, 403)
        assert_error_envelope(self, response.json(), expected_code="PERMISSION_DENIED")

    def test_tracer_invalid_state_satisfies_state_transition_contract(self):
        headers = self._admin_headers()
        member = self.client.post(
            "/api/v1/tracer/members/",
            data={"display_name": "Contract Member"},
            content_type="application/json",
            headers=headers,
        ).json()["data"]
        application = self.client.post(
            f"/api/v1/tracer/members/{member['member_id']}/loan-applications/",
            data={"amount": "100000.00"},
            content_type="application/json",
            headers=headers,
        ).json()["data"]

        response = self.client.post(
            f"/api/v1/tracer/loan-applications/{application['loan_application_id']}/loan-account/",
            data={},
            content_type="application/json",
            headers=headers,
        )

        self.assertEqual(response.status_code, 409)
        assert_error_envelope(
            self,
            response.json(),
            expected_code="INVALID_STATE_TRANSITION",
        )

    def test_admin_users_list_satisfies_pagination_contract(self):
        response = self.client.get(
            "/api/v1/admin/users/?page=1&page_size=20",
            headers=self._admin_headers(),
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_pagination_shape(self, payload)
        self.assertIsInstance(payload["data"], list)
