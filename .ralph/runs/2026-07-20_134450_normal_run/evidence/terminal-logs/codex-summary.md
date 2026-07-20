# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 18839440
Lines: 429679
SHA-256: 78743934e30fdc4868d8ca45ff0552ad224fbf08c79e03c1cb5e6afd78965a35
Session ID: 019f7e97-deaa-7e81-bea9-3841fa864c15
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+        first = fixture._capitalise("owner-capitalisation-exact")
+        from sfpcl_credit.communications.models import CommunicationDeliveryJob
+        from sfpcl_credit.interest.models import (
+            InterestCapitalisation,
+            InterestCapitalisationHardCopyTask,
+        )
+
+        row = InterestCapitalisation.objects.get()
+        job = CommunicationDeliveryJob.objects.get(
+            communication_id=row.borrower_intimation_email_id
+        )
+        job.status = CommunicationDeliveryJob.STATUS_FAILED
+        job.attempts = job.max_attempts
+        job.last_failure_code = "provider_rejected"
+        job.save(update_fields=["status", "attempts", "last_failure_code"])
+        replay = fixture._capitalise("owner-capitalisation-exact")
+        ledger = Client().get(
+            f"/api/v1/loan-accounts/{fixture.account.pk}/ledger/", **fixture.auth
+        )
+
+        self.assertEqual(replay.json()["data"]["original_response"], first.json()["data"])
+        self.assertEqual(ledger.status_code, 200, ledger.content)
+        self.assertEqual(ledger.json()["data"][-1]["transaction_type"], "interest_capitalisation")
+        self.assertEqual(InterestCapitalisationHardCopyTask.objects.count(), 1)
+
+    @staticmethod
+    def _invoice_fixture():
+        fixture = InterestInvoiceApiTests(
+            "test_generation_uses_server_owned_fy_truth_and_leaves_balances_unchanged"
+        )
+        fixture.setUp()
+        return fixture
+
+    @staticmethod
+    def _race(submit):
+        barrier = Barrier(2)
+
+        def worker(index):
+            close_old_connections()
+            barrier.wait()
+            response = submit(index)
+            close_old_connections()
+            return response.status_code
+
+        with ThreadPoolExecutor(max_workers=2) as pool:
+            return sorted(pool.map(worker, range(2)))
+
+
+@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
 class DirectRepaymentPostingPostgreSQLAcceptanceTests(TransactionTestCase):
     reset_sequences = True
 

tokens used
670,217
Implemented selected slice `010H2-interest-calculation-payment-and-replay-owner-closure` and marked it ready for independent validation.

Delivered:

- Shared as-of interest calculation with retained principal/rate segmentation, including leap-day boundaries.
- Exact schedule-application payment ownership and 30 April cutoff handling.
- Tax, fees, charges, unrelated payments, and post-cutoff payments excluded from capitalised principal.
- Atomic principal/interest/schedule/ledger reclassification with email, document, audit, and hard-copy evidence.
- Byte-stable replay snapshots for invoice generation/issuance, accrual generation/SAP posting, and capitalisation.
- Immutable consumed configuration and terminal financial evidence.
- One additive migration.
- Exact five-test `InterestAccountingOwnerPostgreSQLAcceptanceTests` class.

Verification passed:

- PostgreSQL acceptance: 5/5 tests, twice, with `EXIT_STATUS=0`.
- Focused reverse-consumer suite: 44/44 tests.
- Verbose acceptance matrix: 6/6 tests.
- Django system check and migration drift check.
- `git diff --check`.
- Required RED/GREEN and architecture-closure evidence retained.

Artifacts are in [.ralph/runs/2026-07-20_134450_normal_run](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_134450_normal_run/.ralph/runs/2026-07-20_134450_normal_run). The TDD workflow materially shaped the implementation: each financial boundary was driven by a public failing probe before its corresponding correction.

No commit, staging update, merge, push, slice-status transition, or orchestrator-owned bookkeeping was performed. The authoritative complete backend coverage gate remains for the Ralph orchestrator.
