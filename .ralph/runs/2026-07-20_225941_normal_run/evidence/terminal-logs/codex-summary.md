# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 13052403
Lines: 294033
SHA-256: 7c4cfc8f96d667a256de0723a77e08e3e5e7f71c64d4e9f4e963b56fec334858
Session ID: 019f8093-e50a-7af1-8c3d-22853991e0c4
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+        replay = next(
+            response.json()["data"]
+            for response in responses
+            if response.json()["data"].get("idempotency_replayed")
+        )
+        self.assertEqual(replay["original_response"], original)
+        fixture.account.refresh_from_db()
+        self.assertEqual(str(fixture.account.principal_outstanding), "437000.00")
+        self.assertEqual(InterestCapitalisation.objects.count(), 1)
+        self.assertEqual(InterestCapitalisationLedgerEntry.objects.count(), 1)
+
+    def test_changed_key_capitalisation_race_retains_one_reclassification(self):
+        from sfpcl_credit.interest.models import (
+            InterestCapitalisation,
+            InterestCapitalisationLedgerEntry,
+        )
+        from sfpcl_credit.tests.servicing_builders import (
+            build_interest_capitalisation_fixture,
+        )
+
+        fixture = build_interest_capitalisation_fixture()
+        responses = self._race(
+            lambda index: fixture.submit(
+                idempotency_key=f"policy-pg-capitalisation-changed-{index}"
+            )
+        )
+        self.assertEqual(sorted(response.status_code for response in responses), [200, 409])
+        fixture.account.refresh_from_db()
+        self.assertEqual(str(fixture.account.principal_outstanding), "437000.00")
+        self.assertEqual(InterestCapitalisation.objects.count(), 1)
+        self.assertEqual(InterestCapitalisationLedgerEntry.objects.count(), 1)
+
+    @staticmethod
+    def _race(submit):
+        barrier = Barrier(2)
+
+        def worker(index):
+            close_old_connections()
+            try:
+                barrier.wait(timeout=15)
+                return submit(index)
+            finally:
+                close_old_connections()
+
+        with ThreadPoolExecutor(max_workers=2) as pool:
+            return list(pool.map(worker, range(2)))
+
+
+@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
 class DpdSnapshotPostgreSQLAcceptanceTests(TransactionTestCase):
     reset_sequences = True
 

tokens used
485,704
Implemented slice `010H3-interest-policy-and-reclassification-integrity-closure` and prepared it for Ralph’s independent validation.

Delivered:

- Approved interest policies are immutable through instance, queryset, bulk, delete, and PostgreSQL raw-write paths.
- Monetary rounding mode, precision, and whole-decision boundary are explicit and retained with invoice/accrual evidence.
- Segmented interest is rounded once at the approved aggregate boundary.
- Capitalisation now reconciles invoice, account, schedule, payment, ledger, and principal truth exactly before making any changes.
- Account, schedule, ledger, and payment-owner mismatches are verified as zero-write failures.
- Exact-key and changed-key races retain one principal increment and one immutable ledger decision.
- Public servicing test builders and the required five-test PostgreSQL acceptance class were added.

Verification completed:

- Policy/invoice/accrual: 20 passed.
- Capitalisation: 14 passed.
- Reverse consumers: 51 passed, 14 expected SQLite skips.
- PostgreSQL acceptance: 5 passed twice.
- Django system check and migration drift check passed.
- Protected-file and whitespace audits passed.
- Required closure validator: `PASS` for one finding and all five acceptance IDs.

The final review result is exactly `Ready for independent validation` in [review-packet.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_225941_normal_run/.ralph/runs/2026-07-20_225941_normal_run/review-packet.md). Supporting details are in [final-summary.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_225941_normal_run/.ralph/runs/2026-07-20_225941_normal_run/final-summary.md) and [review-closure-evidence.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_225941_normal_run/.ral

No commit, staging-branch bookkeeping, or protected-file changes were performed; those remain with the Ralph orchestrator.
