# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 6385730
Lines: 139005
SHA-256: fc637a29e54816ca029dcca65fd829b56efd94b4a826170e2d95a6712d19f55e
Session ID: 019f8102-b6b6-76d0-b61d-c69f318d0a46
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+
+        self.assertEqual(sorted(self._race(submit)), [200, 200])
+        self.assertEqual(DpdStatus.objects.count(), 3)
+        for account in accounts:
+            account.refresh_from_db()
+            self.assertEqual(
+                DpdStatus.objects.get(pk=account.current_dpd_status_id).loan_account_id,
+                account.pk,
+            )
+
+    def test_failed_policy_race_leaves_history_and_pointer_empty(self):
+        from datetime import date
+
+        from sfpcl_credit.monitoring.models import DpdOperationalBucketScheme, DpdStatus
+
+        for version in ("DPD-PG-OVERLAP-1", "DPD-PG-OVERLAP-2"):
+            DpdOperationalBucketScheme.objects.create(
+                version=version,
+                effective_from=date(2026, 1, 1),
+            )
+
+        self.assertEqual(
+            sorted(self._race(lambda _: self._post("2026-07-01"))),
+            [409, 409],
+        )
+        self.assertEqual(DpdStatus.objects.count(), 0)
+        self.fixture.account.refresh_from_db()
+        self.assertIsNone(self.fixture.account.current_dpd_status_id)
+
+    def _post(self, as_of_date):
+        return Client().post(
+            f"/api/v1/loan-accounts/{self.fixture.account.pk}/dpd-status/calculate/",
+            data=json.dumps({"as_of_date": as_of_date}),
+            content_type="application/json",
+            **self.fixture.auth,
+        ).status_code
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
 
 @skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
 class ReminderQueuePostgreSQLAcceptanceTests(TransactionTestCase):

tokens used
341,438
Implemented slice `010I2-dpd-pointer-and-policy-integrity-closure` and left it ready for independent Ralph validation.

Key outcomes:

- Replaced the unbound current-DPD UUID with a protected same-loan snapshot relationship.
- Added immediate PostgreSQL and SQLite guards against dangling, cross-loan, bulk, queryset, instance, direct-SQL, and deletion integrity violations.
- Added a validating migration/backfill that preserves DPD values while freezing legacy policy provenance.
- Added a locked public loan-owner decision interface for schedule, ledger/allocation, permission, and scope truth.
- Frozen SOP conventions, operational policy versions/bounds, and calculation inputs now drive historical replay.
- Added the exact five-test PostgreSQL acceptance class.

Verification completed:

- Focused DPD and reminder reverse-consumer suite: 22 tests passed.
- PostgreSQL acceptance: exactly 5 tests passed twice, with no skips.
- Django check and migration-state check passed.
- Semantic closure validator: `PASS` for 1 finding and all 5 acceptance IDs.
- `review-packet.md` Result is exactly `Ready for independent validation`.
- No protected files, source documents, frontend code, or unrelated slices were modified.
- No git add, commit, or push was attempted.

Evidence and handoff are in the [review packet](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_010045_normal_run/.ralph/runs/2026-07-21_010045_normal_run/review-packet.md) and [closure evidence](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_010045_normal_run/.ralph/runs/2026-07-21_010045_normal_run/review-closure-evidence.md). The orchestrator can now run the authoritative complete backend coverage and global gates.
