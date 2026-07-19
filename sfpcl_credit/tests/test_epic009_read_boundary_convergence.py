"""Public regressions for the converged Epic 009 read boundary."""

import inspect

from django.test import Client, TestCase

from sfpcl_credit.identity.management.commands import seed_epic_009_e2e_fixture
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest
from sfpcl_credit.tests import test_disbursement_workspace_api as workspace_tests
from sfpcl_credit.tests import test_loan_account_reads_api as account_tests


class Epic009ReadBoundaryConvergenceTests(TestCase):
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
            (response.json()["pagination"]["total_count"], response.json()["data"]),
            (0, []),
        )

    def test_completed_account_send_audit_drift_is_excluded_before_count(self):
        fixture = account_tests.ActiveLoanAccountReadApiTests(
            "test_completion_digest_drift_affects_neither_total_nor_page"
        )
        fixture.setUp()
        request = SapCustomerProfileRequest.objects.get(
            loan_application_id=fixture.account.loan_application_id,
            request_status=SapCustomerProfileRequest.STATUS_COMPLETED,
        )
        audit = AuditLog.objects.get(
            entity_type="sap_customer_profile_request",
            entity_id=request.pk,
            action="finance.sap_customer_code.sent",
        )
        audit.new_value_json = {**audit.new_value_json, "review_drift": True}
        audit.save(update_fields=["new_value_json"])

        response = Client().get("/api/v1/loan-accounts/", **fixture.auth)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            (response.json()["pagination"]["total_count"], response.json()["data"]),
            (0, []),
        )

    def test_s37_file_integrity_drift_is_excluded_before_count(self):
        fixture = workspace_tests.SapStaffWorkspaceApiTests(
            "test_exact_assignee_gets_optional_s37_completion_action"
        )
        fixture.setUp()
        request_id = fixture.fixture._create_and_send("read-boundary-file-drift")
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
            (response.json()["pagination"]["total_count"], response.json()["data"]),
            (0, []),
        )

    def test_cfc_mutable_bank_and_account_owners_are_excluded_before_count(self):
        fixture = workspace_tests.DisbursementWorkspaceApiTests(
            "test_cfc_queue_is_masked_paginated_and_projects_server_owned_actions"
        )
        fixture.setUp()
        cases = (
            (fixture.row.borrower_bank_account, "status", "inactive"),
            (fixture.row.source_bank_account, "status", "inactive"),
            (fixture.row.loan_account, "sanctioned_amount", "399999.00"),
        )

        for row, field, changed in cases:
            with self.subTest(owner=type(row).__name__, field=field):
                original = getattr(row, field)
                type(row).objects.filter(pk=row.pk).update(**{field: changed})
                response = Client().get(
                    "/api/v1/disbursement-workspaces/",
                    **fixture.fixture.fixture._auth(fixture.fixture.cfc),
                )
                self.assertEqual(response.status_code, 200, response.content)
                self.assertEqual(
                    (
                        response.json()["pagination"]["total_count"],
                        response.json()["data"],
                    ),
                    (0, []),
                )
                type(row).objects.filter(pk=row.pk).update(**{field: original})

    def test_runtime_epic009_seed_uses_no_testcase_or_private_test_helpers(self):
        source = inspect.getsource(seed_epic_009_e2e_fixture)

        self.assertNotIn("sfpcl_credit.tests", source)
        self.assertNotIn(".setUp()", source)
        self.assertNotIn("._real_owner_initiation_fixture", source)
