from django.db import connection
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.identity.models import (
    AuditLog,
    Permission,
    Role,
    RolePermission,
    Team,
    User,
    UserTeamMembership,
)
from sfpcl_credit.members.models import Member
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
        for permission_code in (
            "applications.loan_application.read",
            "credit.appraisal.review",
            "finance.loan_account.read",
            "monitoring.dpd.read",
            "monitoring.reminder.create",
            "defaults.case.read",
        ):
            self._grant_permission(
                self.credit_manager.primary_role,
                permission_code,
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

    def _grant_permission(self, role, permission_code):
        permission, _created = Permission.objects.get_or_create(
            permission_code=permission_code,
            defaults={
                "permission_name": permission_code,
                "module_name": permission_code.split(".", 1)[0],
                "risk_level": "medium",
            },
        )
        RolePermission.objects.get_or_create(role=role, permission=permission)

    def _join_team(self, user, team_code):
        team, _created = Team.objects.get_or_create(
            team_code=team_code,
            defaults={"team_name": team_code.replace("_", " ").title()},
        )
        UserTeamMembership.objects.get_or_create(user=user, team=team)

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

    def test_credit_manager_receives_source_named_empty_cards(self):
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
            "/applications?status=submitted&current_stage=initial_loan_request",
        )
        self.assertEqual(cards["appraisals_due_today"]["count"], 0)
        self.assertEqual(cards["loans_outstanding_beyond_one_year"]["count"], 0)
        for card in cards.values():
            self.assertEqual(set(card), {"code", "label", "count", "link"})

        serialized = str(payload["data"])
        self.assertNotIn("borrower", serialized.lower())
        self.assertNotIn("member", serialized.lower())
        self.assertNotIn("loan_account_number", serialized.lower())

    def test_credit_manager_pending_completeness_card_reconciles_to_scoped_application_list(self):
        member = Member.objects.create(
            member_number="MEM-DASH-001",
            member_type="individual_farmer",
            legal_name="Dashboard Test Member",
            display_name="Dashboard Test Member",
            folio_number="FOL-DASH-001",
            membership_status="active",
            pan_encrypted="test-only-encrypted-pan",
            pan_hash="dashboard-test-pan-hash",
            kyc_status="verified",
            default_status="no_default",
            created_by_user=self.credit_manager,
        )
        LoanApplication.objects.create(
            member=member,
            borrower_type=member.member_type,
            received_by_user=self.credit_manager,
            created_by_user=self.credit_manager,
            application_status=LoanApplication.STATUS_SUBMITTED,
            current_stage=LoanApplication.STAGE_INITIAL,
            completeness_status=LoanApplication.COMPLETENESS_NOT_STARTED,
            submitted_at=timezone.now(),
            submitted_by_user=self.credit_manager,
        )
        other_member = Member.objects.create(
            member_number="MEM-DASH-OTHER",
            member_type="individual_farmer",
            legal_name="Other Dashboard Member",
            display_name="Other Dashboard Member",
            folio_number="FOL-DASH-OTHER",
            membership_status="active",
            pan_encrypted="test-only-other-encrypted-pan",
            pan_hash="dashboard-other-pan-hash",
            kyc_status="verified",
            default_status="no_default",
            created_by_user=self.plain_user,
        )
        LoanApplication.objects.create(
            member=other_member,
            borrower_type=other_member.member_type,
            received_by_user=self.plain_user,
            created_by_user=self.plain_user,
            application_status=LoanApplication.STATUS_SUBMITTED,
            current_stage=LoanApplication.STAGE_INITIAL,
            completeness_status=LoanApplication.COMPLETENESS_NOT_STARTED,
            submitted_at=timezone.now(),
            submitted_by_user=self.plain_user,
        )

        response = self.client.get(DASHBOARD_URL, headers=self._auth_headers())

        self.assertEqual(response.status_code, 200)
        cards = {
            card["code"]: card
            for card in response.json()["data"]["cards"]
        }
        self.assertEqual(
            cards["applications_pending_completeness"],
            {
                "code": "applications_pending_completeness",
                "label": "Applications pending completeness",
                "count": 1,
                "link": (
                    "/applications?status=submitted"
                    "&current_stage=initial_loan_request"
                ),
            },
        )
        target = self.client.get(
            (
                "/api/v1/loan-applications/?status=submitted"
                "&current_stage=initial_loan_request"
            ),
            headers=self._auth_headers(),
        )
        self.assertEqual(target.status_code, 200)
        self.assertEqual(
            target.json()["pagination"]["total_count"],
            cards["applications_pending_completeness"]["count"],
        )

    def test_specialist_role_contexts_return_source_named_shell_cards(self):
        contexts = [
            (
                "cfo",
                "CFO",
                "cfo.dashboard@sfpcl.example",
                "CfoPass123!",
                "sanction_committee",
                {"cases_pending_review", "exceptions_pending_decision"},
                {"approvals.case.read", "approvals.exception_register.read"},
            ),
            (
                "compliance_team_member",
                "Compliance Team Member",
                "compliance.dashboard@sfpcl.example",
                "CompliancePass123!",
                "compliance",
                {"documents_pending_generation", "compliance_tasks_due"},
                {"documents.checklist.read", "compliance.task.read"},
            ),
            (
                "senior_manager_finance",
                "Senior Manager Finance",
                "treasury.dashboard@sfpcl.example",
                "TreasuryPass123!",
                "treasury",
                {"sap_requests_pending", "disbursements_pending_authorisation"},
                {
                    "finance.sap_code.read",
                    "finance.disbursement.readiness",
                    "finance.loan_account.read",
                },
            ),
        ]
        for (
            role_code,
            role_name,
            email,
            password,
            expected_context,
            expected_codes,
            permission_codes,
        ) in contexts:
            with self.subTest(role_context=expected_context):
                user = self._user_with_role(
                    role_code=role_code,
                    role_name=role_name,
                    email=email,
                    password=password,
                    grant_dashboard=True,
                )
                for permission_code in permission_codes:
                    self._grant_permission(user.primary_role, permission_code)
                if role_code == "company_secretary":
                    self._join_team(user, "compliance")

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

    def test_dedicated_dashboard_route_derives_context_and_denies_cross_role_access(self):
        compliance_user = self._user_with_role(
            role_code="compliance_team_member",
            role_name="Compliance Team Member",
            email="dedicated.compliance@sfpcl.example",
            password="CompliancePass123!",
        )

        allowed = self.client.get(
            "/api/v1/dashboard/compliance/",
            headers=self._auth_headers(
                email=compliance_user.email,
                password="CompliancePass123!",
            ),
        )
        denied = self.client.get(
            "/api/v1/dashboard/treasury/",
            headers=self._auth_headers(
                email=compliance_user.email,
                password="CompliancePass123!",
            ),
        )

        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(allowed.json()["data"]["role_context"], "compliance")
        self.assertEqual(denied.status_code, 403)
        assert_error_envelope(self, denied.json(), "PERMISSION_DENIED")

    def test_cards_without_their_owner_read_permission_are_omitted_not_faked_as_zero(self):
        cfo = self._user_with_role(
            role_code="cfo",
            role_name="CFO Without Owner Permissions",
            email="unscoped.cfo@sfpcl.example",
            password="UnscopedCfoPass123!",
        )

        response = self.client.get(
            DASHBOARD_URL,
            headers=self._auth_headers(cfo.email, "UnscopedCfoPass123!"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["cards"], [])

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
        self.assertIn("compliance_tasks_due", card_codes)
        self.assertIn("section186_items_pending", card_codes)

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

    def test_primary_role_resolves_multi_role_dashboard_without_caller_override(self):
        Role.objects.create(
            role_code="cfo",
            role_name="CFO",
            is_system_role=True,
            status="active",
        )
        self.credit_manager.approval_authority_type = "cfo"
        self.credit_manager.save(update_fields=["approval_authority_type"])

        response = self.client.get(DASHBOARD_URL, headers=self._auth_headers())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["role_context"], "credit_manager")

    def test_supported_permission_does_not_turn_unknown_role_into_management_dashboard(self):
        unknown = self._user_with_role(
            role_code="unmapped_staff",
            role_name="Unmapped Staff",
            email="unmapped.dashboard@sfpcl.example",
            password="UnmappedPass123!",
        )

        response = self.client.get(
            DASHBOARD_URL,
            headers=self._auth_headers(
                email=unknown.email,
                password="UnmappedPass123!",
            ),
        )

        self.assertEqual(response.status_code, 403)
        assert_error_envelope(self, response.json(), "PERMISSION_DENIED")

    def test_management_viewer_context_returns_an_empty_permission_safe_shell(self):
        viewer = self._user_with_role(
            role_code="management_viewer",
            role_name="Management Viewer",
            email="management.dashboard@sfpcl.example",
            password="ManagementPass123!",
        )

        response = self.client.get(
            DASHBOARD_URL,
            headers=self._auth_headers(viewer.email, "ManagementPass123!"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["role_context"], "management")
        self.assertEqual(response.json()["data"]["cards"], [])
        self.assertEqual(response.json()["data"]["tasks"], [])

    def test_accounts_and_company_secretary_receive_role_specific_source_cards(self):
        role_expectations = [
            (
                "accounts_head",
                "Accounts Head",
                "accounts.dashboard@sfpcl.example",
                "AccountsPass123!",
                {
                    "repayments_pending_posting",
                    "interest_invoices_pending",
                    "accruals_pending",
                    "reconciliation_breaks",
                },
                {
                    "finance.loan_account.read",
                    "finance.bank_statement.read",
                },
            ),
            (
                "company_secretary",
                "Company Secretary",
                "cs.dashboard@sfpcl.example",
                "CompanySecretaryPass123!",
                {
                    "compliance_tasks_due",
                    "board_approvals_required",
                    "grievance_open_cases",
                    "archival_due",
                },
                {
                    "documents.checklist.read",
                    "security.package.read",
                    "compliance.task.read",
                    "approvals.case.read",
                    "compliance.grievance.read",
                    "closure.archive.read",
                },
            ),
        ]
        for (
            role_code,
            role_name,
            email,
            password,
            expected_codes,
            permission_codes,
        ) in role_expectations:
            with self.subTest(role_code=role_code):
                user = self._user_with_role(
                    role_code=role_code,
                    role_name=role_name,
                    email=email,
                    password=password,
                )
                for permission_code in permission_codes:
                    self._grant_permission(user.primary_role, permission_code)
                if role_code == "company_secretary":
                    self._join_team(user, "compliance")

                response = self.client.get(
                    DASHBOARD_URL,
                    headers=self._auth_headers(email=user.email, password=password),
                )

                self.assertEqual(response.status_code, 200)
                self.assertTrue(
                    expected_codes.issubset(
                        {
                            card["code"]
                            for card in response.json()["data"]["cards"]
                        }
                    )
                )

    def test_dashboard_read_does_not_create_audit_row(self):
        headers = self._auth_headers()
        before = AuditLog.objects.count()

        response = self.client.get(DASHBOARD_URL, headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(AuditLog.objects.count(), before)

    def test_credit_dashboard_batches_card_counts_within_fixed_query_budget(self):
        headers = self._auth_headers()

        with CaptureQueriesContext(connection) as captured:
            response = self.client.get(DASHBOARD_URL, headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(
            len(captured),
            11,
            "Dashboard query count includes one bounded workflow-task query and must not grow per card.",
        )

    def test_each_supported_role_uses_a_bounded_dashboard_query_budget(self):
        cases = [
            (
                "cfo",
                {
                    "approvals.case.read",
                    "approvals.exception_register.read",
                    "finance.loan_account.read",
                    "monitoring.dpd.read",
                    "compliance.section186.read",
                    "compliance.nbfc_test.read",
                    "defaults.case.read",
                },
            ),
            (
                "compliance_team_member",
                {
                    "documents.checklist.read",
                    "security.package.read",
                    "compliance.task.read",
                },
            ),
            (
                "senior_manager_finance",
                {
                    "finance.sap_code.read",
                    "finance.disbursement.readiness",
                    "finance.loan_account.read",
                },
            ),
            (
                "accounts_head",
                {
                    "finance.loan_account.read",
                    "finance.bank_statement.read",
                },
            ),
            (
                "company_secretary",
                {
                    "documents.checklist.read",
                    "security.package.read",
                    "compliance.task.read",
                    "approvals.case.read",
                    "compliance.grievance.read",
                    "closure.archive.read",
                },
            ),
        ]
        for index, (role_code, permission_codes) in enumerate(cases):
            with self.subTest(role_code=role_code):
                password = f"DashboardBudgetPass{index}!"
                user = self._user_with_role(
                    role_code=role_code,
                    role_name=role_code.replace("_", " ").title(),
                    email=f"budget.{role_code}@sfpcl.example",
                    password=password,
                )
                for permission_code in permission_codes:
                    self._grant_permission(user.primary_role, permission_code)
                if role_code == "company_secretary":
                    self._join_team(user, "compliance")
                headers = self._auth_headers(user.email, password)

                with CaptureQueriesContext(connection) as captured:
                    response = self.client.get(DASHBOARD_URL, headers=headers)

                self.assertEqual(response.status_code, 200)
                self.assertLessEqual(
                    len(captured),
                    25,
                    (
                        f"{role_code} dashboard exceeded the fixed cross-domain "
                        "selector budget."
                    ),
                )
