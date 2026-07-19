import json
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless

from django.db import close_old_connections, connection
from django.test import Client, TransactionTestCase

from sfpcl_credit.tests.test_bank_statement_matching_api import (
    BankStatementMatchingApiTests,
)


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class StatementEvidenceBoundaryPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = BankStatementMatchingApiTests(
            "test_manual_match_requires_reason_and_one_receipt_cannot_be_consumed_twice"
        )
        fixture.setUp()
        self.fixture = fixture

    def test_concurrent_lines_competing_for_one_receipt_retain_one_owner(self):
        repayment_id = self._capture("ONE", "70000.00")
        line_ids = self._import_lines(
            ("UNKNOWN-ONE-A", "70000.00"),
            ("UNKNOWN-ONE-B", "70000.00"),
            key="pg-owner-one-receipt",
        )
        statuses = self._race(
            lambda line_id: self._match(line_id, repayment_id), line_ids
        )
        self.assertEqual(statuses, [200, 409])
        self._assert_one_owner(repayment_id)

    def test_concurrent_receipts_competing_for_one_line_retain_one_owner(self):
        repayment_ids = [
            self._capture("TWO-A", "71000.00"),
            self._capture("TWO-B", "71000.00"),
        ]
        line_id = self._import_lines(
            ("UNKNOWN-TWO", "71000.00"), key="pg-owner-one-line"
        )[0]
        statuses = self._race(
            lambda repayment_id: self._match(line_id, repayment_id), repayment_ids
        )
        self.assertEqual(statuses, [200, 409])
        from sfpcl_credit.loans.models import BankStatementLine

        self.assertIn(
            str(BankStatementLine.objects.get(pk=line_id).matched_repayment_id),
            repayment_ids,
        )

    def test_concurrent_match_and_exception_retain_one_audit_decision(self):
        repayment_id = self._capture("THREE", "72000.00")
        line_id = self._import_lines(
            ("UNKNOWN-THREE", "72000.00"), key="pg-owner-decision"
        )[0]
        barrier = Barrier(2)

        def match():
            close_old_connections()
            barrier.wait()
            status = self._match(line_id, repayment_id)
            close_old_connections()
            return status

        def decide_exception():
            close_old_connections()
            barrier.wait()
            response = Client().post(
                f"/api/v1/bank-statement-lines/{line_id}/exception/",
                data=json.dumps(
                    {
                        "reason_code": "requires_investigation",
                        "reason": "Concurrent governed decision.",
                    }
                ),
                content_type="application/json",
                **self.fixture.auth,
            )
            close_old_connections()
            return response.status_code

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(match), pool.submit(decide_exception)]
            statuses = sorted(future.result() for future in futures)
        self.assertEqual(statuses, [200, 409])
        from sfpcl_credit.loans.models import BankStatementLine

        line = BankStatementLine.objects.get(pk=line_id)
        self.assertIsNotNone(line.match_audit_id)
        self.assertIn(line.match_status, {"matched", "exception"})

    def test_concurrent_direct_claims_retain_one_relationship_and_audit(self):
        line_id = self._import_lines(
            ("UTR-PG-DIRECT-FOUR", "73000.00"),
            key="pg-owner-direct-line",
            narration=f"Receipt {self.fixture.account.loan_account_number}",
        )[0]
        payload = {
            **self.fixture.fixture._payload(),
            "amount_received": "73000.00",
            "received_date": "2026-12-18",
            "bank_reference_number": "UTR-PG-DIRECT-FOUR",
            "bank_statement_line_id": line_id,
        }
        barrier = Barrier(2)

        def submit(key):
            close_old_connections()
            barrier.wait()
            response = Client().post(
                f"/api/v1/loan-accounts/{self.fixture.account.pk}/repayments/",
                data=json.dumps(payload),
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY=key,
                **self.fixture.auth,
            )
            close_old_connections()
            return response.status_code

        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = sorted(pool.map(submit, ("pg-direct-a", "pg-direct-b")))
        self.assertEqual(statuses, [200, 409])
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import BankStatementLine

        self.assertIsNotNone(BankStatementLine.objects.get(pk=line_id).matched_repayment_id)
        self.assertEqual(
            AuditLog.objects.filter(
                action="bank_statement.line_claimed_for_direct_receipt"
            ).count(),
            1,
        )

    def _capture(self, suffix, amount):
        response = self.fixture.fixture._capture(
            {
                **self.fixture.fixture._payload(),
                "amount_received": amount,
                "received_date": "2026-12-18",
                "bank_reference_number": f"UTR-PG-OWNER-{suffix}",
            },
            f"pg-owner-receipt-{suffix}",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()["data"]["repayment_id"]

    def _import_lines(self, *facts, key, narration="Manual review"):
        rows = "".join(
            f"2026-12-18,2026-12-18,{amount},{narration},{reference},"
            f"{self.fixture.account.loan_account_number}\n"
            for reference, amount in facts
        )
        response = self.fixture._upload(
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            + rows,
            key=key,
        )
        self.assertEqual(response.status_code, 200, response.content)
        return [
            line["bank_statement_line_id"] for line in response.json()["data"]["lines"]
        ]

    def _match(self, line_id, repayment_id):
        response = Client().post(
            f"/api/v1/bank-statement-lines/{line_id}/match/",
            data=json.dumps(
                {
                    "repayment_id": repayment_id,
                    "reason": "Authorised concurrent reconciliation review.",
                }
            ),
            content_type="application/json",
            **self.fixture.auth,
        )
        return response.status_code

    @staticmethod
    def _race(operation, values):
        barrier = Barrier(2)

        def submit(value):
            close_old_connections()
            barrier.wait()
            status = operation(value)
            close_old_connections()
            return status

        with ThreadPoolExecutor(max_workers=2) as pool:
            return sorted(pool.map(submit, values))

    def _assert_one_owner(self, repayment_id):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import BankStatementLine

        self.assertEqual(
            BankStatementLine.objects.filter(
                matched_repayment_id=repayment_id, match_status="matched"
            ).count(),
            1,
        )
        self.assertEqual(
            AuditLog.objects.filter(
                action="bank_statement.line_manually_matched"
            ).count(),
            1,
        )
