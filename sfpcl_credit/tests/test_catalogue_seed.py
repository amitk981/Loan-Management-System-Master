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
    def test_seed_creates_standard_role_and_team_codes(self):
        seed_catalogue()

        seeded_roles = set(Role.objects.values_list("role_code", flat=True))
        for role_code in STANDARD_INTERNAL_ROLE_CODES:
            self.assertIn(role_code, seeded_roles)

        seeded_teams = set(Team.objects.values_list("team_code", flat=True))
        self.assertEqual(seeded_teams, set(TEAM_CODES))

        # External / future roles are seeded but inactive / non-MVP (slice req 4).
        borrower = Role.objects.get(role_code="borrower_portal_user")
        self.assertEqual(borrower.status, "inactive")
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
