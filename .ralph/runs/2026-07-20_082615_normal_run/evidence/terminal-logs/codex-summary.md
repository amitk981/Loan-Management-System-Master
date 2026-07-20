# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 10021329
Lines: 204835
SHA-256: 21d656e84b329d2e0ba8ff387bc7f992a5a0ffd0e6ea17d85e8f7328282754f5
Session ID: 019f7d74-261f-72f3-b831-a6f1c473945d
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

diff --git a/sfpcl_credit/tests/test_servicing_postgresql_acceptance.py b/sfpcl_credit/tests/test_servicing_postgresql_acceptance.py
index 7de24337ac47331d65bb886ef79afbeb888b4c25..04d970e8230b74ba525dfaa8af2a064aa94392dd
--- a/sfpcl_credit/tests/test_servicing_postgresql_acceptance.py
+++ b/sfpcl_credit/tests/test_servicing_postgresql_acceptance.py
@@ -17,6 +17,50 @@
     SubsidiaryDeductionReconciliationApiTests,
 )
 from sfpcl_credit.tests.test_interest_invoice_api import InterestInvoiceApiTests
+from sfpcl_credit.tests.test_interest_accrual_api import MonthlyInterestAccrualApiTests
+
+
+@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
+class MonthlyInterestAccrualPostgreSQLAcceptanceTests(TransactionTestCase):
+    reset_sequences = True
+
+    def setUp(self):
+        fixture = MonthlyInterestAccrualApiTests(
+            "test_single_month_uses_server_owned_snapshots_and_creates_pending_sap_obligation"
+        )
+        fixture.setUp()
+        self.fixture = fixture
+
+    def test_concurrent_same_month_retains_one_accrual_and_sap_obligation(self):
+        barrier = Barrier(2)
+
+        def submit(index):
+            close_old_connections()
+            barrier.wait()
+            response = Client().post(
+                f"/api/v1/loan-accounts/{self.fixture.account.pk}/accrual-entries/",
+                data=json.dumps({"accrual_month": "2026-07"}),
+                content_type="application/json",
+                HTTP_IDEMPOTENCY_KEY=f"postgres-interest-accrual-{index}",
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
+        from sfpcl_credit.interest.models import AccrualEntry, AccrualSapPostingObligation
+
+        self.assertEqual(statuses, [200, 409])
+        self.assertEqual(AccrualEntry.objects.count(), 1)
+        self.assertEqual(AccrualSapPostingObligation.objects.count(), 1)
+        self.assertEqual(InterestRateConsumptionSnapshot.objects.count(), 1)
+        self.assertEqual(
+            AuditLog.objects.filter(action="interest.accrual.generated").count(), 1
+        )
 
 
 @skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")

tokens used
344,433
Implemented slice `010G-monthly-interest-accrual` and marked the candidate ready for independent validation.

Delivered:

- Server-owned monthly accrual calculations using historical month-end principal, effective-rate, and calculation-version snapshots.
- Duplicate-safe single creation and bounded bulk generation with true zero-write dry runs.
- Immutable accrual, audit, rate-consumption, and pending SAP obligation records.
- Authorised, idempotent SAP posted/failed evidence capture without claiming external delivery.
- PostgreSQL same-month concurrency acceptance contract.
- One migration with uniqueness, monetary, status, and evidence-coherence constraints.
- Updated API contracts and recorded the full-month fail-closed policy as assumption A-147.

Validation:

- 48 focused and reverse-consumer tests passed; 8 expected PostgreSQL-only skips.
- Django system check passed.
- Migration synchronization passed.
- `git diff --check` passed.
- The exact PostgreSQL class collected one test locally; Ralph must execute it twice against PostgreSQL.
- No full backend suite or coverage run was duplicated—the orchestrator owns those authoritative gates.

Evidence and handoff are in [review-packet.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_082615_normal_run/.ralph/runs/2026-07-20_082615_normal_run/review-packet.md), [risk-assessment.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_082615_normal_run/.ralph/runs/2026-07-20_082615_normal_run/risk-assessment.md), and [test-evidence.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_082615_normal_run/.ralph/runs/2026-07-20_082615_normal_run/evidence/test-evidence.md). No commit, 
