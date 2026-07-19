"""Public regressions for the converged Epic 009 read boundary."""

import inspect
from importlib import import_module

from django.test import Client, TestCase

from sfpcl_credit.disbursements.modules.post_transfer_evidence import (
    resolve_post_transfer_evidence,
)
from sfpcl_credit.identity import epic009_e2e_fixture
from sfpcl_credit.identity.management.commands import seed_epic_009_e2e_fixture
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest
from sfpcl_credit.tests import test_disbursement_workspace_api as workspace_tests
from sfpcl_credit.tests import test_loan_account_reads_api as account_tests


class Epic009ReadBoundaryConvergenceTests(TestCase):
    def test_transfer_file_drift_hides_public_account_list_and_detail(self):
        fixture = account_tests.ActiveLoanAccountReadApiTests(
            "test_exact_transfer_projects_active_funded_amounts_and_activation_time"
        )
        fixture.setUp()
        evidence = fixture.fixture.evidence
        evidence.checksum_sha256 = "0" * 64
        evidence.save(update_fields=["checksum_sha256"])

        self.assertIsNone(
            resolve_post_transfer_evidence(
                application_id=fixture.account.loan_application_id
            )
        )

        listing = Client().get("/api/v1/loan-accounts/", **fixture.auth)
        detail = Client().get(
            f"/api/v1/loan-accounts/{fixture.account.pk}/", **fixture.auth
        )

        self.assertEqual(listing.status_code, 200, listing.content)
        self.assertEqual(
            (
                listing.json()["pagination"]["total_count"],
                listing.json()["data"],
                detail.status_code,
            ),
            (0, [], 404),
            detail.content,
        )

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

    def test_stale_senior_finance_initiation_is_excluded_before_count(self):
        fixture = workspace_tests.DisbursementWorkspaceApiTests(
            "test_admitted_senior_finance_reader_does_not_hit_internal_permission"
        )
        fixture.setUp()
        Disbursement = type(fixture.row)
        Disbursement.objects.filter(pk=fixture.row.pk).update(
            final_verification_comments="Changed after immutable initiation evidence."
        )

        response = Client().get(
            "/api/v1/disbursement-workspaces/",
            **fixture.fixture.fixture._auth(fixture.fixture.fixture.actor),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            (response.json()["pagination"]["total_count"], response.json()["data"]),
            (0, []),
        )

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

    def test_legacy_sap_delivery_checksum_backfill_preserves_only_coherent_rows(self):
        fixture = account_tests.ActiveLoanAccountReadApiTests(
            "test_exact_transfer_projects_active_funded_amounts_and_activation_time"
        )
        fixture.setUp()
        coherent = SapCustomerProfileRequest.objects.get(
            loan_application_id=fixture.account.loan_application_id,
            request_status=SapCustomerProfileRequest.STATUS_COMPLETED,
        )
        coherent.delivery_storage_checksum_sha256 = ""
        coherent.save(update_fields=["delivery_storage_checksum_sha256"])
        migration = import_module(
            "sfpcl_credit.sap_workflow.migrations."
            "0002_sapcustomerprofilerequest_delivery_storage_checksum_sha256"
        )
        migration.backfill_delivery_storage_checksums(
            type("Apps", (), {"get_model": staticmethod(
                lambda app, model: SapCustomerProfileRequest
                if (app, model) == ("sap_workflow", "SapCustomerProfileRequest")
                else fixture.account._meta.apps.get_model(app, model)
            )})(),
            None,
        )

        coherent.refresh_from_db()
        self.assertEqual(
            coherent.delivery_storage_checksum_sha256,
            coherent.excel_file.checksum_sha256,
        )
        retained_snapshot = coherent.delivery_file_id_snapshot
        coherent.delivery_file_id_snapshot = None
        coherent.delivery_storage_checksum_sha256 = ""
        coherent.save(
            update_fields=[
                "delivery_file_id_snapshot",
                "delivery_storage_checksum_sha256",
            ]
        )
        migration.backfill_delivery_storage_checksums(
            type("Apps", (), {"get_model": staticmethod(
                lambda app, model: SapCustomerProfileRequest
                if (app, model) == ("sap_workflow", "SapCustomerProfileRequest")
                else fixture.account._meta.apps.get_model(app, model)
            )})(),
            None,
        )
        coherent.refresh_from_db()
        self.assertEqual(coherent.delivery_storage_checksum_sha256, "")
        self.assertIsNotNone(retained_snapshot)

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
        source = "\n".join(
            (
                inspect.getsource(seed_epic_009_e2e_fixture),
                inspect.getsource(epic009_e2e_fixture),
            )
        )

        self.assertNotIn("sfpcl_credit.tests", source)
        self.assertNotIn(".setUp()", source)
        self.assertNotIn("._real_owner_initiation_fixture", source)
