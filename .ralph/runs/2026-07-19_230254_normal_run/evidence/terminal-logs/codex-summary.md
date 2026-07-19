# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 5236889
Lines: 102737
SHA-256: ff8cf1fbf50fc1b0b5f9514aa7fcae14e1f42c8b96dec53a8b388b13e1e68fa2
Session ID: 019f7b70-7e0d-7b60-9a74-829a8280d018
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+
+    def setUp(self):
+        fixture = RepaymentAllocationApiTests(
+            "test_partial_receipt_reduces_principal_and_appends_immutable_evidence"
+        )
+        fixture.setUp()
+        self.fixture = fixture
+        captured = fixture.fixture._capture(
+            fixture.fixture._payload(), "postgres-allocation-receipt"
+        )
+        self.repayment_id = captured.json()["data"]["repayment_id"]
+        self.url = f"/api/v1/repayments/{self.repayment_id}/allocate/"
+
+    def test_five_concurrent_allocations_retain_one_balance_transition_and_ledger_row(self):
+        barrier = Barrier(5)
+
+        def submit(_):
+            close_old_connections()
+            barrier.wait()
+            response = Client().post(
+                self.url,
+                data=json.dumps(
+                    {
+                        "allocation_rule": "principal_first",
+                        "remarks": "Concurrent allocation under the approved SOP.",
+                    }
+                ),
+                content_type="application/json",
+                **self.fixture.auth,
+            )
+            close_old_connections()
+            return response.status_code
+
+        with ThreadPoolExecutor(max_workers=5) as pool:
+            statuses = sorted(pool.map(submit, range(5)))
+
+        from sfpcl_credit.identity.models import AuditLog
+        from sfpcl_credit.loans.models import (
+            LoanAccount,
+            RepaymentAllocation,
+            RepaymentLedgerEntry,
+        )
+
+        self.assertEqual(statuses, [200, 200, 200, 200, 200])
+        account = LoanAccount.objects.get(pk=self.fixture.account.pk)
+        self.assertEqual(str(account.principal_outstanding), "300000.00")
+        self.assertEqual(str(account.total_outstanding), "300000.00")
+        self.assertEqual(RepaymentAllocation.objects.count(), 1)
+        self.assertEqual(RepaymentLedgerEntry.objects.count(), 1)
+        self.assertEqual(AuditLog.objects.filter(action="repayment.allocated").count(), 1)

tokens used
232,373
Implemented slice `010C-principal-first-allocation` and marked it ready for independent validation.

Key outcomes:

- Added atomic, idempotent `RepaymentAllocator` with principal-first allocation.
- Added `POST /api/v1/repayments/{repayment_id}/allocate/`.
- Updates account and repayment-schedule balances under row locks.
- Retains excess and unconfigured-charge amounts as explicit exceptions.
- Added immutable allocation, audit, and repayment-ledger evidence.
- Added database constraints for balance arithmetic, duplicate prevention, non-negative values, schedule overpayment, and prohibited charge allocation.
- Extended the 010A ledger without modifying the canonical Epic 009 disbursement row.
- Added the declared five-request PostgreSQL contention test.
- Updated API contracts and recorded schedule-ordering assumption A-139.

Verification:

- 6 allocation tests passed.
- 15 Epic 010A/010B reverse-consumer tests passed.
- 2 Epic 009 opening-balance regressions passed.
- Django system check passed.
- Migration synchronization passed.
- `git diff --check` passed.
- PostgreSQL test collected exactly once and skipped locally on SQLite as expected; Ralph will execute it twice on PostgreSQL.
- No frontend files or protected files were changed.
- No commit/add/push command was run.

The completed handoff is in [review-packet.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_230254_normal_run/.ralph/runs/2026-07-19_230254_normal_run/review-packet.md), with evidence under the run’s `evidence/` directory.
