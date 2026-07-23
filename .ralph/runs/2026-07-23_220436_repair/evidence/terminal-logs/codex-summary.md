# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 8156219
Lines: 72968
SHA-256: 618dc30c091a391bcaec6cbc9116113924e82d3b1d2bc2f6bd68875c51c82cd6
Session ID: 019f8fd4-57dc-75f1-85e2-78fe28ed9ef9
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+- Repair delta: one legacy test fixture now creates the auditor's required active
+  `audit_readonly` scope grant
+- Production, schema, routing, frontend, dependency, and source-document changes in this repair:
+  none
+
+## Demonstrated failure and mitigation
+
+The authoritative coverage run failed in the `internal_auditor` row of the global compliance-search
+permission matrix. Slice 011O correctly added a persisted-scope guard to compliance reads, but the
+pre-existing test constructed a fresh auditor role with read permissions and omitted the now-binding
+`ApprovalCaseReadScopeGrant`.
+
+The repair grants `SCOPE_AUDIT_READONLY` to that exact test actor's role. It does not bypass or weaken
+the production guard. Adjacent tests continue to prove that an auditor with an inactive scope receives
+403 responses.
+
+## Residual risks
+
+- Future test actors that model Internal Auditor reads must create both the relevant read permissions
+  and the persisted `audit_readonly` scope. Omitting either should continue to fail closed.
+- The macOS Codex shell runs under Rosetta while the pinned virtualenv extensions are arm64.
+  Multiprocessing coverage therefore requires the established `PYTHONEXECUTABLE` wrapper handoff.
+  This affects local validator execution only; the unchanged authoritative script and arguments passed.
+
+## Verification
+
+- Exact failing behavior test RED, then GREEN.
+- Adjacent global-search and 011O auditor scope matrix: 11 tests passed.
+- Exact six-worker backend coverage validator: 1,728 tests passed, 175 skipped, 0 failures/errors.
+- Coverage: 89%, above the required 85% floor.
+- `git diff --check`: passed.
diff --git a/sfpcl_credit/tests/test_global_search_compliance.py b/sfpcl_credit/tests/test_global_search_compliance.py
index 4def15a3afedd68625b5f40ef7faf3164adca364..80e85ef4c3f8eea1bc5d07c7b696108b62981956
--- a/sfpcl_credit/tests/test_global_search_compliance.py
+++ b/sfpcl_credit/tests/test_global_search_compliance.py
@@ -5,6 +5,7 @@
 from django.test import Client, TestCase
 from django.utils import timezone
 
+from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant
 from sfpcl_credit.compliance.models import (
     ComplianceControl,
     ComplianceEvidence,
@@ -357,6 +358,11 @@
             "compliance.task.read",
             "compliance.evidence.review",
         )
+        ApprovalCaseReadScopeGrant.objects.create(
+            role=auditor.primary_role,
+            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
+            status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
+        )
 
         expected = {
             self.owner.pk: {str(self.control.pk), str(self.task.pk)},

tokens used
203,149
Repair completed and marked **Ready for independent validation**.

The failure was a stale global-search test fixture: its Internal Auditor had read permissions but lacked the persisted `audit_readonly` scope now required by slice 011O. The repair adds that active scope grant to the test actor’s exact role; production authorization remains unchanged and fail-closed.

Validation:

- Original focused test: RED reproduced, then GREEN.
- Adjacent auditor/global-search matrix: 11 tests passed.
- Exact six-worker backend validator: 1,728 tests passed, 175 skipped, zero failures/errors.
- Coverage: 89%, above the required 85%.
- `git diff --check`: passed.
- No protected files, source documents, schema, routing, frontend, or production code changed by this repair.
- No git add, commit, or push performed.

Artifacts:

- [Review packet](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_210407_normal_run/.ralph/runs/2026-07-23_220436_repair/review-packet.md)
- [Risk assessment](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_210407_normal_run/.ralph/runs/2026-07-23_220436_repair/risk-assessment.md)
- [Final summary](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_210407_normal_run/.ralph/runs/2026-07-23_220436_repair/final-summary.md)
- [Exact coverage evidence](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_210407_normal_run/.ralph/runs/2026-07-23_220436_repair/evidence/terminal-logs/backend-coverage-exact-validator-green.log)

Ralph should now perform full independent validation and commit only if every selected gate remains green.
