"""Review-only public probes for the repayment allocation admission boundary."""

import json
import os
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(WORKTREE))
sys.path.insert(0, str(WORKTREE / "sfpcl_credit"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.test import TestCase
from django.test.runner import DiscoverRunner


class AllocationAdmissionReviewProbe(TestCase):
    def test_pending_sap_receipt_cannot_change_financial_balances(self):
        from sfpcl_credit.loans.models import (
            LoanAccount,
            RepaymentAllocation,
            RepaymentLedgerEntry,
        )
        from sfpcl_credit.tests.test_repayment_allocation_api import (
            RepaymentAllocationApiTests,
        )

        fixture = RepaymentAllocationApiTests(
            "test_partial_receipt_reduces_principal_and_appends_immutable_evidence"
        )
        fixture.setUp()
        captured = fixture.fixture._capture(
            fixture.fixture._payload(), "review-pending-sap-admission"
        )
        repayment_id = captured.json()["data"]["repayment_id"]
        account_before = LoanAccount.objects.values().get(pk=fixture.account.pk)

        response = fixture._allocate(repayment_id)

        self.assertEqual(
            response.status_code,
            409,
            "M09-FR-010 requires the SAP-posting prerequisite before the balance transition; "
            f"observed {response.status_code}: {response.content.decode()}",
        )
        self.assertEqual(RepaymentAllocation.objects.count(), 0)
        self.assertEqual(RepaymentLedgerEntry.objects.count(), 0)
        self.assertEqual(
            LoanAccount.objects.values().get(pk=fixture.account.pk), account_before
        )

    def test_manual_match_exception_requires_010c2_approval_before_allocation(self):
        from sfpcl_credit.loans.models import (
            LoanAccount,
            RepaymentAllocation,
            RepaymentLedgerEntry,
        )
        from sfpcl_credit.tests.test_bank_statement_matching_api import (
            BankStatementMatchingApiTests,
        )

        fixture = BankStatementMatchingApiTests(
            "test_manual_match_requires_reason_and_one_receipt_cannot_be_consumed_twice"
        )
        fixture.setUp()
        fixture.fixture.fixture.fixture.owner.fixture.fixture._grant(
            fixture.actor, "finance.repayment.allocate"
        )
        captured = fixture.fixture._capture(
            {
                **fixture.fixture._payload(),
                "amount_received": "75000.00",
                "received_date": "2026-12-06",
                "bank_reference_number": "UTR-REVIEW-MANUAL-EXCEPTION",
            },
            "review-manual-exception-receipt",
        )
        repayment_id = captured.json()["data"]["repayment_id"]
        posted = fixture.fixture._mark(
            repayment_id,
            {
                "sap_entry_reference": "SAP-REVIEW-POSTED",
                "sap_posted_at": "2026-12-07T10:00:00Z",
                "remarks": "Review-only posting prerequisite.",
            },
        )
        self.assertEqual(posted.status_code, 200, posted.content)
        imported = fixture._upload(
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-06,2026-12-06,75000.00,Manual review,UNKNOWN-REVIEW,"
            f"{fixture.account.loan_account_number}\n",
            key="review-manual-exception-import",
        ).json()["data"]
        line_id = imported["lines"][0]["bank_statement_line_id"]
        matched = fixture._match(
            line_id,
            repayment_id,
            "Review-only manual evidence decision pending terminal approval.",
        )
        self.assertEqual(matched.status_code, 200, matched.content)
        account_before = LoanAccount.objects.values().get(pk=fixture.account.pk)

        response = fixture.client.post(
            f"/api/v1/repayments/{repayment_id}/allocate/",
            data=json.dumps(
                {
                    "allocation_rule": "principal_first",
                    "remarks": "Must be governed by 010C2 approval.",
                }
            ),
            content_type="application/json",
            **fixture.auth,
        )

        self.assertEqual(
            response.status_code,
            409,
            "010D defers manual-exception financial allocation to 010C2 approval; "
            f"observed {response.status_code}: {response.content.decode()}",
        )
        self.assertEqual(RepaymentAllocation.objects.count(), 0)
        self.assertEqual(RepaymentLedgerEntry.objects.count(), 0)
        self.assertEqual(
            LoanAccount.objects.values().get(pk=fixture.account.pk), account_before
        )


if __name__ == "__main__":
    failures = DiscoverRunner(verbosity=2).run_tests(
        ["__main__.AllocationAdmissionReviewProbe"]
    )
    sys.exit(bool(failures))
