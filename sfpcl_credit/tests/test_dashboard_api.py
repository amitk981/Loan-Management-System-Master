from django.test import Client, TestCase

from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.tests.api_contracts import assert_error_envelope, assert_success_envelope


DASHBOARD_URL = "/api/v1/dashboard/"
DASHBOARD_READ_PERMISSION = "management_readonly"


class DashboardApiTests(TestCase):
    """003G: protected role-based dashboard summary shell."""

    def setUp(self):
        self.client = Client()
        self.dashboard_permission = Permission.objects.create(
            permission_code=DASHBOARD_READ_PERMISSION,
            permission_name="View dashboard summaries",
            module_name="dashboard",
            risk_level="medium",
        )
        self.credit_manager = self._user_with_role(
            role_code="credit_manager",
            role_name="Credit Manager",
            email="credit.dashboard@sfpcl.example",
            password="CreditPass123!",
            grant_dashboard=True,
        )
        self.plain_user = self._user_with_role(
            role_code="plain_staff",
            role_name="Plain Staff",
            email="plain.dashboard@sfpcl.example",
            password="PlainPass123!",
            grant_dashboard=False,
        )

    def _user_with_role(
        self, *, role_code, role_name, email, password, grant_dashboard=True
    ):
        role = Role.objects.create(
            role_code=role_code,
            role_name=role_name,
            is_system_role=True,
            status="active",
        )
        if grant_dashboard:
            RolePermission.objects.create(
                role=role, permission=self.dashboard_permission
            )
        user = User.objects.create(
            full_name=role_name,
            email=email,
            status="active",
            primary_role=role,
        )
        user.set_password(password)
        user.save()
        return user

    def _access_token(self, email, password):
        return self._login_tokens(email, password)["access_token"]

    def _login_tokens(self, email, password):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": email, "password": password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]

    def _auth_headers(self, email="credit.dashboard@sfpcl.example", password="CreditPass123!"):
        return {"Authorization": f"Bearer {self._access_token(email, password)}"}

    def test_credit_manager_receives_source_named_zero_count_shell(self):
        response = self.client.get(
            DASHBOARD_URL,
            headers={**self._auth_headers(), "X-Request-ID": "req-dashboard-credit"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_success_envelope(self, payload)
        self.assertEqual(payload["meta"]["request_id"], "req-dashboard-credit")
        self.assertEqual(payload["data"]["role_context"], "credit_manager")
        self.assertEqual(payload["data"]["tasks"], [])

        cards = {card["code"]: card for card in payload["data"]["cards"]}
        self.assertEqual(
            {
                "applications_pending_completeness",
                "deficiencies_pending_resolution",
                "appraisals_due_today",
                "appraisals_breaching_two_day_tat",
                "credit_manager_review_queue",
                "rejected_applications",
                "loans_outstanding_beyond_one_year",
                "dpd_buckets",
                "reminder_queue",
                "default_assessment_queue",
            },
            set(cards),
        )
        self.assertEqual(cards["applications_pending_completeness"]["count"], 0)
        self.assertEqual(
            cards["applications_pending_completeness"]["label"],
            "Applications pending completeness",
        )
        self.assertEqual(
            cards["applications_pending_completeness"]["link"],
            "/applications?status=pending_completeness",
        )
        self.assertEqual(cards["appraisals_due_today"]["count"], 0)
        self.assertEqual(cards["loans_outstanding_beyond_one_year"]["count"], 0)
        for card in cards.values():
            self.assertEqual(set(card), {"code", "label", "count", "link"})

        serialized = str(payload["data"])
        self.assertNotIn("borrower", serialized.lower())
        self.assertNotIn("member", serialized.lower())
        self.assertNotIn("loan_account_number", serialized.lower())

    def test_specialist_role_contexts_return_source_named_shell_cards(self):
        contexts = [
            (
                "cfo",
                "CFO",
                "cfo.dashboard@sfpcl.example",
                "CfoPass123!",
                "sanction_committee",
                {"cases_pending_review", "exceptions_pending_decision"},
            ),
            (
                "compliance_team_member",
                "Compliance Team Member",
                "compliance.dashboard@sfpcl.example",
                "CompliancePass123!",
                "compliance",
                {"documents_pending_generation", "compliance_tasks_due"},
            ),
            (
                "senior_manager_finance",
                "Senior Manager Finance",
                "treasury.dashboard@sfpcl.example",
                "TreasuryPass123!",
                "treasury",
                {"sap_requests_pending", "disbursements_pending_authorisation"},
            ),
            (
                "management_viewer",
                "Management Viewer",
                "management.dashboard@sfpcl.example",
                "ManagementPass123!",
                "management",
                {"portfolio_outstanding", "applications_pipeline"},
            ),
        ]
        for role_code, role_name, email, password, expected_context, expected_codes in contexts:
            with self.subTest(role_context=expected_context):
                self._user_with_role(
                    role_code=role_code,
                    role_name=role_name,
                    email=email,
                    password=password,
                    grant_dashboard=True,
                )

                response = self.client.get(
                    DASHBOARD_URL,
                    headers=self._auth_headers(email=email, password=password),
                )

                self.assertEqual(response.status_code, 200)
                payload = response.json()
                assert_success_envelope(self, payload)
                self.assertEqual(payload["data"]["role_context"], expected_context)
                self.assertEqual(payload["data"]["tasks"], [])
                cards = payload["data"]["cards"]
                self.assertTrue(expected_codes.issubset({card["code"] for card in cards}))
                self.assertTrue(all(card["count"] == 0 for card in cards))

    def test_seeded_internal_auditor_receives_compliance_shell(self):
        # 003G2 regression: the canonical catalogue seed must grant the
        # internal_auditor the management_readonly dashboard scope so the
        # documented internal_auditor -> "compliance" mapping is reachable
        # instead of returning 403.
        from sfpcl_credit.identity.catalogue import seed_catalogue

        seed_catalogue()
        auditor_role = Role.objects.get(role_code="internal_auditor")
        auditor = User.objects.create(
            full_name="Internal Auditor",
            email="auditor.dashboard@sfpcl.example",
            status="active",
            primary_role=auditor_role,
        )
        auditor.set_password("AuditorPass123!")
        auditor.save()

        response = self.client.get(
            DASHBOARD_URL,
            headers=self._auth_headers(
                email="auditor.dashboard@sfpcl.example", password="AuditorPass123!"
            ),
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_success_envelope(self, payload)
        self.assertEqual(payload["data"]["role_context"], "compliance")
        self.assertEqual(payload["data"]["tasks"], [])
        card_codes = {card["code"] for card in payload["data"]["cards"]}
        self.assertIn("documents_pending_generation", card_codes)
        self.assertIn("compliance_tasks_due", card_codes)

    def test_unauthenticated_request_returns_401(self):
        response = self.client.get(DASHBOARD_URL)

        self.assertEqual(response.status_code, 401)
        assert_error_envelope(self, response.json(), "AUTH_REQUIRED")

    def test_revoked_bearer_token_returns_401(self):
        tokens = self._login_tokens(
            "credit.dashboard@sfpcl.example", "CreditPass123!"
        )
        logout_response = self.client.post(
            "/api/v1/auth/logout/",
            data={"refresh_token": tokens["refresh_token"]},
            content_type="application/json",
        )
        self.assertEqual(logout_response.status_code, 200)

        response = self.client.get(
            DASHBOARD_URL,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )

        self.assertEqual(response.status_code, 401)
        assert_error_envelope(self, response.json(), "INVALID_TOKEN")

    def test_user_without_dashboard_permission_is_forbidden(self):
        response = self.client.get(
            DASHBOARD_URL,
            headers=self._auth_headers(
                email="plain.dashboard@sfpcl.example", password="PlainPass123!"
            ),
        )

        self.assertEqual(response.status_code, 403)
        assert_error_envelope(self, response.json(), "PERMISSION_DENIED")

    def test_unknown_query_parameter_returns_validation_error(self):
        response = self.client.get(
            f"{DASHBOARD_URL}?role_context=credit_manager",
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 400)
        payload = response.json()
        assert_error_envelope(self, payload, "VALIDATION_ERROR")
        self.assertEqual(
            payload["error"]["field_errors"],
            {"role_context": "Unknown query parameter."},
        )

    def test_dashboard_read_does_not_create_audit_row(self):
        headers = self._auth_headers()
        before = AuditLog.objects.count()

        response = self.client.get(DASHBOARD_URL, headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(AuditLog.objects.count(), before)
