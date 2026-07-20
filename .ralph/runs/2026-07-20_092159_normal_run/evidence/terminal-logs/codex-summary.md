# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 6657224
Lines: 155235
SHA-256: cfc43e2211d2d6afbb0a81f93fe56f484d807d8ba571642479e5114ce1b98d08
Session ID: 019f7da7-3aa7-7851-9cd6-0c39fa05a29f
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+    InterestCapitalisationApiTests,
+)
+
+
+@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
+class InterestCapitalisationPostgreSQLAcceptanceTests(TransactionTestCase):
+    reset_sequences = True
+
+    def setUp(self):
+        fixture = InterestCapitalisationApiTests(
+            "test_may_first_finalisation_moves_principal_once_and_retains_intimation_chain"
+        )
+        fixture.setUp()
+        self.fixture = fixture
+
+    def test_concurrent_finalisation_retains_one_principal_and_ledger_movement(self):
+        barrier = Barrier(2)
+
+        def submit(index):
+            close_old_connections()
+            barrier.wait()
+            response = Client().post(
+                f"/api/v1/loan-accounts/{self.fixture.account.pk}/interest-capitalisations/",
+                data=json.dumps(
+                    {
+                        "financial_year": "FY2026-27",
+                        "capitalisation_date": "2027-05-01",
+                    }
+                ),
+                content_type="application/json",
+                HTTP_IDEMPOTENCY_KEY=f"postgres-interest-capitalisation-{index}",
+                **self.fixture.auth,
+            )
+            close_old_connections()
+            return response.status_code
+
+        with ThreadPoolExecutor(max_workers=2) as pool:
+            statuses = sorted(pool.map(submit, range(2)))
+
+        from sfpcl_credit.interest.models import (
+            InterestCapitalisation,
+            InterestCapitalisationLedgerEntry,
+        )
+
+        self.fixture.account.refresh_from_db()
+        self.assertEqual(statuses, [200, 409])
+        self.assertEqual(InterestCapitalisation.objects.count(), 1)
+        self.assertEqual(InterestCapitalisationLedgerEntry.objects.count(), 1)
+        self.assertEqual(str(self.fixture.account.principal_outstanding), "437000.00")
 
 
 @skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")

tokens used
299,238
Implemented slice `010H-interest-capitalisation-after-30-april` and marked it ready for independent validation.

Delivered:

- Zero-write capitalisation eligibility preview.
- Post-30-April atomic principal capitalisation derived exclusively from backend invoice truth.
- Immutable source-invoice, calculation-version, audit, and ledger evidence.
- Idempotency and unique loan/FY enforcement, including PostgreSQL contention acceptance.
- Official email queueing and hard-copy PDF generation with honest delivery status.
- Cutoff, paid/zero interest, caller-supplied money, duplicate/replay, permission, scope, missing configuration, and provider-failure coverage.
- Loan Account 360, ledger, and future principal-as-of projections now expose the revised principal.
- One additive database migration and updated API documentation.

Validation completed:

- 110 focused backend tests passed.
- 12 expected PostgreSQL-only skips under local SQLite.
- Django system check passed.
- Migration synchronization passed.
- Catalogue, API contract, communications, 010A, 010F, and 010G reverse-consumer tests passed.
- The exact one-test PostgreSQL contract collected successfully; Ralph’s independent gate will execute it twice against PostgreSQL.
- No frontend files or protected files were changed.
- No git add, commit, or push was performed.

Review artifacts are available in [review-packet.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_092159_normal_run/.ralph/runs/2026-07-20_092159_normal_run/review-packet.md) and [final-summary.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_092159_normal_run/.ralph/runs/2026-07-20_092159_normal_run/final-summary.md).
