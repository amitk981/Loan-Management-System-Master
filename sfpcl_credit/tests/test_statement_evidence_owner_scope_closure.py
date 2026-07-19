from uuid import uuid4

from django.core.exceptions import FieldDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase


class StatementEvidenceOwnerScopeClosureTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_direct_repayment_posting_api import (
            DirectRepaymentPostingApiTests,
        )

        fixture = DirectRepaymentPostingApiTests(
            "test_valid_direct_receipt_and_exact_replay_create_one_pending_obligation"
        )
        fixture.setUp()
        self.fixture = fixture

    def test_statement_line_is_the_only_database_relationship_owner(self):
        from sfpcl_credit.loans.models import Repayment

        with self.assertRaises(FieldDoesNotExist):
            Repayment._meta.get_field("bank_statement_line_id")

    def test_direct_capture_rejects_nonexistent_statement_line_evidence(self):
        from sfpcl_credit.communications.models import Notification
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import Repayment

        response = self.fixture._capture(
            {
                **self.fixture._payload(),
                "bank_statement_line_id": str(uuid4()),
            },
            "statement-owner-orphan",
        )

        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(Repayment.objects.count(), 0)
        self.assertEqual(
            Notification.objects.filter(
                notification_type="repayment_sap_posting_due"
            ).count(),
            0,
        )
        self.assertEqual(
            AuditLog.objects.filter(action__startswith="repayment.").count(), 0
        )

    def test_import_time_auto_match_respects_permission_and_loan_object_scope(self):
        from sfpcl_credit.configurations.modules.source_bank_governance import (
            resolve_source_bank_account,
        )
        from sfpcl_credit.loans.models import LoanAccount, Repayment

        captured = self.fixture._capture(
            {
                **self.fixture._payload(),
                "amount_received": "43000.00",
                "received_date": "2026-12-09",
                "bank_reference_number": "UTR-SCOPE-CLOSURE-001",
            },
            "statement-scope-receipt",
        )
        self.assertEqual(captured.status_code, 200, captured.content)
        repayment_id = captured.json()["data"]["repayment_id"]

        user_fixture = self.fixture.fixture.fixture.owner.fixture.fixture
        auth_fixture = self.fixture.fixture.fixture.owner.fixture
        importer = user_fixture._user(
            "credit_manager", "Statement Import Scope Closure"
        )
        user_fixture._grant(importer, "finance.bank_statement.import")
        LoanAccount.objects.filter(pk=self.fixture.account.pk).update(
            loan_account_status="sanctioned"
        )
        content = (
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-09,2026-12-09,43000.00,Receipt for "
            f"{self.fixture.account.loan_account_number},UTR-SCOPE-CLOSURE-001,"
            f"{self.fixture.account.loan_account_number}\n"
        )

        response = self.fixture.client.post(
            "/api/v1/bank-statement-imports/",
            data={
                "file": SimpleUploadedFile(
                    "scope.csv", content.encode(), content_type="text/csv"
                ),
                "collection_bank_account_id": str(
                    resolve_source_bank_account().source_bank_account_id
                ),
            },
            HTTP_IDEMPOTENCY_KEY="statement-scope-import",
            **auth_fixture._auth(importer),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["data"]["matched_count"], 0)
        self.assertEqual(response.json()["data"]["unmatched_count"], 1)
        self.assertEqual(
            response.json()["data"]["lines"][0]["match_reason_code"],
            "match_authority_or_scope_required",
        )
        repayment = Repayment.objects.get(pk=repayment_id)
        self.assertIsNone(repayment.bank_statement_line_id)

    def test_subsidiary_auto_match_requires_borrower_and_application_facts(self):
        from sfpcl_credit.applications.models import LoanApplication
        from sfpcl_credit.configurations.modules.source_bank_governance import (
            resolve_source_bank_account,
        )
        from sfpcl_credit.loans.models import Repayment

        self.fixture.fixture.fixture.owner.fixture.fixture._grant(
            self.fixture.actor,
            "finance.bank_statement.import",
            "finance.bank_statement.match",
        )
        borrower_name = self.fixture.account.member.legal_name
        application_number = (
            self.fixture.account.loan_application.application_reference_number
        )
        conflicting_application = LoanApplication.objects.create(
            application_reference_number="APP-OTHER-AMBIGUOUS",
            member=self.fixture.account.member,
            borrower_type=self.fixture.account.member.member_type,
            received_by_user=self.fixture.actor,
        )
        receipt_ids = []
        for suffix in (
            "BORROWER",
            "APPLICATION",
            "ACCOUNT",
            "BOTH",
            "AMBIGUOUS",
            "MISSING",
        ):
            response = self.fixture._capture(
                {
                    **self.fixture._payload(),
                    "amount_received": "51000.00",
                    "received_date": "2026-12-12",
                    "bank_reference_number": f"UTR-SUBSIDIARY-{suffix}",
                },
                f"statement-subsidiary-{suffix.lower()}",
            )
            self.assertEqual(response.status_code, 200, response.content)
            receipt_ids.append(response.json()["data"]["repayment_id"])
        Repayment.objects.filter(pk__in=receipt_ids).update(
            repayment_source="subsidiary_deduction",
            payment_method="subsidiary_transfer",
        )
        content = (
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-12,2026-12-12,51000.00,{borrower_name},"
            f"UTR-SUBSIDIARY-BORROWER,{self.fixture.account.loan_account_number}\n"
            f"2026-12-12,2026-12-12,51000.00,{application_number},"
            f"UTR-SUBSIDIARY-APPLICATION,{self.fixture.account.loan_account_number}\n"
            f"2026-12-12,2026-12-12,51000.00,{self.fixture.account.loan_account_number},"
            f"UTR-SUBSIDIARY-ACCOUNT,{self.fixture.account.loan_account_number}\n"
            f"2026-12-12,2026-12-12,51000.00,{borrower_name} {application_number},"
            f"UTR-SUBSIDIARY-BOTH,{self.fixture.account.loan_account_number}\n"
            f"2026-12-12,2026-12-12,51000.00,{borrower_name} {application_number} "
            f"{conflicting_application.application_reference_number},"
            f"UTR-SUBSIDIARY-AMBIGUOUS,{self.fixture.account.loan_account_number}\n"
            f"2026-12-12,2026-12-12,51000.00,,UTR-SUBSIDIARY-MISSING,"
            f"{self.fixture.account.loan_account_number}\n"
        )

        response = self.fixture.client.post(
            "/api/v1/bank-statement-imports/",
            data={
                "file": SimpleUploadedFile(
                    "subsidiary.csv", content.encode(), content_type="text/csv"
                ),
                "collection_bank_account_id": str(
                    resolve_source_bank_account().source_bank_account_id
                ),
            },
            HTTP_IDEMPOTENCY_KEY="statement-subsidiary-matrix",
            **self.fixture.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        lines = response.json()["data"]["lines"]
        self.assertEqual(
            [line["match_status"] for line in lines],
            ["unmatched", "unmatched", "unmatched", "matched", "unmatched", "unmatched"],
        )
        self.assertEqual(
            [line["match_reason_code"] for line in lines],
            [
                "missing_borrower_and_application_narration",
                "missing_borrower_and_application_narration",
                "missing_borrower_and_application_narration",
                "exact_reference_amount_date_account",
                "ambiguous_borrower_or_application_narration",
                "missing_borrower_and_application_narration",
            ],
        )

    def test_statement_list_hides_out_of_scope_matches_counts_and_private_facts(self):
        from sfpcl_credit.configurations.modules.source_bank_governance import (
            resolve_source_bank_account,
        )
        from sfpcl_credit.loans.models import LoanAccount

        self.fixture.fixture.fixture.owner.fixture.fixture._grant(
            self.fixture.actor,
            "finance.bank_statement.import",
            "finance.bank_statement.match",
        )
        captured = self.fixture._capture(
            {
                **self.fixture._payload(),
                "amount_received": "47000.00",
                "received_date": "2026-12-13",
                "bank_reference_number": "UTR-LIST-SCOPE-001",
            },
            "statement-list-scope-receipt",
        )
        self.assertEqual(captured.status_code, 200, captured.content)
        content = (
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-13,2026-12-13,47000.00,Private "
            f"{self.fixture.account.loan_account_number},UTR-LIST-SCOPE-001,"
            f"{self.fixture.account.loan_account_number}\n"
        )
        imported = self.fixture.client.post(
            "/api/v1/bank-statement-imports/",
            data={
                "file": SimpleUploadedFile(
                    "private.csv", content.encode(), content_type="text/csv"
                ),
                "collection_bank_account_id": str(
                    resolve_source_bank_account().source_bank_account_id
                ),
            },
            HTTP_IDEMPOTENCY_KEY="statement-list-scope-import",
            **self.fixture.auth,
        )
        self.assertEqual(imported.status_code, 200, imported.content)
        serialized_import = str(imported.json())
        self.assertNotIn("collection_bank_account", serialized_import)
        self.assertNotIn("UTR-LIST-SCOPE-001", serialized_import)
        self.assertNotIn("Private", serialized_import)

        user_fixture = self.fixture.fixture.fixture.owner.fixture.fixture
        auth_fixture = self.fixture.fixture.fixture.owner.fixture
        reader = user_fixture._user("credit_manager", "Statement Scoped Reader")
        user_fixture._grant(reader, "finance.bank_statement.read")
        LoanAccount.objects.filter(pk=self.fixture.account.pk).update(
            loan_account_status="sanctioned"
        )
        response = self.fixture.client.get(
            "/api/v1/bank-statement-lines/?match_status=matched",
            **auth_fixture._auth(reader),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["data"], [])
        self.assertEqual(response.json()["pagination"]["total_count"], 0)

    def test_direct_capture_claims_only_exact_governed_statement_evidence(self):
        from sfpcl_credit.configurations.modules.source_bank_governance import (
            resolve_source_bank_account,
        )
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import BankStatementLine, Repayment

        self.fixture.fixture.fixture.owner.fixture.fixture._grant(
            self.fixture.actor,
            "finance.bank_statement.import",
            "finance.bank_statement.match",
        )
        content = (
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-16,2026-12-16,48000.00,Receipt "
            f"{self.fixture.account.loan_account_number},UTR-DIRECT-CLAIM-001,"
            f"{self.fixture.account.loan_account_number}\n"
        )
        imported = self.fixture.client.post(
            "/api/v1/bank-statement-imports/",
            data={
                "file": SimpleUploadedFile(
                    "direct-claim.csv", content.encode(), content_type="text/csv"
                ),
                "collection_bank_account_id": str(
                    resolve_source_bank_account().source_bank_account_id
                ),
            },
            HTTP_IDEMPOTENCY_KEY="statement-direct-claim-import",
            **self.fixture.auth,
        )
        self.assertEqual(imported.status_code, 200, imported.content)
        line_id = imported.json()["data"]["lines"][0]["bank_statement_line_id"]

        captured = self.fixture._capture(
            {
                **self.fixture._payload(),
                "amount_received": "48000.00",
                "received_date": "2026-12-16",
                "bank_reference_number": "UTR-DIRECT-CLAIM-001",
                "bank_statement_line_id": line_id,
            },
            "statement-direct-claim-receipt",
        )

        self.assertEqual(captured.status_code, 200, captured.content)
        repayment = Repayment.objects.get(
            pk=captured.json()["data"]["repayment_id"]
        )
        line = BankStatementLine.objects.get(pk=line_id)
        self.assertEqual(line.matched_repayment_id, repayment.pk)
        self.assertEqual(repayment.bank_statement_line_id, line.pk)
        self.assertEqual(repayment.statement_match_status, "matched_exact")
        self.assertEqual(
            AuditLog.objects.filter(
                action="bank_statement.line_claimed_for_direct_receipt"
            ).count(),
            1,
        )
