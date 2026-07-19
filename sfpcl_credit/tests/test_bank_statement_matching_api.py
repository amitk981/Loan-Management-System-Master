import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings

@override_settings(DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-statement-tests-"))
class BankStatementMatchingApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_direct_repayment_posting_api import (
            DirectRepaymentPostingApiTests,
        )

        fixture = DirectRepaymentPostingApiTests(
            "test_valid_direct_receipt_and_exact_replay_create_one_pending_obligation"
        )
        fixture.setUp()
        self.fixture = fixture
        self.account = fixture.account
        self.actor = fixture.actor
        fixture.fixture.fixture.owner.fixture.fixture._grant(
            self.actor,
            "finance.bank_statement.read",
            "finance.bank_statement.import",
            "finance.bank_statement.match",
        )
        self.client = Client()
        self.auth = fixture.auth

    def test_exact_statement_evidence_matches_one_receipt_without_financial_mutation(self):
        from sfpcl_credit.loans.models import (
            LoanAccount,
            Repayment,
            RepaymentAllocation,
            RepaymentLedgerEntry,
            RepaymentSchedule,
        )

        receipt_payload = {
            **self.fixture._payload(),
            "amount_received": "125000.00",
            "received_date": "2026-12-04",
            "bank_reference_number": "UTR-STATEMENT-001",
        }
        captured = self.fixture._capture(receipt_payload, "statement-receipt-key")
        self.assertEqual(captured.status_code, 200, captured.content)
        repayment_id = captured.json()["data"]["repayment_id"]
        account_before = LoanAccount.objects.values().get(pk=self.account.pk)
        schedules_before = list(
            RepaymentSchedule.objects.filter(loan_account=self.account).values()
        )

        response = self._upload(
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-04,2026-12-04,125000.00,Receipt for {self.account.loan_account_number},UTR-STATEMENT-001,"
            f"{self.account.loan_account_number}\n",
            key="statement-import-001",
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["line_count"], 1)
        self.assertEqual(data["matched_count"], 1, data)
        self.assertEqual(data["exception_count"], 0)
        line = data["lines"][0]
        self.assertEqual(line["match_status"], "matched")
        self.assertEqual(line["matched_repayment_id"], repayment_id)
        self.assertEqual(line["match_reason_code"], "exact_reference_amount_date_account")

        repayment = Repayment.objects.get(pk=repayment_id)
        self.assertEqual(str(repayment.bank_statement_line_id), line["bank_statement_line_id"])
        self.assertEqual(repayment.allocation_status, "pending")
        self.assertEqual(RepaymentAllocation.objects.count(), 0)
        self.assertEqual(RepaymentLedgerEntry.objects.count(), 0)
        self.assertEqual(LoanAccount.objects.values().get(pk=self.account.pk), account_before)
        self.assertEqual(
            list(RepaymentSchedule.objects.filter(loan_account=self.account).values()),
            schedules_before,
        )

    def test_reconciliation_queue_lists_safe_unmatched_and_parse_exception_reasons(self):
        response = self._upload(
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-05,2026-12-05,125000.00,Private borrower narration,UNKNOWN-UTR,"
            f"{self.account.loan_account_number}\n"
            "not-a-date,2026-12-05,invalid,Malformed private row,BAD-ROW,LN-UNKNOWN\n",
            key="statement-queue-001",
        )
        self.assertEqual(response.status_code, 200, response.content)

        unmatched = self.client.get(
            "/api/v1/bank-statement-lines/?match_status=unmatched&page=1&page_size=20",
            **self.auth,
        )
        exceptions = self.client.get(
            "/api/v1/bank-statement-lines/?match_status=exception&page=1&page_size=20",
            **self.auth,
        )

        self.assertEqual(unmatched.status_code, 200, unmatched.content)
        self.assertEqual(exceptions.status_code, 200, exceptions.content)
        self.assertEqual(unmatched.json()["pagination"]["total_count"], 1)
        self.assertEqual(exceptions.json()["pagination"]["total_count"], 1)
        self.assertEqual(
            unmatched.json()["data"][0]["match_reason_code"],
            "no_exact_receipt_candidate",
        )
        self.assertEqual(exceptions.json()["data"][0]["match_reason_code"], "parse_failed")
        self.assertNotIn("narration", unmatched.json()["data"][0])
        self.assertNotIn("reference", unmatched.json()["data"][0])

    def test_duplicate_mismatch_and_missing_candidate_facts_never_fabricate_matches(self):
        captured = self.fixture._capture(
            {
                **self.fixture._payload(),
                "amount_received": "30000.00",
                "received_date": "2026-12-05",
                "bank_reference_number": "UTR-CANDIDATE-001",
            },
            "candidate-receipt",
        )
        repayment_id = captured.json()["data"]["repayment_id"]
        imported = self._upload(
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-05,2026-12-05,30000.00,Exact {self.account.loan_account_number},UTR-CANDIDATE-001,"
            f"{self.account.loan_account_number}\n"
            f"2026-12-05,2026-12-05,30000.00,Duplicate {self.account.loan_account_number},UTR-CANDIDATE-001,"
            f"{self.account.loan_account_number}\n"
            f"2026-12-05,2026-12-05,30001.00,Amount mismatch,UTR-CANDIDATE-001,"
            f"{self.account.loan_account_number}\n"
            "2026-12-05,2026-12-05,30000.00,Missing account,UTR-CANDIDATE-001,\n"
            f"2026-12-05,2026-12-05,30000.00,Missing reference,,"
            f"{self.account.loan_account_number}\n",
            key="candidate-matrix-import",
        ).json()["data"]

        self.assertEqual(imported["matched_count"], 1)
        self.assertEqual(imported["exception_count"], 1)
        self.assertEqual(imported["unmatched_count"], 3)
        self.assertEqual(
            [line["match_reason_code"] for line in imported["lines"]],
            [
                "exact_reference_amount_date_account",
                "counterpart_already_matched",
                "no_exact_receipt_candidate",
                "missing_loan_reference",
                "missing_reference",
            ],
        )
        self.assertEqual(imported["lines"][0]["matched_repayment_id"], repayment_id)
        self.assertTrue(
            all(
                line["matched_repayment_id"] is None
                for line in imported["lines"][1:]
            )
        )

    def test_exact_bank_facts_without_borrower_or_application_narration_remain_unmatched(self):
        from sfpcl_credit.loans.models import Repayment

        captured = self.fixture._capture(
            {
                **self.fixture._payload(),
                "amount_received": "35000.00",
                "received_date": "2026-12-11",
                "bank_reference_number": "UTR-NARRATION-001",
            },
            "narration-receipt",
        )
        repayment_id = captured.json()["data"]["repayment_id"]
        imported = self._upload(
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-11,2026-12-11,35000.00,Generic incoming credit,UTR-NARRATION-001,"
            f"{self.account.loan_account_number}\n",
            key="narration-import",
        ).json()["data"]

        self.assertEqual(imported["matched_count"], 0)
        self.assertEqual(imported["unmatched_count"], 1)
        self.assertEqual(
            imported["lines"][0]["match_reason_code"],
            "missing_borrower_or_application_narration",
        )
        repayment = Repayment.objects.get(pk=repayment_id)
        self.assertIsNone(repayment.bank_statement_line_id)
        self.assertEqual(repayment.statement_match_status, "not_linked")

    def test_manual_match_requires_reason_and_one_receipt_cannot_be_consumed_twice(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import Repayment

        captured = self.fixture._capture(
            {
                **self.fixture._payload(),
                "amount_received": "75000.00",
                "received_date": "2026-12-06",
                "bank_reference_number": "UTR-MANUAL-RECEIPT",
            },
            "manual-match-receipt",
        )
        repayment_id = captured.json()["data"]["repayment_id"]
        imported = self._upload(
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-06,2026-12-06,75000.00,Manual review A,UNKNOWN-A,"
            f"{self.account.loan_account_number}\n"
            f"2026-12-06,2026-12-06,75000.00,Manual review B,UNKNOWN-B,"
            f"{self.account.loan_account_number}\n",
            key="manual-match-import",
        ).json()["data"]
        first_line_id, second_line_id = [
            line["bank_statement_line_id"] for line in imported["lines"]
        ]

        blank_reason = self._match(first_line_id, repayment_id, " ")
        matched = self._match(
            first_line_id,
            repayment_id,
            "Reviewed the retained bank advice and receipt identifiers.",
        )
        duplicate = self._match(
            second_line_id,
            repayment_id,
            "Attempting to reuse the same receipt must fail.",
        )

        self.assertEqual(blank_reason.status_code, 400, blank_reason.content)
        self.assertEqual(matched.status_code, 200, matched.content)
        self.assertEqual(duplicate.status_code, 409, duplicate.content)
        data = matched.json()["data"]
        self.assertEqual(data["match_status"], "matched")
        self.assertEqual(data["match_reason_code"], "authorised_manual_evidence_match")
        self.assertEqual(
            data["repayment_evidence"],
            {
                "repayment_id": repayment_id,
                "bank_statement_line_id": first_line_id,
                "statement_match_status": "manual_match_exception",
                "allocation_status": "pending",
            },
        )
        repayment = Repayment.objects.get(pk=repayment_id)
        self.assertEqual(str(repayment.bank_statement_line_id), first_line_id)
        self.assertEqual(repayment.statement_match_status, "manual_match_exception")
        self.assertEqual(repayment.allocation_status, "pending")
        audit = AuditLog.objects.get(action="bank_statement.line_manually_matched")
        self.assertEqual(audit.actor_user_id, self.actor.pk)
        self.assertNotIn("Reviewed the retained", str(audit.new_value_json))

    def test_authorised_exception_action_retains_safe_reason_and_audit(self):
        import json

        from sfpcl_credit.identity.models import AuditLog

        imported = self._upload(
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-07,2026-12-07,50000.00,Conflicting private detail,UNKNOWN-CONFLICT,"
            f"{self.account.loan_account_number}\n",
            key="statement-exception-001",
        ).json()["data"]
        line_id = imported["lines"][0]["bank_statement_line_id"]

        response = self.client.post(
            f"/api/v1/bank-statement-lines/{line_id}/exception/",
            data=json.dumps(
                {
                    "reason_code": "evidence_conflict",
                    "reason": "The retained advice conflicts with the captured receipt.",
                }
            ),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["data"]["match_status"], "exception")
        self.assertEqual(
            response.json()["data"]["match_reason_code"], "evidence_conflict"
        )
        audit = AuditLog.objects.get(action="bank_statement.line_exception_recorded")
        self.assertEqual(audit.actor_user_id, self.actor.pk)
        self.assertNotIn("retained advice", str(audit.new_value_json))

    def test_import_replay_file_validation_and_permission_fail_closed_without_duplicates(self):
        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import BankStatementImport, BankStatementLine

        document_count_before = DocumentFile.objects.count()
        content = (
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-08,2026-12-08,25000.00,Unknown receipt,UNKNOWN-REPLAY,"
            f"{self.account.loan_account_number}\n"
        )
        first = self._upload(content, key="stable-statement-key")
        replay = self._upload(content, key="stable-statement-key")
        same_file_new_key = self._upload(content, key="different-statement-key")
        changed_same_key = self._upload(
            content.replace("25000.00", "25001.00"), key="stable-statement-key"
        )
        forbidden_file = self._upload(
            content,
            key="forbidden-file-key",
            name="statement.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(same_file_new_key.status_code, 200, same_file_new_key.content)
        self.assertTrue(replay.json()["data"]["idempotency_replayed"])
        self.assertTrue(same_file_new_key.json()["data"]["idempotency_replayed"])
        self.assertEqual(changed_same_key.status_code, 409, changed_same_key.content)
        self.assertEqual(forbidden_file.status_code, 400, forbidden_file.content)
        self.assertEqual(BankStatementImport.objects.count(), 1)
        self.assertEqual(BankStatementLine.objects.count(), 1)
        self.assertEqual(DocumentFile.objects.count(), document_count_before + 1)
        self.assertEqual(
            AuditLog.objects.filter(action="bank_statement.imported").count(), 1
        )

        user_factory = self.fixture.fixture.fixture.owner.fixture.fixture
        auth_factory = self.fixture.fixture.fixture.owner.fixture
        unauthorized = user_factory._user("field_officer", "Statement Unauthorized")
        denied = self.client.get(
            "/api/v1/bank-statement-lines/", **auth_factory._auth(unauthorized)
        )
        anonymous = self.client.get("/api/v1/bank-statement-lines/")
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(anonymous.status_code, 401, anonymous.content)
        self.assertEqual(BankStatementImport.objects.count(), 1)

    def test_manual_match_hides_out_of_scope_receipt_and_rejects_unauthorised_actor(self):
        import json

        from sfpcl_credit.loans.models import BankStatementLine, LoanAccount

        captured = self.fixture._capture(
            {
                **self.fixture._payload(),
                "amount_received": "45000.00",
                "received_date": "2026-12-10",
                "bank_reference_number": "UTR-SCOPE-001",
            },
            "scope-receipt",
        )
        repayment_id = captured.json()["data"]["repayment_id"]
        imported = self._upload(
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-10,2026-12-10,45000.00,Scoped review,UNKNOWN-SCOPE,"
            f"{self.account.loan_account_number}\n",
            key="scope-import",
        ).json()["data"]
        line_id = imported["lines"][0]["bank_statement_line_id"]
        user_factory = self.fixture.fixture.fixture.owner.fixture.fixture
        auth_factory = self.fixture.fixture.fixture.owner.fixture
        credit_actor = user_factory._user("credit_manager", "Statement Credit Scope")
        user_factory._grant(
            credit_actor,
            "finance.bank_statement.read",
            "finance.bank_statement.import",
            "finance.bank_statement.match",
        )
        unauthorised = user_factory._user("field_officer", "Statement Unauthorised")
        payload = json.dumps(
            {"repayment_id": repayment_id, "reason": "Scoped manual review."}
        )

        LoanAccount.objects.filter(pk=self.account.pk).update(
            loan_account_status="sanctioned"
        )
        hidden = self.client.post(
            f"/api/v1/bank-statement-lines/{line_id}/match/",
            data=payload,
            content_type="application/json",
            **auth_factory._auth(credit_actor),
        )
        denied = self.client.post(
            f"/api/v1/bank-statement-lines/{line_id}/match/",
            data=payload,
            content_type="application/json",
            **auth_factory._auth(unauthorised),
        )

        self.assertEqual(hidden.status_code, 404, hidden.content)
        self.assertEqual(denied.status_code, 403, denied.content)
        line = BankStatementLine.objects.get(pk=line_id)
        self.assertEqual(line.match_status, "unmatched")
        self.assertIsNone(line.matched_repayment_id)

    def _match(self, line_id, repayment_id, reason):
        import json

        return self.client.post(
            f"/api/v1/bank-statement-lines/{line_id}/match/",
            data=json.dumps({"repayment_id": repayment_id, "reason": reason}),
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-bank-statement-match-001",
            **self.auth,
        )

    def _upload(self, content, *, key, name="statement.csv", content_type="text/csv"):
        return self.client.post(
            "/api/v1/bank-statement-imports/",
            data={
                "file": SimpleUploadedFile(name, content.encode(), content_type=content_type),
                "sfpcl_bank_account": "SFPCL-COLLECTION-001",
            },
            HTTP_IDEMPOTENCY_KEY=key,
            HTTP_X_REQUEST_ID="req-bank-statement-001",
            **self.auth,
        )
