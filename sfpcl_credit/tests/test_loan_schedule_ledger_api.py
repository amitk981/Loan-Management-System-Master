from datetime import timedelta
from uuid import uuid4

from django.db import IntegrityError, connection, transaction
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext

from sfpcl_credit.tests.api_contracts import assert_pagination_shape


class LoanScheduleLedgerApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_loan_account_reads_api import (
            ActiveLoanAccountReadApiTests,
        )

        fixture = ActiveLoanAccountReadApiTests(
            "test_exact_transfer_projects_active_funded_amounts_and_activation_time"
        )
        fixture.setUp()
        self.fixture = fixture
        self.account = fixture.account
        self.client = Client()
        self.auth = fixture.auth

    def _schedule_line(self, installment_number, **overrides):
        from sfpcl_credit.loans.models import RepaymentSchedule

        values = {
            "loan_account": self.account,
            "installment_number": installment_number,
            "due_date": self.account.repayment_date
            + timedelta(days=installment_number - 1),
            "principal_due": "1000.00",
            "interest_due": "100.00",
            "charges_due": "0.00",
            "total_due": "1100.00",
            "schedule_status": "pending",
        }
        values.update(overrides)
        return RepaymentSchedule.objects.create(**values)

    def test_authorised_reader_gets_ordered_decimal_schedule_truth(self):
        from sfpcl_credit.loans.models import RepaymentSchedule

        later = RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=2,
            due_date=self.account.repayment_date + timedelta(days=30),
            principal_due="200000.00",
            interest_due="12000.00",
            charges_due="250.00",
            total_due="212250.00",
            paid_principal="10000.00",
            paid_interest="500.00",
            paid_charges="0.00",
            schedule_status="pending",
        )
        earlier = RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=self.account.repayment_date,
            principal_due="200000.00",
            interest_due="10000.00",
            charges_due="0.00",
            total_due="210000.00",
            schedule_status="pending",
        )

        response = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/repayment-schedule/"
            "?page=1&page_size=20",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        assert_pagination_shape(self, response.json())
        self.assertEqual(response.json()["pagination"]["total_count"], 2)
        self.assertEqual(
            response.json()["data"],
            [
                {
                    "repayment_schedule_id": str(earlier.pk),
                    "installment_number": 1,
                    "due_date": self.account.repayment_date.isoformat(),
                    "principal_due": "200000.00",
                    "interest_due": "10000.00",
                    "charges_due": "0.00",
                    "total_due": "210000.00",
                    "paid_principal": "0.00",
                    "paid_interest": "0.00",
                    "paid_charges": "0.00",
                    "amount_received": "0.00",
                    "schedule_status": "pending",
                    "extended_due_date": None,
                    "created_at": self._utc(earlier.created_at),
                },
                {
                    "repayment_schedule_id": str(later.pk),
                    "installment_number": 2,
                    "due_date": later.due_date.isoformat(),
                    "principal_due": "200000.00",
                    "interest_due": "12000.00",
                    "charges_due": "250.00",
                    "total_due": "212250.00",
                    "paid_principal": "10000.00",
                    "paid_interest": "500.00",
                    "paid_charges": "0.00",
                    "amount_received": "10500.00",
                    "schedule_status": "pending",
                    "extended_due_date": None,
                    "created_at": self._utc(later.created_at),
                },
            ],
        )

    def test_ledger_projects_one_canonical_disbursement_without_copying_it(self):
        from sfpcl_credit.disbursements.models import (
            BankTransfer,
            Disbursement,
            InitialLoanPaymentSapPosting,
        )

        disbursement = Disbursement.objects.select_related(
            "transfer_success_actor_user"
        ).get(loan_account=self.account)
        transfer = BankTransfer.objects.get(disbursement=disbursement)
        posting = InitialLoanPaymentSapPosting.objects.get(
            disbursement=disbursement
        )
        source_snapshots = (
            Disbursement.objects.values().get(pk=disbursement.pk),
            BankTransfer.objects.values().get(pk=transfer.pk),
            InitialLoanPaymentSapPosting.objects.values().get(pk=posting.pk),
        )

        response = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/ledger/"
            "?page=1&page_size=20",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        assert_pagination_shape(self, response.json())
        self.assertEqual(response.json()["pagination"]["total_count"], 1)
        self.assertEqual(
            response.json()["data"],
            [
                {
                    "transaction_date": disbursement.disbursed_at.date().isoformat(),
                    "transaction_type": "disbursement",
                    "owner_reference": {
                        "entity_type": "disbursement",
                        "entity_id": str(disbursement.pk),
                    },
                    "reference": transfer.bank_reference_number,
                    "debit": "400000.00",
                    "credit": "0.00",
                    "principal_balance": "400000.00",
                    "interest_balance": "0.00",
                    "total_outstanding": "400000.00",
                    "actor": {
                        "user_id": str(disbursement.transfer_success_actor_user_id),
                        "display_name": disbursement.transfer_success_actor_user.full_name,
                    },
                    "sap_status": posting.posting_status,
                    "remarks": "Initial loan disbursement.",
                }
            ],
        )
        self.assertEqual(
            (
                Disbursement.objects.values().get(pk=disbursement.pk),
                BankTransfer.objects.values().get(pk=transfer.pk),
                InitialLoanPaymentSapPosting.objects.values().get(pk=posting.pk),
            ),
            source_snapshots,
        )

    def test_schedule_pagination_is_stable_at_page_boundaries(self):
        for installment_number in range(1, 22):
            self._schedule_line(installment_number)

        first = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/repayment-schedule/"
            "?page=1&page_size=20",
            **self.auth,
        )
        second = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/repayment-schedule/"
            "?page=2&page_size=20",
            **self.auth,
        )

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(second.status_code, 200, second.content)
        self.assertEqual(first.json()["pagination"]["total_count"], 21)
        self.assertEqual(first.json()["pagination"]["total_pages"], 2)
        self.assertEqual(
            [row["installment_number"] for row in first.json()["data"]],
            list(range(1, 21)),
        )
        self.assertEqual(
            [row["installment_number"] for row in second.json()["data"]], [21]
        )

    def test_later_servicing_balances_preserve_schedule_and_opening_disbursement(self):
        type(self.account).objects.filter(pk=self.account.pk).update(
            loan_account_status="partially_repaid",
            principal_outstanding="350000.00",
            interest_outstanding="10000.00",
            total_outstanding="360000.00",
        )

        schedule = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/repayment-schedule/",
            **self.auth,
        )
        ledger = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/ledger/", **self.auth
        )

        self.assertEqual(schedule.status_code, 200, schedule.content)
        self.assertEqual(ledger.status_code, 200, ledger.content)
        self.assertEqual(ledger.json()["pagination"]["total_count"], 1)
        self.assertEqual(ledger.json()["data"][0]["debit"], "400000.00")
        self.assertEqual(
            ledger.json()["data"][0]["principal_balance"], "400000.00"
        )

    def test_historical_ledger_rejects_drifted_immutable_activation_amount(self):
        type(self.account).objects.filter(pk=self.account.pk).update(
            loan_account_status="partially_repaid",
            disbursed_amount="399999.00",
            principal_outstanding="350000.00",
            interest_outstanding="10000.00",
            total_outstanding="360000.00",
        )

        response = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/ledger/", **self.auth
        )

        self.assertEqual(response.status_code, 404, response.content)

        type(self.account).objects.filter(pk=self.account.pk).update(
            disbursed_amount="400000.00",
            tenure_start_date=self.account.tenure_start_date + timedelta(days=1),
        )
        changed_date = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/ledger/", **self.auth
        )
        self.assertEqual(changed_date.status_code, 404, changed_date.content)

    def test_schedule_and_ledger_queries_validate_the_same_bounded_parameters(self):
        invalid_queries = (
            ("page=0", {"page": "Must be a positive integer."}),
            ("page=2", {"page": "Page is out of range."}),
            ("page_size=101", {"page_size": "Must be at most 100."}),
            ("page_size=abc", {"page_size": "Must be a positive integer."}),
            ("ordering=date", {"ordering": "Unknown query parameter."}),
        )
        for endpoint in ("repayment-schedule", "ledger"):
            for query, expected_errors in invalid_queries:
                with self.subTest(endpoint=endpoint, query=query):
                    response = self.client.get(
                        f"/api/v1/loan-accounts/{self.account.pk}/{endpoint}/?{query}",
                        **self.auth,
                    )
                    self.assertEqual(response.status_code, 400, response.content)
                    self.assertEqual(
                        response.json()["error"]["field_errors"], expected_errors
                    )

    def test_schedule_and_ledger_enforce_auth_role_permission_and_object_scope(self):
        user_fixture = self.fixture.fixture.owner.fixture.fixture
        auth_fixture = self.fixture.fixture.owner.fixture
        role_without_permission = user_fixture._user(
            "cfo", "CFO Without Loan Read Grant"
        )
        permission_without_role = user_fixture._user(
            "field_officer", "Field Officer With Read Grant"
        )
        user_fixture._grant(permission_without_role, "finance.loan_account.read")
        outside_scope = user_fixture._user(
            "senior_manager_finance", "Unassigned Senior Finance Reader"
        )
        user_fixture._grant(outside_scope, "finance.loan_account.read")

        for endpoint in ("repayment-schedule", "ledger"):
            url = f"/api/v1/loan-accounts/{self.account.pk}/{endpoint}/"
            with self.subTest(endpoint=endpoint, authority="unauthenticated"):
                self.assertEqual(self.client.get(url).status_code, 401)
            with self.subTest(endpoint=endpoint, authority="role_only"):
                self.assertEqual(
                    self.client.get(url, **auth_fixture._auth(role_without_permission)).status_code,
                    403,
                )
            with self.subTest(endpoint=endpoint, authority="permission_only"):
                self.assertEqual(
                    self.client.get(
                        url, **auth_fixture._auth(permission_without_role)
                    ).status_code,
                    403,
                )
            with self.subTest(endpoint=endpoint, authority="cross_scope"):
                self.assertEqual(
                    self.client.get(url, **auth_fixture._auth(outside_scope)).status_code,
                    404,
                )
            with self.subTest(endpoint=endpoint, authority="missing"):
                self.assertEqual(
                    self.client.get(
                        f"/api/v1/loan-accounts/{uuid4()}/{endpoint}/", **self.auth
                    ).status_code,
                    404,
                )

    def test_database_rejects_duplicate_installments_and_negative_financial_truth(self):
        self._schedule_line(1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            self._schedule_line(1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            self._schedule_line(
                2,
                principal_due="-1.00",
                interest_due="1.00",
                total_due="0.00",
            )
        with self.assertRaises(IntegrityError), transaction.atomic():
            self._schedule_line(3, total_due="1101.00")
        with self.assertRaises(IntegrityError), transaction.atomic():
            type(self.account).objects.filter(pk=self.account.pk).update(
                principal_outstanding="-1.00"
            )

    def test_populated_schedule_and_ledger_reads_have_query_ceilings(self):
        for installment_number in range(1, 21):
            self._schedule_line(installment_number)

        with CaptureQueriesContext(connection) as schedule_queries:
            schedule = self.client.get(
                f"/api/v1/loan-accounts/{self.account.pk}/repayment-schedule/",
                **self.auth,
            )
        with CaptureQueriesContext(connection) as ledger_queries:
            ledger = self.client.get(
                f"/api/v1/loan-accounts/{self.account.pk}/ledger/", **self.auth
            )

        self.assertEqual(schedule.status_code, 200, schedule.content)
        self.assertEqual(ledger.status_code, 200, ledger.content)
        self.assertEqual(len(schedule.json()["data"]), 20)
        self.assertEqual(len(ledger.json()["data"]), 1)
        self.assertLessEqual(len(schedule_queries), 35)
        self.assertLessEqual(len(ledger_queries), 35)

    @staticmethod
    def _utc(value):
        return value.isoformat().replace("+00:00", "Z")


class EmptyLoanScheduleLedgerApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_loan_account_reads_api import (
            LoanAccountReadApiTests,
        )

        fixture = LoanAccountReadApiTests(
            "test_sanctioned_list_and_detail_are_exact_paginated_zero_write_projections"
        )
        fixture.setUp()
        self.fixture = fixture
        self.client = Client()

    def test_sanctioned_account_has_truthful_empty_schedule_and_ledger(self):
        for endpoint in ("repayment-schedule", "ledger"):
            with self.subTest(endpoint=endpoint):
                response = self.client.get(
                    f"/api/v1/loan-accounts/{self.fixture.account.pk}/{endpoint}/",
                    **self.fixture.auth,
                )
                self.assertEqual(response.status_code, 200, response.content)
                self.assertEqual(response.json()["data"], [])
                self.assertEqual(
                    response.json()["pagination"],
                    {
                        "page": 1,
                        "page_size": 20,
                        "total_count": 0,
                        "total_pages": 1,
                        "has_next": False,
                        "has_previous": False,
                    },
                )
