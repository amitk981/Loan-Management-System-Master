from django.apps import apps
from django.core.management import call_command
from django.test import TestCase

from sfpcl_credit.identity.catalogue import (
    PERMISSIONS,
    PROTOTYPE_PERMISSION_ALIASES,
    ROLE_PERMISSIONS,
    ROLES,
    TEAMS,
    seed_catalogue,
)
from sfpcl_credit.identity.models import (
    Permission,
    Role,
    RolePermission,
    Team,
)


STANDARD_INTERNAL_ROLE_CODES = [
    "field_officer",
    "deputy_manager_finance",
    "credit_manager",
    "compliance_team_member",
    "company_secretary",
    "senior_manager_finance",
    "chief_financial_controller",
    "cfo",
    "director",
    "accounts_head",
    "sales_team_user",
    "it_head",
    "internal_auditor",
    "system_admin",
    "management_viewer",
]

TEAM_CODES = [
    "credit_assessment",
    "compliance",
    "treasury",
    "sanction_committee",
    "accounts",
    "it",
    "audit",
    "sales",
]

# One representative permission code per digest module group (auth-permissions §12.1-12.13).
REPRESENTATIVE_PERMISSIONS_BY_GROUP = {
    "auth/user-admin": "users.user.create",
    "members": "members.member.read",
    "kyc": "kyc.profile.read",
    "applications": "applications.loan_application.submit",
    "credit": "credit.loan_limit.calculate",
    "approvals": "approvals.case.approve",
    "documentation": "documents.loan_document.verify",
    "security": "security.blank_cheque.manage",
    "sap/finance": "finance.disbursement.authorise",
    "monitoring/default": "defaults.case.open",
    "closure": "closure.loan.close",
    "compliance": "compliance.nbfc_test.create",
    "reports/audit/config": "reports.export",
}


