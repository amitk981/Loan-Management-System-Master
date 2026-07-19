import json
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless

from django.db import close_old_connections, connection
from django.test import Client, TransactionTestCase

from sfpcl_credit.tests.test_direct_repayment_posting_api import (
    DirectRepaymentPostingApiTests,
)
from sfpcl_credit.tests.test_repayment_allocation_api import RepaymentAllocationApiTests
from sfpcl_credit.tests.test_bank_statement_matching_api import (
    BankStatementMatchingApiTests,
)


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class DirectRepaymentPostingPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = DirectRepaymentPostingApiTests(
            "test_valid_direct_receipt_and_exact_replay_create_one_pending_obligation"
        )
        fixture.setUp()
        self.fixture = fixture
        self.url = f"/api/v1/loan-accounts/{fixture.account.pk}/repayments/"

    def test_concurrent_same_idempotency_key_retains_one_receipt_and_obligation(self):
        payload = self.fixture._payload()
        statuses = self._race(
            (payload, "postgres-key-same"),
            (payload, "postgres-key-same"),
        )
        self.assertEqual(statuses, [200, 200])
        self._assert_single_chain()

    def test_concurrent_canonical_bank_reference_retains_one_receipt_and_obligation(self):
        payload = self.fixture._payload()
        changed_case = {
            **payload,
            "bank_reference_number": payload["bank_reference_number"].lower(),
        }
        statuses = self._race(
            (payload, "postgres-reference-a"),
            (changed_case, "postgres-reference-b"),
        )
        self.assertEqual(statuses, [200, 409])
        self._assert_single_chain()

    def _race(self, *requests):
        barrier = Barrier(len(requests))

        def submit(item):
            close_old_connections()
            barrier.wait()
            response = Client().post(
                self.url,
                data=json.dumps(item[0]),
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY=item[1],
                **self.fixture.auth,
            )
            close_old_connections()
            return response.status_code

        with ThreadPoolExecutor(max_workers=len(requests)) as pool:
            return sorted(pool.map(submit, requests))

    def _assert_single_chain(self):
        from sfpcl_credit.communications.models import Notification
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import Repayment, RepaymentSapPostingObligation

        self.assertEqual(Repayment.objects.count(), 1)
        self.assertEqual(RepaymentSapPostingObligation.objects.count(), 1)
        self.assertEqual(
            Notification.objects.filter(
                notification_type="repayment_sap_posting_due"
            ).count(),
            1,
        )
        self.assertEqual(
            AuditLog.objects.filter(action="repayment.receipt_created").count(), 1
        )


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class PrincipalFirstAllocationPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = RepaymentAllocationApiTests(
            "test_partial_receipt_reduces_principal_and_appends_immutable_evidence"
        )
        fixture.setUp()
        self.fixture = fixture
        captured = fixture.fixture._capture(
            fixture.fixture._payload(), "postgres-allocation-receipt"
        )
        self.repayment_id = captured.json()["data"]["repayment_id"]
        self.url = f"/api/v1/repayments/{self.repayment_id}/allocate/"

    def test_five_concurrent_allocations_retain_one_balance_transition_and_ledger_row(self):
        barrier = Barrier(5)

        def submit(_):
            close_old_connections()
            barrier.wait()
            response = Client().post(
                self.url,
                data=json.dumps(
                    {
                        "allocation_rule": "principal_first",
                        "remarks": "Concurrent allocation under the approved SOP.",
                    }
                ),
                content_type="application/json",
                **self.fixture.auth,
            )
            close_old_connections()
            return response.status_code

        with ThreadPoolExecutor(max_workers=5) as pool:
            statuses = sorted(pool.map(submit, range(5)))

        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import (
            LoanAccount,
            RepaymentAllocation,
            RepaymentLedgerEntry,
        )

        self.assertEqual(statuses, [200, 200, 200, 200, 200])
        account = LoanAccount.objects.get(pk=self.fixture.account.pk)
        self.assertEqual(str(account.principal_outstanding), "300000.00")
        self.assertEqual(str(account.total_outstanding), "300000.00")
        self.assertEqual(RepaymentAllocation.objects.count(), 1)
        self.assertEqual(RepaymentLedgerEntry.objects.count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="repayment.allocated").count(), 1)


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class BankStatementMatchingPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = BankStatementMatchingApiTests(
            "test_manual_match_requires_reason_and_one_receipt_cannot_be_consumed_twice"
        )
        fixture.setUp()
        self.fixture = fixture
        captured = fixture.fixture._capture(
            {
                **fixture.fixture._payload(),
                "amount_received": "60000.00",
                "received_date": "2026-12-09",
                "bank_reference_number": "UTR-PG-STATEMENT-MATCH",
            },
            "postgres-statement-receipt",
        )
        self.repayment_id = captured.json()["data"]["repayment_id"]
        imported = fixture._upload(
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-09,2026-12-09,60000.00,Race candidate A,UNKNOWN-PG-A,"
            f"{fixture.account.loan_account_number}\n"
            f"2026-12-09,2026-12-09,60000.00,Race candidate B,UNKNOWN-PG-B,"
            f"{fixture.account.loan_account_number}\n",
            key="postgres-statement-import",
        ).json()["data"]
        self.line_ids = [line["bank_statement_line_id"] for line in imported["lines"]]

    def test_concurrent_manual_matches_retain_one_statement_counterpart(self):
        barrier = Barrier(2)

        def submit(line_id):
            close_old_connections()
            barrier.wait()
            response = Client().post(
                f"/api/v1/bank-statement-lines/{line_id}/match/",
                data=json.dumps(
                    {
                        "repayment_id": self.repayment_id,
                        "reason": "Authorised concurrent reconciliation review.",
                    }
                ),
                content_type="application/json",
                **self.fixture.auth,
            )
            close_old_connections()
            return response.status_code

        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = sorted(pool.map(submit, self.line_ids))

        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import BankStatementLine, Repayment

        self.assertEqual(statuses, [200, 409])
        repayment = Repayment.objects.get(pk=self.repayment_id)
        self.assertEqual(repayment.statement_match_status, "manual_match_exception")
        self.assertEqual(
            BankStatementLine.objects.filter(
                matched_repayment_id=self.repayment_id, match_status="matched"
            ).count(),
            1,
        )
        self.assertEqual(
            str(repayment.bank_statement_line_id),
            str(
                BankStatementLine.objects.get(
                    matched_repayment_id=self.repayment_id
                ).pk
            ),
        )
        self.assertEqual(
            AuditLog.objects.filter(
                action="bank_statement.line_manually_matched"
            ).count(),
            1,
        )
