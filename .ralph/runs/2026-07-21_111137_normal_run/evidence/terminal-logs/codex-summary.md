# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 20441672
Lines: 330465
SHA-256: 32789b5ea77419ca7bd2a38ac3edeb9917d101d838344344bcf0376455c8821d
Session ID: 019f8332-1ed9-7870-b88a-10468e5ca1eb
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+            "?page=2",
+            "?page_size=101",
+            "?unknown=value",
+        ):
+            with self.subTest(query=query):
+                self.assertEqual(
+                    self.client.get(f"{url}{query}", **self.auth).status_code, 400
+                )
+
+
+class ServicingSubsidiaryReadProjectionTests(TestCase):
+    def setUp(self):
+        from sfpcl_credit.tests.test_subsidiary_deduction_reconciliation_api import (
+            SubsidiaryDeductionReconciliationApiTests,
+        )
+
+        fixture = SubsidiaryDeductionReconciliationApiTests(
+            "test_verified_agreement_allows_subsidiary_deduction_capture"
+        )
+        fixture.setUp()
+        self.fixture = fixture
+        self.account = fixture.account
+        self.client = Client()
+        self.auth = fixture.auth
+
+    def test_lists_retained_subsidiary_reconciliation_without_local_policy(self):
+        agreement = self.fixture._verified_tri_party_agreement()
+        captured = self.fixture._capture(
+            self.fixture._payload(), "frontend-read-subsidiary"
+        )
+        repayment_id = captured.json()["data"]["repayment_id"]
+
+        response = self.client.get(
+            f"/api/v1/loan-accounts/{self.account.pk}/repayments/?page=1&page_size=20",
+            **self.auth,
+        )
+
+        self.assertEqual(response.status_code, 200, response.content)
+        row = response.json()["data"][0]
+        self.assertEqual(row["repayment_id"], repayment_id)
+        self.assertEqual(row["amount_received"], "75000.00")
+        self.assertIsNone(row["allocation"])
+        self.assertEqual(
+            row["subsidiary_reconciliation"],
+            {
+                "subsidiary_company_id": str(self.fixture.subsidiary_company_id),
+                "produce_payment_reference": "PRODUCE-PAY-001",
+                "transfer_reference": "SUB-TRANSFER-001",
+                "tri_party_agreement_id": str(agreement.pk),
+                "reconciliation_status": "pending_statement",
+                "treasury_verification_status": "pending",
+            },
+        )

tokens used
683,968
Implemented slice `010MA-servicing-account-and-repayment-frontend-wiring` and marked it **Ready for independent validation**.

Delivered:

- Canonical Loan Account 360 schedule and ledger wiring with deterministic pagination.
- Governed direct repayment capture, SAP posting, principal-first allocation, stable idempotency keys, replay protection, and canonical refresh.
- Independent bank-statement exception/unmatched queues and subsidiary reconciliation views.
- Narrow scoped repayment read projection with retained allocation, SAP, statement, and subsidiary evidence.
- Source-role plus permission enforcement, stale-response protection, and precision-safe Money rendering.
- Removal of mock financial data from all three owned production surfaces.
- Exact two-scenario trusted-browser specification and deterministic real-auth permissions.

Validation completed:

- Frontend: **47 test files, 378 tests passed**
- Focused backend repayment suite: **28 tests passed**
- Backend projection tests: **3 passed**
- Typecheck, lint, production build, Django checks, migration drift, browser collection, and static audits: **passed**
- Independent standards/spec review: all findings corrected; final re-review found no remaining issue or regression
- Protected paths remained untouched; no dependencies, migrations, or git operations were introduced

Local Chromium aborted at sandbox launch with `SIGABRT` before executing either browser test. No screenshots were fabricated. Ralph’s out-of-sandbox twice-run browser contract remains the authoritative screenshot gate.

Artifacts are complete in [.ralph/runs/2026-07-21_111137_normal_run](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_111137_normal_run/.ralph/runs/2026-07-21_111137_normal_run), including the execution plan, risk assessment, evidence logs, review packet, and final summary.