class CatalogueSeedTests(TestCase):
    def test_quarterly_mis_grants_separate_prepare_submit_review_and_export_roles(self):
        seed_catalogue()

        def codes(role_code):
            return set(
                RolePermission.objects.filter(role__role_code=role_code).values_list(
                    "permission__permission_code", flat=True
                )
            )

        self.assertTrue(
            {"monitoring.mis.generate", "monitoring.mis.submit", "reports.export"}
            <= codes("credit_manager")
        )
        self.assertTrue(
            {"monitoring.mis.review", "reports.export"} <= codes("cfo")
        )
        self.assertNotIn("monitoring.mis.review", codes("credit_manager"))
        self.assertNotIn("monitoring.mis.submit", codes("cfo"))

    def test_disbursement_advice_grant_matches_stage_five_role_matrix(self):
        seed_catalogue()
        permission_code = "finance.disbursement.send_advice"

        granted_roles = set(
            RolePermission.objects.filter(
                permission__permission_code=permission_code
            ).values_list("role__role_code", flat=True)
        )

        self.assertIn("credit_manager", granted_roles)
        self.assertIn("senior_manager_finance", granted_roles)
        self.assertNotIn("chief_financial_controller", granted_roles)

    def test_seed_creates_standard_role_and_team_codes(self):
        seed_catalogue()

        seeded_roles = set(Role.objects.values_list("role_code", flat=True))
        for role_code in STANDARD_INTERNAL_ROLE_CODES:
            self.assertIn(role_code, seeded_roles)

        seeded_teams = set(Team.objects.values_list("team_code", flat=True))
        self.assertEqual(seeded_teams, set(TEAM_CODES))

        # Borrower portal access is live; only the remaining future external
        # identities stay inactive / non-MVP.
        borrower = Role.objects.get(role_code="borrower_portal_user")
        self.assertEqual(borrower.status, "active")
        self.assertFalse(borrower.is_system_role)

    def test_seed_creates_representative_permission_per_module_group(self):
        seed_catalogue()

        codes = set(Permission.objects.values_list("permission_code", flat=True))
        for group, representative in REPRESENTATIVE_PERMISSIONS_BY_GROUP.items():
            self.assertIn(
                representative,
                codes,
                msg=f"missing representative permission for module group {group}",
            )

        def role_codes(role_code):
            return set(RolePermission.objects.filter(role__role_code=role_code).values_list(
                "permission__permission_code", flat=True
            ))

        creates = {"compliance.section186.create", "compliance.nbfc_test.create"}
        reads = {"compliance.section186.read", "compliance.nbfc_test.read"}
        self.assertTrue(creates | reads <= role_codes("cfo"))
        self.assertTrue(creates | reads <= role_codes("accounts_head"))
        self.assertTrue(reads <= role_codes("internal_auditor"))

        # Every declared catalogue permission is persisted with a module name and risk level.
        self.assertEqual(Permission.objects.count(), len(PERMISSIONS))
        for permission in Permission.objects.all():
            self.assertTrue(permission.module_name)
            self.assertIn(
                permission.risk_level, {"low", "medium", "high", "critical"}
            )

    def test_seed_is_idempotent(self):
        seed_catalogue()
        first = (
            Permission.objects.count(),
            Role.objects.count(),
            Team.objects.count(),
            RolePermission.objects.count(),
        )

        seed_catalogue()
        second = (
            Permission.objects.count(),
            Role.objects.count(),
            Team.objects.count(),
            RolePermission.objects.count(),
        )

        self.assertEqual(first, second)
        self.assertEqual(Permission.objects.count(), len(PERMISSIONS))
        self.assertEqual(Role.objects.count(), len(ROLES))
        self.assertEqual(Team.objects.count(), len(TEAMS))

    def test_management_command_runs_seed_idempotently(self):
        call_command("seed_role_catalogue")
        call_command("seed_role_catalogue")

        self.assertEqual(Permission.objects.count(), len(PERMISSIONS))
        self.assertEqual(Role.objects.count(), len(ROLES))

    def test_prototype_aliases_map_to_canonical_permissions(self):
        seed_catalogue()

        # A-005: prototype permission strings reconciled to canonical backend codes.
        self.assertEqual(
            set(PROTOTYPE_PERMISSION_ALIASES),
            {"export", "export_reports", "view_loans"},
        )
        for alias, canonical_code in PROTOTYPE_PERMISSION_ALIASES.items():
            self.assertTrue(
                Permission.objects.filter(permission_code=canonical_code).exists(),
                msg=f"alias {alias} maps to unknown canonical code {canonical_code}",
            )

    def test_content_template_permissions_are_seeded_for_compliance_owner(self):
        seed_catalogue()

        codes = set(Permission.objects.values_list("permission_code", flat=True))
        expected = {
            "communications.content_template.read",
            "communications.content_template.manage",
        }
        self.assertTrue(expected.issubset(codes))

        compliance_role = Role.objects.get(role_code="compliance_team_member")
        compliance_codes = set(
            RolePermission.objects.filter(role=compliance_role).values_list(
                "permission__permission_code", flat=True
            )
        )
        self.assertTrue(expected.issubset(compliance_codes))

    def test_communication_permissions_are_seeded_for_compliance_owner(self):
        seed_catalogue()

        codes = set(Permission.objects.values_list("permission_code", flat=True))
        expected = {
            "communications.communication.read",
            "communications.communication.send",
        }
        self.assertTrue(expected.issubset(codes))

        compliance_role = Role.objects.get(role_code="compliance_team_member")
        compliance_codes = set(
            RolePermission.objects.filter(role=compliance_role).values_list(
                "permission__permission_code", flat=True
            )
        )
        self.assertTrue(expected.issubset(compliance_codes))

    def test_deputy_manager_has_each_source_completeness_action_permission(self):
        seed_catalogue()

        deputy_manager = Role.objects.get(role_code="deputy_manager_finance")
        codes = set(
            RolePermission.objects.filter(role=deputy_manager).values_list(
                "permission__permission_code", flat=True
            )
        )
        self.assertTrue(
            {
                "applications.loan_application.complete_check",
                "applications.loan_application.return_deficiency",
                "applications.deficiency.resolve",
            }.issubset(codes)
        )

    def test_management_readonly_dashboard_scope_is_seeded_for_dashboard_roles(self):
        seed_catalogue()

        self.assertTrue(
            Permission.objects.filter(permission_code="management_readonly").exists()
        )
        role_codes = {
            "credit_manager",
            "cfo",
            "director",
            "compliance_team_member",
            "company_secretary",
            "senior_manager_finance",
            "chief_financial_controller",
            "accounts_head",
            "internal_auditor",
            "management_viewer",
        }
        for role_code in role_codes:
            with self.subTest(role_code=role_code):
                role = Role.objects.get(role_code=role_code)
                self.assertTrue(
                    RolePermission.objects.filter(
                        role=role,
                        permission__permission_code="management_readonly",
                    ).exists()
                )

    def test_source_sanction_package_readers_receive_case_read_permission(self):
        seed_catalogue()

        for role_code in {
            "credit_manager",
            "company_secretary",
            "internal_auditor",
        }:
            with self.subTest(role_code=role_code):
                self.assertTrue(
                    RolePermission.objects.filter(
                        role__role_code=role_code,
                        permission__permission_code="approvals.case.read",
                    ).exists()
                )

    def test_source_security_read_roles_receive_package_read_without_mutation(self):
        seed_catalogue()

        read_roles = {
            "credit_manager",
            "compliance_team_member",
            "company_secretary",
            "senior_manager_finance",
            "chief_financial_controller",
            "cfo",
            "director",
            "internal_auditor",
        }
        mutation_codes = {
            "security.package.create",
            "security.package.update",
            "security.poa.manage",
            "security.sh4.manage",
            "security.cdsl_pledge.manage",
            "security.blank_cheque.manage",
            "security.custody.record",
            "security.instrument.invoke",
            "security.instrument.release",
        }
        for role_code in read_roles:
            with self.subTest(role_code=role_code):
                codes = set(
                    RolePermission.objects.filter(
                        role__role_code=role_code
                    ).values_list("permission__permission_code", flat=True)
                )
                self.assertIn("security.package.read", codes)
                if role_code not in {"compliance_team_member", "company_secretary"}:
                    self.assertFalse(codes.intersection(mutation_codes))

    def test_exception_register_permissions_support_system_generation_and_source_readers(self):
        seed_catalogue()

        self.assertTrue(
            RolePermission.objects.filter(
                role__role_code="credit_manager",
                permission__permission_code="approvals.exception.create",
            ).exists()
        )
        for role_code in {"cfo", "director", "internal_auditor"}:
            with self.subTest(role_code=role_code):
                self.assertTrue(
                    RolePermission.objects.filter(
                        role__role_code=role_code,
                        permission__permission_code="approvals.exception_register.read",
                    ).exists()
                )

    def test_credit_sanction_register_is_seeded_for_committee_cs_and_auditor(self):
        seed_catalogue()

        for role_code in {"cfo", "director", "company_secretary", "internal_auditor"}:
            with self.subTest(role_code=role_code):
                self.assertTrue(
                    RolePermission.objects.filter(
                        role__role_code=role_code,
                        permission__permission_code="approvals.sanction_register.read",
                    ).exists()
                )

        for role_code in {"cfo", "director"}:
            with self.subTest(role_code=role_code):
                self.assertTrue(
                    RolePermission.objects.filter(
                        role__role_code=role_code,
                        permission__permission_code="approvals.sanction.read",
                    ).exists()
                )
        credit_manager = Role.objects.get(role_code="credit_manager")
        self.assertFalse(
            RolePermission.objects.filter(
                role=credit_manager,
                permission__permission_code__in={
                    "approvals.sanction.read",
                    "approvals.sanction_register.read",
                },
            ).exists()
        )

    def test_seed_creates_only_source_named_approval_case_read_scope_grants(self):
        seed_catalogue()

        grant_model = apps.get_model("approvals", "ApprovalCaseReadScopeGrant")
        self.assertEqual(
            set(grant_model.objects.values_list("role__role_code", "scope_type")),
            {
                ("company_secretary", "legal_readonly"),
                ("internal_auditor", "audit_readonly"),
            },
        )

    def test_every_dashboard_context_role_can_read_dashboard(self):
        # 003G2 regression: every role named in the dashboard role-context mapping
        # must hold the management_readonly scope the dashboard endpoint gates on,
        # otherwise the mapped role receives a 403 instead of its documented shell.
        from sfpcl_credit.dashboard.services import _ROLE_CONTEXTS

        seed_catalogue()

        for role_code in _ROLE_CONTEXTS:
            with self.subTest(role_code=role_code):
                role = Role.objects.get(role_code=role_code)
                self.assertTrue(
                    RolePermission.objects.filter(
                        role=role,
                        permission__permission_code="management_readonly",
                    ).exists(),
                    msg=(
                        f"{role_code} is mapped to a dashboard context but lacks "
                        "management_readonly, so /api/v1/dashboard/ would return 403"
                    ),
                )

    def test_role_permission_links_use_catalogue_and_seed_interface(self):
        # Links must be produced by the shared seed interface, not rebuilt in the test.
        seed_catalogue()

        catalogue_codes = set(Permission.objects.values_list("permission_code", flat=True))
        link_codes = set(
            RolePermission.objects.values_list("permission__permission_code", flat=True)
        )
        self.assertTrue(link_codes)
        # No link may reference a permission outside the seeded catalogue.
        self.assertTrue(link_codes.issubset(catalogue_codes))
        # Every declared role-permission code resolves to a real catalogue permission.
        for codes in ROLE_PERMISSIONS.values():
            for code in codes:
                self.assertIn(code, catalogue_codes)

        credit_manager = Role.objects.get(role_code="credit_manager")
        cm_codes = set(
            RolePermission.objects.filter(role=credit_manager).values_list(
                "permission__permission_code", flat=True
            )
        )
        expected_subset = {
            "credit.appraisal.review",
            "credit.appraisal.submit_sanction",
            "approvals.case.create",
            "closure.loan.close",
        }
        self.assertTrue(expected_subset.issubset(cm_codes))
