"""Review-only probes for the retained 009L6 selector-equivalence contract."""

from django.test import Client, TestCase

from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest
from sfpcl_credit.tests import test_disbursement_workspace_api as workspace_tests
from sfpcl_credit.tests import test_loan_account_reads_api as account_tests


class Epic009L6ClosureReviewProbes(TestCase):
    def test_initiation_authority_does_not_replace_public_account_read_permission(self):
        fixture = workspace_tests.DisbursementWorkspaceApiTests(
            "test_admitted_senior_finance_reader_does_not_hit_internal_permission"
        )
        fixture.setUp()
        initiator = fixture.fixture.fixture.actor

        response = Client().get(
            "/api/v1/loan-accounts/",
            **fixture.fixture.fixture._auth(initiator),
        )

        self.assertEqual(response.status_code, 403, response.content)
        self.assertEqual(response.json()["error"]["code"], "FORBIDDEN")

    def test_completed_account_send_ledger_drift_is_excluded_before_count(self):
        fixture = account_tests.ActiveLoanAccountReadApiTests(
            "test_completion_digest_drift_affects_neither_total_nor_page"
        )
        fixture.setUp()
        request = SapCustomerProfileRequest.objects.select_related(
            "sent_communication"
        ).get(
            loan_application_id=fixture.account.loan_application_id,
            request_status=SapCustomerProfileRequest.STATUS_COMPLETED,
        )
        request.sent_communication.body_snapshot = "Drifted after SAP completion."
        request.sent_communication.save(update_fields=["body_snapshot"])

        response = Client().get("/api/v1/loan-accounts/", **fixture.auth)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            (
                response.json()["pagination"]["total_count"],
                response.json()["data"],
            ),
            (0, []),
        )

    def test_s37_file_integrity_drift_is_excluded_before_count(self):
        fixture = workspace_tests.SapStaffWorkspaceApiTests(
            "test_exact_assignee_gets_optional_s37_completion_action"
        )
        fixture.setUp()
        request_id = fixture.fixture._create_and_send("review-s37-file-drift")
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
        self.assertEqual(
            (
                response.json()["pagination"]["total_count"],
                response.json()["data"],
            ),
            (0, []),
        )
