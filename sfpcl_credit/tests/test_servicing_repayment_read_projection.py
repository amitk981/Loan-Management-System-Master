from django.test import Client, TestCase


class ServicingRepaymentReadProjectionTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_repayment_allocation_api import (
            RepaymentAllocationApiTests,
        )

        fixture = RepaymentAllocationApiTests(
            "test_partial_receipt_reduces_principal_and_appends_immutable_evidence"
        )
        fixture.setUp()
        self.fixture = fixture
        self.account = fixture.account
        self.client = Client()
        self.auth = fixture.auth

    def test_lists_scoped_allocated_repayments_with_backend_money_and_pagination(self):
        captured = self.fixture.fixture._capture(
            self.fixture.fixture._payload(), "frontend-read-direct"
        )

        repayment_id = captured.json()["data"]["repayment_id"]
        self.fixture._schedule("400000.00")
        allocated = self.fixture._allocate(repayment_id)
        self.assertEqual(allocated.status_code, 200, allocated.content)

        response = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/repayments/?page=1&page_size=20",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            response.json()["pagination"],
            {
                "page": 1,
                "page_size": 20,
                "total_count": 1,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False,
            },
        )
        self.assertEqual(
            response.json()["data"],
            [
                {
                    "repayment_id": repayment_id,
                    "loan_account_id": str(self.account.pk),
                    "repayment_source": "direct_farmer",
                    "amount_received": "100000.00",
                    "received_date": "2026-12-04",
                    "payment_method": "rtgs",
                    "bank_reference_number": "UTR-DIRECT-VALIDATION-001",
                    "bank_statement_line_id": None,
                    "statement_match_status": "not_linked",
                    "allocation_status": "allocated",
                    "sap_posting_status": "posted",
                    "sap_posting_due_date": "2026-12-07",
                    "sap_entry_reference": f"SAP-{repayment_id}",
                    "sap_posted_at": "2026-12-05T10:00:00Z",
                    "allocation": {
                        "allocated_to_principal": "100000.00",
                        "allocated_to_interest": "0.00",
                        "allocated_to_charges": "0.00",
                        "unallocated_amount": "0.00",
                        "exception_reason": None,
                    },
                    "subsidiary_reconciliation": None,
                }
            ],
        )

    def test_read_projection_enforces_strict_pagination_and_nondisclosing_scope(self):
        user_fixture = self.fixture.fixture.fixture.fixture.owner.fixture.fixture
        auth_fixture = self.fixture.fixture.fixture.fixture.owner.fixture
        role_only = user_fixture._user("cfo", "Repayment Read Role Only")
        permission_only = user_fixture._user(
            "field_officer", "Repayment Read Permission Only"
        )
        outside_scope = user_fixture._user(
            "senior_manager_finance", "Repayment Read Outside Scope"
        )
        user_fixture._grant(permission_only, "finance.loan_account.read")
        user_fixture._grant(outside_scope, "finance.loan_account.read")
        url = f"/api/v1/loan-accounts/{self.account.pk}/repayments/"

        self.assertEqual(self.client.get(url).status_code, 401)
        self.assertEqual(
            self.client.get(url, **auth_fixture._auth(role_only)).status_code, 403
        )
        self.assertEqual(
            self.client.get(url, **auth_fixture._auth(permission_only)).status_code,
            403,
        )
        self.assertEqual(
            self.client.get(url, **auth_fixture._auth(outside_scope)).status_code, 404
        )
        for query in (
            "?page=0",
            "?page=abc",
            "?page=2",
            "?page_size=101",
            "?unknown=value",
        ):
            with self.subTest(query=query):
                self.assertEqual(
                    self.client.get(f"{url}{query}", **self.auth).status_code, 400
                )


class ServicingSubsidiaryReadProjectionTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_subsidiary_deduction_reconciliation_api import (
            SubsidiaryDeductionReconciliationApiTests,
        )

        fixture = SubsidiaryDeductionReconciliationApiTests(
            "test_verified_agreement_allows_subsidiary_deduction_capture"
        )
        fixture.setUp()
        self.fixture = fixture
        self.account = fixture.account
        self.client = Client()
        self.auth = fixture.auth

    def test_lists_retained_subsidiary_reconciliation_without_local_policy(self):
        agreement = self.fixture._verified_tri_party_agreement()
        captured = self.fixture._capture(
            self.fixture._payload(), "frontend-read-subsidiary"
        )
        repayment_id = captured.json()["data"]["repayment_id"]

        response = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/repayments/?page=1&page_size=20",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        row = response.json()["data"][0]
        self.assertEqual(row["repayment_id"], repayment_id)
        self.assertEqual(row["amount_received"], "75000.00")
        self.assertIsNone(row["allocation"])
        self.assertEqual(
            row["subsidiary_reconciliation"],
            {
                "subsidiary_company_id": str(self.fixture.subsidiary_company_id),
                "produce_payment_reference": "PRODUCE-PAY-001",
                "transfer_reference": "SUB-TRANSFER-001",
                "tri_party_agreement_id": str(agreement.pk),
                "reconciliation_status": "pending_statement",
                "treasury_verification_status": "pending",
            },
        )
