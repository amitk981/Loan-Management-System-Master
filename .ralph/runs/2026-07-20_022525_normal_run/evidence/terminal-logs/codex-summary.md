# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 7722827
Lines: 170738
SHA-256: 43c237ad9901f0a283edeb982e872da5a12c7542af5691e147561b064b882c13
Session ID: 019f7c29-cdc6-72b1-8184-156f0f2d2581
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+
+        self.fixture.fixture.fixture.owner.fixture.fixture._grant(
+            self.fixture.actor,
+            "finance.bank_statement.import",
+            "finance.bank_statement.match",
+        )
+        content = (
+            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
+            f"2026-12-16,2026-12-16,48000.00,Receipt "
+            f"{self.fixture.account.loan_account_number},UTR-DIRECT-CLAIM-001,"
+            f"{self.fixture.account.loan_account_number}\n"
+        )
+        imported = self.fixture.client.post(
+            "/api/v1/bank-statement-imports/",
+            data={
+                "file": SimpleUploadedFile(
+                    "direct-claim.csv", content.encode(), content_type="text/csv"
+                ),
+                "collection_bank_account_id": str(
+                    resolve_source_bank_account().source_bank_account_id
+                ),
+            },
+            HTTP_IDEMPOTENCY_KEY="statement-direct-claim-import",
+            **self.fixture.auth,
+        )
+        self.assertEqual(imported.status_code, 200, imported.content)
+        line_id = imported.json()["data"]["lines"][0]["bank_statement_line_id"]
+
+        captured = self.fixture._capture(
+            {
+                **self.fixture._payload(),
+                "amount_received": "48000.00",
+                "received_date": "2026-12-16",
+                "bank_reference_number": "UTR-DIRECT-CLAIM-001",
+                "bank_statement_line_id": line_id,
+            },
+            "statement-direct-claim-receipt",
+        )
+
+        self.assertEqual(captured.status_code, 200, captured.content)
+        repayment = Repayment.objects.get(
+            pk=captured.json()["data"]["repayment_id"]
+        )
+        line = BankStatementLine.objects.get(pk=line_id)
+        self.assertEqual(line.matched_repayment_id, repayment.pk)
+        self.assertEqual(repayment.bank_statement_line_id, line.pk)
+        self.assertEqual(repayment.statement_match_status, "matched_exact")
+        self.assertEqual(
+            AuditLog.objects.filter(
+                action="bank_statement.line_claimed_for_direct_receipt"
+            ).count(),
+            1,
+        )

tokens used
322,350
Implemented slice `010D2-statement-evidence-owner-and-scope-closure` and marked it ready for independent validation.

Key outcomes:

- `BankStatementLine.matched_repayment` is now the sole persisted statement-to-receipt relationship owner.
- Receipt statement IDs/statuses are derived projections; orphan or contradictory UUID truth is no longer writable.
- Legacy coherent, orphaned, incomplete, and contradictory links have deterministic, ownership-safe migration behavior.
- Import, automatic match, manual match, direct capture, exception decisions, lists, and counts enforce permission and loan-object scope.
- Subsidiary matching now covers borrower-only, application-only, account-only, both-present, ambiguous, and missing narration.
- Collection accounts use the centrally governed opaque bank-account UUID; unmapped legacy labels are encrypted.
- Four declared PostgreSQL race tests were added and collect under the exact required class.

Local validation passed:

- 34 focused/reverse-consumer tests, with four expected PostgreSQL skips.
- Six final owner/scope/source/privacy tests.
- Forward/backward migration executor test.
- Django system check and migration-sync check.
- Frontend lint, typecheck, all 355 tests, and production build.
- Protected-path and diff checks.

The sandbox could not execute PostgreSQL races, and the complete backend coverage suite was intentionally left to Ralph’s independent validator.

Artifacts: [review-packet.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_022525_normal_run/.ralph/runs/2026-07-20_022525_normal_run/review-packet.md), [review-closure-evidence.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_022525_normal_run/.ralph/runs/2026-07-20_022525_normal_run/review-closure-evidence.md), and [final-summary.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_022525_normal_run/.ralph/runs/2026-07-20_022525_normal_run/final-summary.md).
