# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 486450
Lines: 8150
SHA-256: 36276ea68b8b43f1144b16fd3fac77bb0e3db54c1ca7d49c8fe0ec67fce6cc68
Session ID: 019f890f-9e4d-7371-96af-b1c7aac601e1
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

 - Selected slice: 011D-non-payment-note-workflow
 - Mode: repair
-- Manual review required: yes until agent completes this file.
+- Failed domain: PostgreSQL five-worker create/submit acceptance.
+
+## Root cause and correction
+
+The candidate applied `select_for_update()` to querysets that eager-joined nullable workflow
+relations. PostgreSQL rejects locks against nullable outer-join sides. When explicit lock targets
+were first combined with the same nullable eager joins, concurrent submit replay also demonstrated a
+stale cached `approval_case=None` after the winning request committed.
+
+The final correction uses `select_for_update(of=...)` to lock only the owning workflow row and the
+canonical loan row, and eager-loads only non-null relations involved in those lock targets. This
+preserves duplicate convergence and protects the financial balance snapshot while avoiding nullable
+outer joins and stale cached approval relations.
+
+## Risk controls and residuals
+
+- Final PostgreSQL acceptance: exactly 2 tests passed, including five concurrent creates and five
+  concurrent submits converging on one note and one approval chain.
+- Focused API regression: 6 tests passed. Django check and migration-drift checks passed.
+- PostgreSQL 14.20 environment evidence is retained. No migration, API, permission, frontend, source,
+  protected, dependency, or business-rule change was introduced by this repair.
+- `FOR UPDATE OF` is deliberately PostgreSQL-shaped because PostgreSQL is the production and trusted
+  concurrency database. SQLite remains covered by the focused workflow tests but is not concurrency
+  evidence.
+- Residual process risk: Ralph must still perform its fresh independent validation runs before any
+  commit. No blocking product risk remains from the demonstrated validator.
diff --git a/sfpcl_credit/recovery/modules/recovery_workflow.py b/sfpcl_credit/recovery/modules/recovery_workflow.py
index c7e23c3ca5db12f26e46163b1d529cdcef55770b..a45402d210f2b767042fe453396708da3bab5a62
--- a/sfpcl_credit/recovery/modules/recovery_workflow.py
+++ b/sfpcl_credit/recovery/modules/recovery_workflow.py
@@ -50,12 +50,8 @@
         scoped_case_ids = _scoped_case_candidates(actor=actor).values("pk")
         with transaction.atomic():
             row = (
-                DefaultCase.objects.select_for_update()
-                .select_related(
-                    "loan_account",
-                    "current_assessment",
-                    "extension_note",
-                )
+                DefaultCase.objects.select_for_update(of=("self", "loan_account"))
+                .select_related("loan_account")
                 .filter(pk=default_case_id, pk__in=scoped_case_ids)
                 .first()
             )
@@ -212,8 +208,10 @@
         scoped_case_ids = _scoped_case_candidates(actor=actor).values("pk")
         with transaction.atomic():
             note = (
-                NonPaymentNote.objects.select_for_update()
-                .select_related("loan_account", "default_case", "approval_case")
+                NonPaymentNote.objects.select_for_update(
+                    of=("self", "loan_account", "default_case")
+                )
+                .select_related("loan_account", "default_case")
                 .filter(pk=non_payment_note_id, default_case_id__in=scoped_case_ids)
                 .first()
             )

tokens used
139,352
Repair complete and ready for independent validation.

- Fixed the PostgreSQL concurrency failure in [recovery_workflow.py](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_131655_normal_run/sfpcl_credit/recovery/modules/recovery_workflow.py:52). Lock queries now target only the workflow and canonical loan rows, excluding nullable outer joins and stale nullable relation caches.
- Exact PostgreSQL acceptance class: **2/2 passed**, covering five concurrent creates and five concurrent submits.
- Focused Non-Payment Note workflow tests: **6/6 passed**.
- Django system check passed; migration drift check reported no changes.
- PostgreSQL environment confirmed as PostgreSQL 14.20.
- No protected files were modified, no debug instrumentation remains, and no commit/add/push command was run.

Evidence and handoff:

- [Repair evidence](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_131655_normal_run/.ralph/runs/2026-07-22_143202_repair/evidence/repair-evidence.md)
- [Risk assessment](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_131655_normal_run/.ralph/runs/2026-07-22_143202_repair/risk-assessment.md)
- [Review packet](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_131655_normal_run/.ralph/runs/2026-07-22_143202_repair/review-packet.md) — Result is exactly `Ready for independent validation`.

Ralph should now perform its fresh independent validation runs before committing.
