from django.db import connection
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from uuid import uuid4

from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.loans.models import LoanAccount, LoanStatusHistory
from sfpcl_credit.tests.api_contracts import (
    assert_pagination_shape,
    assert_success_envelope,
)
from sfpcl_credit.workflows.models import WorkflowEvent


class LoanAccountReadApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_loan_account_creation_api import (
            LoanAccountCreationApiTests,
        )

        fixture = LoanAccountCreationApiTests(
            "test_terminal_sanction_creates_unfunded_account_terms_and_evidence"
        )
        fixture.setUp()
        created = fixture._post(
            {
                "sanction_decision_id": str(fixture.sanction.pk),
                "loan_account_number": "LN-2026-00025",
            }
        )
        self.assertEqual(created.status_code, 200, created.content)
        self.fixture = fixture
        self.account = LoanAccount.objects.get()
        self.reader = fixture._user("accounts_head", "Accounts Head")
        fixture._grant(self.reader, "finance.loan_account.read")
        self.client = Client()
        self.auth = fixture._auth(self.reader)

    def test_sanctioned_list_and_detail_are_exact_paginated_zero_write_projections(self):
        counts_before = self._business_counts()

        listing = self.client.get(
            "/api/v1/loan-accounts/?page=1&page_size=20", **self.auth
        )

        self.assertEqual(listing.status_code, 200, listing.content)
        assert_pagination_shape(self, listing.json())
        self.assertEqual(listing.json()["pagination"]["total_count"], 1)
        expected = {
            "loan_account_id": str(self.account.pk),
            "loan_account_number": "LN-2026-00025",
            "loan_application_id": str(self.fixture.application.pk),
            "application_reference_number": self.fixture.application.application_reference_number,
            "member": {
                "member_id": str(self.fixture.application.member_id),
                "display_name": "Ramesh Patil",
            },
            "sap_customer_code": None,
            "loan_type": "short_term",
            "facility_type": "short_term",
            "interest_rate_type": "floating",
            "current_interest_rate": "9.2500",
            "sanctioned_amount": "400000.00",
            "disbursed_amount": "0.00",
            "principal_outstanding": "0.00",
            "interest_outstanding": "0.00",
            "charges_outstanding": "0.00",
            "total_outstanding": "0.00",
            "loan_account_status": "sanctioned",
            "tenure_start_date": None,
            "tenure_end_date": None,
            "repayment_date": "2027-06-22",
            "tenure_months": 12,
            "created_at": self._utc(self.account.created_at),
            "activated_at": None,
        }
        self.assertEqual(listing.json()["data"], [expected])

        detail = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/", **self.auth
        )
        self.assertEqual(detail.status_code, 200, detail.content)
        assert_success_envelope(self, detail.json())
        self.assertEqual(detail.json()["data"], expected)
        self.assertEqual(self._business_counts(), counts_before)

        serialized = str(detail.json()) + str(listing.json())
        for forbidden in (
            "protected-pan",
            "protected-aadhaar",
            "bank_reference",
            "evidence_document",
            "checksum",
            "idempotency",
            "request_id_digest",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_populated_loan_account_collection_has_a_query_ceiling(self):
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                "/api/v1/loan-accounts/?page=1&page_size=20", **self.auth
            )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 1)
        self.assertLessEqual(len(queries), 30)

    def test_portfolio_authority_requires_both_source_role_and_current_permission(self):
        cfo = self.fixture._user("cfo", "CFO Portfolio Reader")
        self.fixture._grant(cfo, "finance.loan_account.read")
        cfo_detail = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/",
            **self.fixture._auth(cfo),
        )

        permission_only = self.fixture._user(
            "field_officer", "Intake Assignment Is Not Account Scope"
        )
        self.fixture._grant(permission_only, "finance.loan_account.read")
        permission_only_detail = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/",
            **self.fixture._auth(permission_only),
        )

        from sfpcl_credit.identity.models import RolePermission
        RolePermission.objects.filter(role=self.reader.primary_role).delete()
        role_only_detail = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/",
            **self.fixture._auth(self.reader),
        )

        self.assertEqual(cfo_detail.status_code, 200, cfo_detail.content)
        self.assertEqual(permission_only_detail.status_code, 403)
        self.assertEqual(role_only_detail.status_code, 403)

    def test_query_validation_and_missing_detail_are_strict_and_nondisclosing(self):
        for query in ("page=0", "page=2", "page_size=101", "page_size=abc"):
            with self.subTest(query=query):
                response = self.client.get(
                    f"/api/v1/loan-accounts/?{query}", **self.auth
                )
                self.assertEqual(response.status_code, 400, response.content)
                self.assertEqual(response.json()["error"]["code"], "VALIDATION_ERROR")
        missing = self.client.get(
            f"/api/v1/loan-accounts/{uuid4()}/", **self.auth
        )
        self.assertEqual(missing.status_code, 404, missing.content)
        self.assertEqual(missing.json()["error"]["code"], "NOT_FOUND")

    def test_source_supported_filters_and_dpd_deferral_are_explicit(self):
        matches = (
            f"search=00025",
            "loan_account_status=sanctioned",
            f"member_id={self.account.member_id}",
        )
        for query in matches:
            with self.subTest(query=query):
                response = self.client.get(
                    f"/api/v1/loan-accounts/?{query}", **self.auth
                )
                self.assertEqual(response.status_code, 200, response.content)
                self.assertEqual(response.json()["pagination"]["total_count"], 1)

        for query in (
            "search=does-not-exist",
            "loan_account_status=active",
            f"member_id={uuid4()}",
        ):
            with self.subTest(query=query):
                response = self.client.get(
                    f"/api/v1/loan-accounts/?{query}", **self.auth
                )
                self.assertEqual(response.status_code, 200, response.content)
                self.assertEqual(response.json()["data"], [])

        deferred = self.client.get(
            "/api/v1/loan-accounts/?dpd_bucket=current", **self.auth
        )
        self.assertEqual(deferred.status_code, 400, deferred.content)
        self.assertEqual(
            deferred.json()["error"]["field_errors"],
            {"dpd_bucket": "DPD filtering is owned by Epic 010 and is not available yet."},
        )

    def test_changed_creation_amount_fails_closed_without_existence_disclosure(self):
        LoanAccount.objects.filter(pk=self.account.pk).update(
            sanctioned_amount="399999.00"
        )

        detail = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/", **self.auth
        )
        listing = self.client.get("/api/v1/loan-accounts/", **self.auth)

        self.assertEqual(detail.status_code, 404, detail.content)
        self.assertEqual(listing.status_code, 200, listing.content)
        self.assertEqual(listing.json()["data"], [])

    def test_source_role_scope_matrix_is_identical_for_list_and_detail(self):
        from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant

        company_secretary = self.fixture._user(
            "company_secretary", "Company Secretary Reader"
        )
        auditor = self.fixture._user("internal_auditor", "Scoped Auditor")
        credit = self.fixture._user("credit_manager", "Pre-activation Credit Reader")
        finance = self.fixture._user(
            "senior_manager_finance", "Unassigned Finance Reader"
        )
        cfc = self.fixture._user(
            "chief_financial_controller", "Unassigned CFC Reader"
        )
        for actor in (company_secretary, auditor, credit, finance, cfc):
            self.fixture._grant(actor, "finance.loan_account.read")
        ApprovalCaseReadScopeGrant.objects.create(
            role=auditor.primary_role,
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
            status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
        )

        for actor, allowed in (
            (company_secretary, True),
            (auditor, True),
            (credit, False),
            (finance, False),
            (cfc, False),
        ):
            with self.subTest(role=actor.primary_role.role_code):
                auth = self.fixture._auth(actor)
                detail = self.client.get(
                    f"/api/v1/loan-accounts/{self.account.pk}/", **auth
                )
                listing = self.client.get("/api/v1/loan-accounts/", **auth)
                self.assertEqual(detail.status_code, 200 if allowed else 404)
                self.assertEqual(
                    listing.json()["pagination"]["total_count"], 1 if allowed else 0
                )

    @staticmethod
    def _utc(value):
        return value.isoformat().replace("+00:00", "Z")

    @staticmethod
    def _business_counts():
        return (
            LoanAccount.objects.count(),
            LoanStatusHistory.objects.count(),
            AuditLog.objects.count(),
            WorkflowEvent.objects.count(),
        )


class ActiveLoanAccountReadApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_disbursement_transfer_success_api import (
            DisbursementTransferSuccessApiTests,
        )

        fixture = DisbursementTransferSuccessApiTests(
            "test_public_success_records_transfer_and_activates_exact_loan_atomically"
        )
        fixture.setUp()
        self.disbursed_at = timezone.now()
        transferred = fixture._post(
            bank_reference_number="RBL-READ-UTR-001",
            disbursed_at=self.disbursed_at,
        )
        self.assertEqual(transferred.status_code, 200, transferred.content)
        self.fixture = fixture
        self.account = LoanAccount.objects.get(pk=fixture.owner.fixture.application.loan_account.pk)
        self.account.refresh_from_db()
        self.reader = fixture.owner.fixture.fixture._user(
            "accounts_head", "Account Read Portfolio Owner"
        )
        fixture.owner.fixture.fixture._grant(
            self.reader, "finance.loan_account.read"
        )
        self.client = Client()
        self.auth = fixture.owner.fixture._auth(self.reader)

    def test_exact_transfer_projects_active_funded_amounts_and_activation_time(self):
        from sfpcl_credit.disbursements.modules.post_transfer_evidence import (
            resolve_post_transfer_evidence,
        )
        from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
            get_account_customer_code,
        )

        self.assertIsNotNone(
            get_account_customer_code(
                application_id=self.account.loan_application_id,
                member_id=self.account.member_id,
                customer_code_id=self.account.sap_customer_code_id,
            )
        )
        self.assertIsNotNone(
            resolve_post_transfer_evidence(
                application_id=self.account.loan_application_id
            )
        )
        response = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/", **self.auth
        )

        self.assertEqual(response.status_code, 200, response.content)
        assert_success_envelope(self, response.json())
        data = response.json()["data"]
        self.assertEqual(data["loan_account_status"], "active")
        self.assertEqual(data["sanctioned_amount"], "400000.00")
        self.assertEqual(data["disbursed_amount"], "400000.00")
        self.assertEqual(data["principal_outstanding"], "400000.00")
        self.assertEqual(data["interest_outstanding"], "0.00")
        self.assertEqual(data["charges_outstanding"], "0.00")
        self.assertEqual(data["total_outstanding"], "400000.00")
        self.assertEqual(data["tenure_start_date"], self.disbursed_at.date().isoformat())
        self.assertEqual(
            data["tenure_end_date"],
            self.account.tenure_end_date.isoformat()
            if self.account.tenure_end_date
            else None,
        )
        self.assertEqual(data["activated_at"], self._utc(self.disbursed_at))
        self.assertNotIn("bank_reference_number", str(response.json()))
        self.assertNotIn("disbursement_advice_communication_id", str(response.json()))
        from sfpcl_credit.sap_workflow.models import SapCustomerCode

        SapCustomerCode.objects.filter(pk=self.account.sap_customer_code_id).update(
            status=SapCustomerCode.STATUS_INACTIVE
        )

        detail = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/", **self.auth
        )
        listing = self.client.get("/api/v1/loan-accounts/", **self.auth)

        self.assertEqual(detail.status_code, 404, detail.content)
        self.assertEqual(detail.json()["error"]["code"], "NOT_FOUND")
        self.assertEqual(listing.status_code, 200, listing.content)
        self.assertEqual(listing.json()["data"], [])
        self.assertEqual(listing.json()["pagination"]["total_count"], 0)

    def test_exact_active_scope_allows_assigned_finance_cfc_and_credit(self):
        finance = self.fixture.owner.fixture.actor
        cfc = self.fixture.actor
        credit = self.fixture.owner.fixture.fixture._user(
            "credit_manager", "Active Monitoring Credit Reader"
        )
        for actor in (finance, cfc, credit):
            self.fixture.owner.fixture.fixture._grant(
                actor, "finance.loan_account.read"
            )

        for actor in (finance, cfc, credit):
            with self.subTest(role=actor.primary_role.role_code):
                auth = self.fixture.owner.fixture._auth(actor)
                detail = self.client.get(
                    f"/api/v1/loan-accounts/{self.account.pk}/", **auth
                )
                listing = self.client.get("/api/v1/loan-accounts/", **auth)
                self.assertEqual(detail.status_code, 200, detail.content)
                self.assertEqual(listing.status_code, 200, listing.content)
                self.assertEqual(listing.json()["pagination"]["total_count"], 1)

    @staticmethod
    def _utc(value):
        return value.isoformat().replace("+00:00", "Z")
