# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 5407509
Lines: 115112
SHA-256: bf5728770eefbbdd7b57035d0f2d230ba70ef38b6761dbd396c8e436f9c391f8
Session ID: 019f7d2a-10c9-7bd1-813d-5d4b8c7fed73
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

index acc4e5cdf2f29978f76f7f7d69157e942b81fe94..7de24337ac47331d65bb886ef79afbeb888b4c25
--- a/sfpcl_credit/tests/test_servicing_postgresql_acceptance.py
+++ b/sfpcl_credit/tests/test_servicing_postgresql_acceptance.py
@@ -16,6 +16,49 @@
 from sfpcl_credit.tests.test_subsidiary_deduction_reconciliation_api import (
     SubsidiaryDeductionReconciliationApiTests,
 )
+from sfpcl_credit.tests.test_interest_invoice_api import InterestInvoiceApiTests
+
+
+@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
+class InterestInvoicePostgreSQLAcceptanceTests(TransactionTestCase):
+    reset_sequences = True
+
+    def setUp(self):
+        fixture = InterestInvoiceApiTests(
+            "test_generation_uses_server_owned_fy_truth_and_leaves_balances_unchanged"
+        )
+        fixture.setUp()
+        self.fixture = fixture
+
+    def test_concurrent_same_period_retains_one_immutable_invoice(self):
+        barrier = Barrier(2)
+
+        def submit(index):
+            close_old_connections()
+            barrier.wait()
+            response = Client().post(
+                f"/api/v1/loan-accounts/{self.fixture.account.pk}/interest-invoices/",
+                data=json.dumps({"financial_year": "FY2026-27"}),
+                content_type="application/json",
+                HTTP_IDEMPOTENCY_KEY=f"postgres-interest-invoice-{index}",
+                **self.fixture.auth,
+            )
+            close_old_connections()
+            return response.status_code
+
+        with ThreadPoolExecutor(max_workers=2) as pool:
+            statuses = sorted(pool.map(submit, range(2)))
+
+        from sfpcl_credit.configurations.models import InterestRateConsumptionSnapshot
+        from sfpcl_credit.identity.models import AuditLog
+        from sfpcl_credit.interest.models import InterestInvoice
+
+        self.assertEqual(statuses, [200, 409])
+        self.assertEqual(InterestInvoice.objects.count(), 1)
+        self.assertEqual(InterestRateConsumptionSnapshot.objects.count(), 1)
+        self.assertEqual(
+            AuditLog.objects.filter(action="interest.invoice.generated").count(), 1
+        )
 
 
 @skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")

tokens used
264,458
Implemented slice `010F-interest-invoice-generation` and marked the review packet `Ready for independent validation`.

Delivered:

- Backend-owned annual interest calculation from frozen loan, rate, and accounting configuration.
- Immutable invoice, calculation, rate, actor, and audit snapshots.
- Exact idempotency replay and loan/period duplicate protection.
- Scoped generate, portfolio/nested list, and issue endpoints.
- Configurable invoice ownership with fail-closed accounting configuration.
- Deterministic PDF generation and retained communication/job evidence.
- PostgreSQL same-period concurrency acceptance contract.
- Updated API contracts and assumption A-146.
- Complete Ralph execution plan, risk assessment, evidence index, review packet, and final summary.

Validation completed:

- 6 interest-invoice tests passed.
- Focused interest, communications, and servicing reverse-consumer run passed: 7 passed, 1 PostgreSQL-only test skipped locally.
- Django system check passed.
- Migration synchronization passed.
- Compilation and diff hygiene passed.
- No frontend, dependency, protected-file, or source-document changes were made.

The orchestrator can now run independent full coverage and the declared PostgreSQL race twice.
