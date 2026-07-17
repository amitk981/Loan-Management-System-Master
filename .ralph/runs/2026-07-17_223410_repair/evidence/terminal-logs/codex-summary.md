# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 759395
Lines: 12801
SHA-256: a5ceec8bc3ef65cc8f19fd8ad4c1ab56ce25b6960e645552ba5c8a8b10cc036d
Session ID: 019f7109-2e44-7a33-9067-5094fa6beaa5
Raw retention: operator-local, at most 20 runs or 14 days.

## Final Excerpt

+  policy, and checklist policy remain unchanged.
+- The exact red/green test, both impacted backend classes (61 tests), Django check, and migration
+  sync pass. Complete parallel coverage and twice-run PostgreSQL acceptance remain independent
+  orchestrator gates.
+- 009H3 and 009G4 remain concrete after recheck; no sharpening edit was needed.
+
 ## 009G3 Repair — Protected Register Migration Closure
 
 - Independent validation found that the protected `Disbursement.register_update` model relation
diff --git a/sfpcl_credit/tests/test_final_documentation_approval_api.py b/sfpcl_credit/tests/test_final_documentation_approval_api.py
index 8352a6e20372ee6a5ddc8323c06edf49978331c2..cdd092601cc31e8938bb43dedbebfb7d9340ac97
--- a/sfpcl_credit/tests/test_final_documentation_approval_api.py
+++ b/sfpcl_credit/tests/test_final_documentation_approval_api.py
@@ -11,6 +11,7 @@
 from django.core.files.base import ContentFile
 from django.core.files.uploadedfile import SimpleUploadedFile
 from django.db import close_old_connections, connection, connections, transaction
+from django.db.models.deletion import ProtectedError
 from django.test import RequestFactory, TestCase
 from django.test import TransactionTestCase, override_settings
 from django.test.utils import CaptureQueriesContext
@@ -2531,17 +2532,22 @@
         ).update(transfer_evidence_digest=retained_digest)
 
         register = disbursement.loan_register_update
-        register_id = register.pk
-        register.delete()
-        missing_register = self._post_stage(
+        with self.assertRaises(ProtectedError), transaction.atomic():
+            register.delete()
+
+        retained_register_checksum = register.evidence_checksum_sha256
+        register.__class__.objects.filter(pk=register.pk).update(
+            evidence_checksum_sha256="f" * 64
+        )
+        changed_register = self._post_stage(
             "sign-disbursement-complete",
             self.finance,
             {"comments": "Loan has been disbursed to the applicant account."},
         )
-        self.assertEqual(missing_register.status_code, 409, missing_register.content)
-        register.pk = register_id
-        register._state.adding = True
-        register.save(force_insert=True)
+        self.assertEqual(changed_register.status_code, 409, changed_register.content)
+        register.__class__.objects.filter(pk=register.pk).update(
+            evidence_checksum_sha256=retained_register_checksum
+        )
 
         intent = disbursement.advice_intent
         intent.delete()

tokens used
217,252
Repair `2026-07-17_223410_repair` is complete and ready for independent Ralph validation.

The failure was an obsolete regression test deleting `LoanRegisterUpdate`, which 009G3 now correctly protects. Using a focused red/green loop, I updated only that test to:

- Assert deletion raises `ProtectedError`.
- Mutate the retained register checksum to preserve the HTTP 409 reconciliation check.
- Leave all production code and migration behavior unchanged.

Verification:

- Exact repaired test: passed.
- Impacted backend classes: 61 tests passed.
- Django system check: passed.
- Migration sync: no changes detected.
- Protected-path and whitespace checks: passed.
- No frontend changes.
- No git add, commit, or push performed.

A supplemental local parallel run was excluded because spawned workers encountered an x86_64/arm64 CFFI mismatch before running tests. Full parallel coverage and twice-run PostgreSQL acceptance remain authoritative orchestrator gates.

Artifacts:

- [Final summary](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_215313_normal_run/.ralph/runs/2026-07-17_223410_repair/final-summary.md)
- [Review packet](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_215313_normal_run/.ralph/runs/2026-07-17_223410_repair/review-packet.md)
- [RED evidence](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_215313_normal_run/.ralph/runs/2026-07-17_223410_repair/evidence/terminal-logs/focused-test-red.md)
- [GREEN evidence](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_215313_normal_run/.ralph/runs/2026-07-17_223410_repair/evidence/terminal-logs/focused-test-green.md)
