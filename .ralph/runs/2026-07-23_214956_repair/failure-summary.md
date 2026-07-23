# Failure Summary

- Run: 2026-07-23_214956_repair
- Mode: repair
- Slice: 011O-auditor-read-only-views
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=1, skipped=10)
```

## Last 50 lines: backend-coverage-results.md

```
..................ssss....................ssssss...............................E
======================================================================
ERROR: test_compliance_cfo_cs_and_auditor_permission_matrix (sfpcl_credit.tests.test_global_search_compliance.GlobalSearchComplianceTests.test_compliance_cfo_cs_and_auditor_permission_matrix) [<object object at 0x107e4a650>] (role='internal_auditor')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 57, in testPartExecutor
    yield
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 538, in subTest
    yield
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_210407_normal_run/sfpcl_credit/tests/test_global_search_compliance.py", line 377, in test_compliance_cfo_cs_and_auditor_permission_matrix
    cards = search_compliance_records(
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_210407_normal_run/sfpcl_credit/compliance/search_facade.py", line 22, in search_compliance_records
    list(compliance_control_tracker.search_controls(actor=actor, search=search))
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_210407_normal_run/sfpcl_credit/compliance/modules/compliance_control_tracker.py", line 110, in search_controls
    require(actor, "compliance.control.read")
      ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_210407_normal_run/sfpcl_credit/compliance/modules/compliance_control_tracker.py", line 41, in require
    require_auditor_scope(actor)
      ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_210407_normal_run/sfpcl_credit/compliance/modules/compliance_control_tracker.py", line 52, in require_auditor_scope
    raise ComplianceDenied()
    ^^^^^^^^^^^^^^^^^
sfpcl_credit.compliance.modules.compliance_control_tracker.ComplianceDenied

----------------------------------------------------------------------
Ran 658 tests in 53.243s

FAILED (errors=1, skipped=10)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 79.165s
  Creating 'default' took 79.060s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.019s
  Cloning 'default' took 0.021s
  Cloning 'default' took 0.024s
  Cloning 'default' took 0.020s
Total database teardown took 0.002s
Total run took 133.193s

Duration milliseconds: 133945
Exit code: 1
```

## Changed files (git status)

```
.ralph/runs/2026-07-23_210407_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-23_210407_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-23_210407_normal_run/backend-check-results.md
.ralph/runs/2026-07-23_210407_normal_run/backend-coverage-results.md
.ralph/runs/2026-07-23_210407_normal_run/backend-impacted-results.md
.ralph/runs/2026-07-23_210407_normal_run/backend-migrations-results.md
.ralph/runs/2026-07-23_210407_normal_run/backend-test-results.md
.ralph/runs/2026-07-23_210407_normal_run/backend-validation-lane-results.md
.ralph/runs/2026-07-23_210407_normal_run/build-results.md
.ralph/runs/2026-07-23_210407_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-23_210407_normal_run/candidate-hash-results.md
.ralph/runs/2026-07-23_210407_normal_run/changed-files.txt
.ralph/runs/2026-07-23_210407_normal_run/codex-settings.md
.ralph/runs/2026-07-23_210407_normal_run/diff-limits-results.md
.ralph/runs/2026-07-23_210407_normal_run/e2e-results.md
.ralph/runs/2026-07-23_210407_normal_run/evidence/screenshots/run-1/auditor-epic-011-empty.png
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-backend-focused.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-empty-green.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-empty-red.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-frontend-green.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-frontend-red.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-mutation-green.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-mutation-red.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-mutation-side-effects-green.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-mutation-side-effects.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-playwright.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-populated-green.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-populated-red.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-scope-green.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-scope-red.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/backend-check.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/backend-impacted-regressions-green.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/backend-impacted-regressions.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/backend-migrations-check.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/frontend-build.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/frontend-full-tests.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/frontend-lint.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/frontend-typecheck.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/trusted-browser-acceptance-1.log
.ralph/runs/2026-07-23_210407_normal_run/execution-plan.md
.ralph/runs/2026-07-23_210407_normal_run/failure-summary.md
.ralph/runs/2026-07-23_210407_normal_run/final-summary.md
.ralph/runs/2026-07-23_210407_normal_run/install-results.md
.ralph/runs/2026-07-23_210407_normal_run/lint-results.md
.ralph/runs/2026-07-23_210407_normal_run/no-op-check-results.md
.ralph/runs/2026-07-23_210407_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-23_210407_normal_run/preflight-results.md
.ralph/runs/2026-07-23_210407_normal_run/prompt.md
.ralph/runs/2026-07-23_210407_normal_run/protected-paths-check.md
.ralph/runs/2026-07-23_210407_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-23_210407_normal_run/review-packet.md
.ralph/runs/2026-07-23_210407_normal_run/risk-assessment.md
.ralph/runs/2026-07-23_210407_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-23_210407_normal_run/slice-status-transition-check.md
.ralph/runs/2026-07-23_210407_normal_run/test-results.md
.ralph/runs/2026-07-23_210407_normal_run/typecheck-results.md
.ralph/runs/2026-07-23_210407_normal_run/validated-commit-candidate.sha256
.ralph/runs/2026-07-23_214956_repair/agent-declared-result-check.md
.ralph/runs/2026-07-23_214956_repair/artifact-quality-check.md
.ralph/runs/2026-07-23_214956_repair/candidate-fast-check-results.md
.ralph/runs/2026-07-23_214956_repair/changed-files.txt
.ralph/runs/2026-07-23_214956_repair/codex-settings.md
.ralph/runs/2026-07-23_214956_repair/diff-limits-results.md
.ralph/runs/2026-07-23_214956_repair/evidence/terminal-logs/auditor-epic-011-browser-final-attempt.log
.ralph/runs/2026-07-23_214956_repair/evidence/terminal-logs/auditor-epic-011-browser-red.log
.ralph/runs/2026-07-23_214956_repair/evidence/terminal-logs/auditor-epic-011-frontend-focused.log
.ralph/runs/2026-07-23_214956_repair/evidence/terminal-logs/auditor-epic-011-playwright-list.log
.ralph/runs/2026-07-23_214956_repair/evidence/terminal-logs/auditor-epic-011-trusted-functional-red.log
.ralph/runs/2026-07-23_214956_repair/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-23_214956_repair/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-23_214956_repair/evidence/terminal-logs/frontend-build.log
.ralph/runs/2026-07-23_214956_repair/evidence/terminal-logs/frontend-lint.log
.ralph/runs/2026-07-23_214956_repair/evidence/terminal-logs/frontend-typecheck.log
.ralph/runs/2026-07-23_214956_repair/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-23_214956_repair/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-23_214956_repair/execution-plan.md
.ralph/runs/2026-07-23_214956_repair/final-summary.md
.ralph/runs/2026-07-23_214956_repair/orchestrator-ownership-check.md
.ralph/runs/2026-07-23_214956_repair/preflight-results.md
.ralph/runs/2026-07-23_214956_repair/prompt.md
.ralph/runs/2026-07-23_214956_repair/protected-paths-check.md
.ralph/runs/2026-07-23_214956_repair/ralph-artifact-validation.md
.ralph/runs/2026-07-23_214956_repair/review-packet.md
.ralph/runs/2026-07-23_214956_repair/risk-assessment.md
.ralph/runs/2026-07-23_214956_repair/slice-queue-lint.md
.ralph/runs/2026-07-23_214956_repair/slice-status-transition-check.md
docs/working/API_CONTRACTS.md
docs/working/PROTOTYPE_GAP_REPORT.md
docs/working/PROTOTYPE_INVENTORY.md
sfpcl-lms/e2e/auditor-read-only-epic-011.e2e.spec.ts
sfpcl-lms/src/App.tsx
sfpcl-lms/src/pages/compliance/AuditorEpic011View.test.tsx
sfpcl-lms/src/pages/compliance/AuditorEpic011View.tsx
sfpcl-lms/src/services/auditorApi.ts
sfpcl_credit/approvals/modules/read_scope.py
sfpcl_credit/closure/modules/loan_closure.py
sfpcl_credit/compliance/modules/auditor_epic_011.py
sfpcl_credit/compliance/modules/compliance_control_tracker.py
sfpcl_credit/compliance/modules/grievance_workflow.py
sfpcl_credit/compliance/modules/kyc_review_tracker.py
sfpcl_credit/compliance/modules/nbfc_principal_business_test.py
sfpcl_credit/compliance/modules/section186_tracker.py
sfpcl_credit/compliance/views.py
sfpcl_credit/config/urls.py
sfpcl_credit/defaults/modules/default_workflow.py
sfpcl_credit/identity/catalogue.py
sfpcl_credit/tests/test_auditor_epic_011_api.py
sfpcl_credit/tests/test_default_case_opening_api.py
sfpcl_credit/tests/test_kyc_review_api.py
sfpcl_credit/tests/test_statutory_trackers.py
```
