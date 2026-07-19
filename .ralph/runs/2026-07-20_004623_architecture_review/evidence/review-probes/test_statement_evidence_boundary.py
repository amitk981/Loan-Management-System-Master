"""Review-only public probes for the bank-statement evidence owner boundary."""

import os
import sys
from pathlib import Path
from uuid import uuid4

WORKTREE = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(WORKTREE))
sys.path.insert(0, str(WORKTREE / "sfpcl_credit"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.test.runner import DiscoverRunner


class StatementEvidenceBoundaryReviewProbe(TestCase):
    def test_direct_capture_rejects_nonexistent_statement_line_evidence(self):
        from sfpcl_credit.loans.models import BankStatementLine, Repayment
        from sfpcl_credit.tests.test_direct_repayment_posting_api import (
            DirectRepaymentPostingApiTests,
        )

        fixture = DirectRepaymentPostingApiTests(
            "test_valid_direct_receipt_and_exact_replay_create_one_pending_obligation"
        )
        fixture.setUp()
        nonexistent_line_id = uuid4()
        payload = {
            **fixture._payload(),
            "bank_reference_number": "UTR-REVIEW-ORPHAN-LINK",
            "bank_statement_line_id": str(nonexistent_line_id),
        }

        response = fixture._capture(payload, "review-orphan-line-link")

        self.assertEqual(
            response.status_code,
            400,
            "A supplied evidence link must resolve to canonical statement evidence; "
            f"observed {response.status_code}: {response.content.decode()}",
        )
        self.assertFalse(BankStatementLine.objects.filter(pk=nonexistent_line_id).exists())
        self.assertFalse(
            Repayment.objects.filter(bank_statement_line_id=nonexistent_line_id).exists()
        )

    def test_import_time_auto_match_respects_permission_and_loan_object_scope(self):
        from sfpcl_credit.loans.models import LoanAccount, Repayment
        from sfpcl_credit.tests.test_bank_statement_matching_api import (
            BankStatementMatchingApiTests,
        )

        fixture = BankStatementMatchingApiTests(
            "test_exact_statement_evidence_matches_one_receipt_without_financial_mutation"
        )
        fixture.setUp()
        captured = fixture.fixture._capture(
            {
                **fixture.fixture._payload(),
                "amount_received": "25000.00",
                "received_date": "2026-12-12",
                "bank_reference_number": "UTR-REVIEW-SCOPE-BYPASS",
            },
            "review-scope-receipt",
        )
        repayment_id = captured.json()["data"]["repayment_id"]
        LoanAccount.objects.filter(pk=fixture.account.pk).update(
            loan_account_status="sanctioned"
        )
        user_factory = fixture.fixture.fixture.fixture.owner.fixture.fixture
        auth_factory = fixture.fixture.fixture.fixture.owner.fixture
        importer = user_factory._user("credit_manager", "Import-Only Review Actor")
        user_factory._grant(importer, "finance.bank_statement.import")
        content = (
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-12,2026-12-12,25000.00,Receipt for {fixture.account.loan_account_number},"
            f"UTR-REVIEW-SCOPE-BYPASS,{fixture.account.loan_account_number}\n"
        )

        response = Client().post(
            "/api/v1/bank-statement-imports/",
            data={
                "file": SimpleUploadedFile(
                    "review-statement.csv", content.encode(), content_type="text/csv"
                ),
                "sfpcl_bank_account": "SFPCL-REVIEW-COLLECTION",
            },
            HTTP_IDEMPOTENCY_KEY="review-import-scope-bypass",
            **auth_factory._auth(importer),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            response.json()["data"]["matched_count"],
            0,
            "Import permission must not perform a match outside the actor's loan-object scope or "
            f"without match permission; observed {response.json()['data']}",
        )
        repayment = Repayment.objects.get(pk=repayment_id)
        self.assertIsNone(repayment.bank_statement_line_id)
        self.assertEqual(repayment.statement_match_status, "not_linked")


if __name__ == "__main__":
    failures = DiscoverRunner(verbosity=2).run_tests(
        ["__main__.StatementEvidenceBoundaryReviewProbe"]
    )
    sys.exit(bool(failures))
