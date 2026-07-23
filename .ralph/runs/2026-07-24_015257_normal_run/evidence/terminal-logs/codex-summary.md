# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 6380862
Lines: 152677
SHA-256: d370a744181c4cb13fc7a5fe87cbcc6115942907ea6eed6e1ef2a48ef4cb0f52
Session ID: 019f90a5-827b-7e63-af59-4422595dbba0
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+    def test_credit_and_exception_reports_reuse_owner_registers_and_filters(self):
+        auth = self.fixture._auth(self.fixture.cfo)
+
+        sanction = get_with_query_bound(
+            self,
+            self.client,
+            (
+                "/api/v1/reports/credit-sanction/"
+                "?financial_year=FY2026-27&decision=rejected"
+            ),
+            auth,
+        )
+        exception = get_with_query_bound(
+            self,
+            self.client,
+            (
+                "/api/v1/reports/exception/"
+                "?status=pending&exception_type=exceeds_loan_limit"
+            ),
+            auth,
+        )
+
+        self.assertEqual(sanction.status_code, 200, sanction.content)
+        self.assertEqual(exception.status_code, 200, exception.content)
+        self.assertEqual(sanction.json()["pagination"]["total_count"], 1)
+        self.assertEqual(
+            sanction.json()["pagination"]["totals"],
+            {"sanctioned_amount": "0.00"},
+        )
+        self.assertEqual(
+            sanction.json()["data"][0]["credit_sanction_register_entry_id"],
+            str(self.sanction_entry.pk),
+        )
+        self.assertEqual(exception.json()["pagination"]["total_count"], 1)
+        self.assertEqual(
+            exception.json()["data"][0]["exception_register_entry_id"],
+            str(self.exception_entry.pk),
+        )
+        assert_validation_error(
+            self,
+            self.client.get(
+                "/api/v1/reports/credit-sanction/?decision=unknown",
+                **auth,
+            ),
+            "decision",
+        )
+        assert_validation_error(
+            self,
+            self.client.get(
+                "/api/v1/reports/exception/?exception_type=unknown",
+                **auth,
+            ),
+            "exception_type",
+        )

tokens used
347,722
Implemented slice `012A2-finance-and-servicing-report-catalogue` and marked it ready for independent validation.

Delivered:

- Registered all nine required report codes.
- Added governed selectors for Credit Sanction, Exception, Security Custody, SAP Pending, Disbursement, Repayment, Interest Invoice, Interest Accrual, and CFO Quarterly MIS.
- Reused canonical owner projections, permissions, and object scope.
- Added filtered monetary totals where source-backed.
- Preserved masking and excluded restricted custody/SAP evidence.
- Updated `API_CONTRACTS.md` and recorded assumption A-169.
- Saved RED/GREEN logs, reconciliation/permission matrix, risk assessment, review packet, and final summary.

Validation passed:

- 23 final focused report tests.
- 28 focused and reverse-consumer tests.
- Nine catalogue filter/query-bound tests.
- Django system check.
- Migration consistency check.
- Python compilation.
- Protected-path and diff-limit audit.

The review result is exactly `Ready for independent validation`. No git add, commit, or push was performed.
