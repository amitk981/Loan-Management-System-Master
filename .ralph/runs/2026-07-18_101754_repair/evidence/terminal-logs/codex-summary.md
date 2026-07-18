# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 617005
Lines: 9427
SHA-256: 65932afaf73ec82d81cc1b85f161d5029c2bce143fd6f956b8bde101d3bcb9c2
Session ID: 019f738d-7cf2-7b63-a6ad-3b1b8d068bff
Raw retention: operator-local, at most 20 runs or 14 days.

## Final Excerpt

-No assumption, API, frontend, model, production row, or status changed. 009I and 009J were rechecked;
-both already contain concrete source-backed endpoints, fields, authority, validation, tests, and
-browser evidence, so no speculative sharpening edit was made.
+The exact failure was reproduced before the test-only fix. Both credit-ownership migration cases
+then passed in three runs total, and the combined 15-test 009G4/credit/communications/document/SAP
+migration set passed. Django check, migration sync, and compilation are green. Production migrations,
+models, APIs, checklist rows/statuses, ownership guard, and the 009G3 aggregate are unchanged; full
+coverage remains the independent repair gate. 009I and 009J were rechecked and remain concrete, so
+no speculative sharpening edit was made.
 
 ## Next Run
 Run 009I for the borrower-safe MP14 projection and advice download flow. Then run 009J for the
diff --git a/docs/working/digests/epic-009-sap-loan-account-disbursement.md b/docs/working/digests/epic-009-sap-loan-account-disbursement.md
index d7c31e7db041179a9d655438c77079dfe3c6de3e..1c1d5df598fae7942059c72614858844828f6c9f
--- a/docs/working/digests/epic-009-sap-loan-account-disbursement.md
+++ b/docs/working/digests/epic-009-sap-loan-account-disbursement.md
@@ -1,5 +1,17 @@
 # Epic 009 Digest — SAP, Loan Account, and Disbursement
 
+## 009G4 Repair — Historical Credit Projection Isolation
+
+- The new legal 0015 leaf depends on current disbursement/communications state, so a retained
+  credit-ownership migration test that projected every leaf except known downstream apps silently
+  pulled `credit.0001` into its intended pre-move `applications.0010` registry.
+- The test now also excludes `legal_documents`; the projected registry again contains application-
+  owned `EligibilityAssessment` and `LoanLimitAssessment`. Production migrations, models, rows,
+  constraints, APIs, checklist behavior, and the 009G3 aggregate are unchanged.
+- The exact coverage failure was reproduced. The two-test credit migration class passed repeatedly,
+  the combined 15-test 009G4/credit/communications/document/SAP migration set passed, and Django
+  check, migration sync, and compilation are green. Full coverage remains the independent gate.
+
 ## 009G4 Legal Checklist Migration Ownership Anchor
 
 - Legal documents migration 0015 is an empty, zero-SQL state anchor over the current legal 0014,
diff --git a/sfpcl_credit/tests/test_credit_model_ownership_migration.py b/sfpcl_credit/tests/test_credit_model_ownership_migration.py
index 6136d51c65839f4ce982e58841b4c00162ecb02d..20313832d863eef4899387c2e3b507adf1c9d715
--- a/sfpcl_credit/tests/test_credit_model_ownership_migration.py
+++ b/sfpcl_credit/tests/test_credit_model_ownership_migration.py
@@ -20,9 +20,9 @@
         pre_move_state_targets = [
             node
             for node in self.executor.loader.graph.leaf_nodes()
-            # Downstream loan-account, SAP, and communications ownership anchor
-            # current approval/application state and must not outrun this
-            # historical pre-move projection.
+            # Downstream legal-document, loan-account, SAP, and communications
+            # ownership anchors current approval/application state and must not
+            # outrun this historical pre-move projection.
             if node[0]
             not in {
                 "credit",
@@ -31,6 +31,7 @@
                 "sap_workflow",
                 "disbursements",
                 "communications",
+                "legal_documents",
             }
         ]
         old_apps = self.executor.loader.project_state(pre_move_state_targets).apps

tokens used
147,996
Repair `2026-07-18_101754_repair` is complete pending independent Ralph validation.

Root cause: the new `legal_documents.0015` migration leaf transitively pulled current `credit.0001` state into a historical test projection intended to stop at `applications.0010`. The projected registry therefore lacked the application-owned assessment models.

Repair: [test_credit_model_ownership_migration.py](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_095146_normal_run/sfpcl_credit/tests/test_credit_model_ownership_migration.py:20) now excludes `legal_documents` alongside the other downstream migration leaves. No production migration, model, schema, data, API, checklist behavior, frontend, or 009G3 aggregate changed.

Verification completed:

- Exact failure reproduced: 1 test red with the original `EligibilityAssessment` lookup error.
- Both forward/reverse ownership tests passed repeatedly.
- Combined 15-test migration set passed.
- Django check passed.
- Migration sync passed with no changes detected.
- Python compilation passed.
- Protected-path, whitespace, debug-marker, diff-limit, and artifact checks passed.
- 009I and 009J remain fully sharpened; no speculative edits were made.

Repair artifacts are in [.ralph/runs/2026-07-18_101754_repair](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_095146_normal_run/.ralph/runs/2026-07-18_101754_repair). The authoritative complete backend coverage suite remains delegated to the Ralph orchestrator, and no git commit/add/push was attempted.
