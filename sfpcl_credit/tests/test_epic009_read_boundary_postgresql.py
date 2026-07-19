"""Six-test PostgreSQL acceptance for the converged Epic 009 read boundary."""

from unittest import skipUnless

from django.db import connection
from django.test import Client, TestCase

from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest
from sfpcl_credit.tests import test_disbursement_workspace_api as workspace_tests
from sfpcl_credit.tests import test_loan_account_reads_api as account_tests
from sfpcl_credit.tests import test_epic009_exact_selector_postgresql as exact_tests


@skipUnless(
    connection.vendor == "postgresql",
    "Exact SHA-256 selector acceptance requires PostgreSQL.",
)
class Epic009ReadBoundaryPostgreSQLAcceptanceTests(TestCase):
    test_loan_account_selector_excludes_non_array_creation_team_evidence = (
        exact_tests.Epic009ExactSelectorPostgreSQLAcceptanceTests.
        test_loan_account_selector_excludes_non_array_creation_team_evidence
    )
    test_s37_selector_excludes_send_body_key_drift = (
        exact_tests.Epic009ExactSelectorPostgreSQLAcceptanceTests.
        test_s37_selector_excludes_send_body_key_drift
    )
    test_combined_senior_finance_selector_projects_its_exact_count = (
        exact_tests.Epic009ExactSelectorPostgreSQLAcceptanceTests.
        test_combined_senior_finance_selector_projects_its_exact_count
    )
    test_cfc_selector_executes_sha256_and_excludes_comment_drift = (
        exact_tests.Epic009ExactSelectorPostgreSQLAcceptanceTests.
        test_cfc_selector_executes_sha256_and_excludes_comment_drift
    )

    def test_transfer_file_owner_is_excluded_before_count_and_detail(self):
        fixture = account_tests.ActiveLoanAccountReadApiTests(
            "test_exact_transfer_projects_active_funded_amounts_and_activation_time"
        )
        fixture.setUp()
        fixture.fixture.evidence.checksum_sha256 = "0" * 64
        fixture.fixture.evidence.save(update_fields=["checksum_sha256"])

        response = Client().get("/api/v1/loan-accounts/", **fixture.auth)
        detail = Client().get(
            f"/api/v1/loan-accounts/{fixture.account.pk}/", **fixture.auth
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])
        self.assertEqual(detail.status_code, 404, detail.content)

    def test_s37_file_digest_owner_is_excluded_before_count(self):
        fixture = workspace_tests.SapStaffWorkspaceApiTests(
            "test_exact_assignee_gets_optional_s37_completion_action"
        )
        fixture.setUp()
        request_id = fixture.fixture._create_and_send("postgresql-s37-file-drift")
        request = SapCustomerProfileRequest.objects.select_related("excel_file").get(
            pk=request_id
        )
        request.excel_file.checksum_sha256 = "0" * 64
        request.excel_file.save(update_fields=["checksum_sha256"])

        response = Client().get(
            "/api/v1/disbursement-workspaces/",
            **fixture.fixture._auth(fixture.fixture.assignee),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])
