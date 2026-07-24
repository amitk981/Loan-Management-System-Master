# Failure Summary

- Run: 2026-07-24_071133_normal_run
- Mode: normal_run
- Slice: 012D-audit-explorer
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAIL: test_request_status_authentication_validation_and_not_found_contracts (sfpcl_credit.tests.test_report_exports_api.ReportExportApiTests.test_request_status_authentication_validation_and_not_found_contracts)
backend-coverage-results.md:FAILED (failures=1, skipped=10)
```

## Last 50 lines: backend-coverage-results.md

```
............Catalogue seeded: 197 permissions, 20 roles, 8 teams, 272 role-permission links.
.Catalogue seeded: 197 permissions, 20 roles, 8 teams, 272 role-permission links.
...............................F
======================================================================
FAIL: test_request_status_authentication_validation_and_not_found_contracts (sfpcl_credit.tests.test_report_exports_api.ReportExportApiTests.test_request_status_authentication_validation_and_not_found_contracts)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 57, in testPartExecutor
    yield
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 623, in run
    self._callTestMethod(testMethod)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 579, in _callTestMethod
    if method() is not None:
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_071133_normal_run/sfpcl_credit/tests/test_report_exports_api.py", line 800, in test_request_status_authentication_validation_and_not_found_contracts
    self.assertIn("report_code", unsupported.json()["error"]["field_errors"])
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 1140, in assertIn
    self.fail(self._formatMessage(msg, standardMsg))
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 703, in fail
    raise self.failureException(msg)
    ^^^^^^^^^^^^^^^^^
AssertionError: 'report_code' not found in {'format': 'Must be one of csv, xlsx, pdf, json.'}

----------------------------------------------------------------------
Ran 1215 tests in 115.727s

FAILED (failures=1, skipped=10)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 80.061s
  Creating 'default' took 79.989s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.013s
  Cloning 'default' took 0.012s
  Cloning 'default' took 0.013s
  Cloning 'default' took 0.012s
Total database teardown took 0.022s
Total run took 196.432s

Duration milliseconds: 197177
Exit code: 1
```

## Changed files (git status)

```
.ralph/runs/2026-07-24_071133_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-24_071133_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-24_071133_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-24_071133_normal_run/changed-files.txt
.ralph/runs/2026-07-24_071133_normal_run/codex-settings.md
.ralph/runs/2026-07-24_071133_normal_run/diff-limits-results.md
.ralph/runs/2026-07-24_071133_normal_run/evidence/api-responses/filtered-pages.md
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/audit-explorer-focused-green.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/audit-explorer-focused.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/audit-explorer-green.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/audit-explorer-red.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/audit-export-green.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/audit-export-red.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/audit-reverse-consumers.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/audit-scope-green.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/audit-scope-red.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/backend-check.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/final-focused-regression-2.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/final-focused-regression.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/final-targeted-after-review.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/migrations-check.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/reference-filter-green.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/reference-filter-red.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/version-explorer-green.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/version-explorer-red.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/workflow-explorer-green.log
.ralph/runs/2026-07-24_071133_normal_run/evidence/terminal-logs/workflow-explorer-red.log
.ralph/runs/2026-07-24_071133_normal_run/execution-plan.md
.ralph/runs/2026-07-24_071133_normal_run/final-summary.md
.ralph/runs/2026-07-24_071133_normal_run/no-op-check-results.md
.ralph/runs/2026-07-24_071133_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-24_071133_normal_run/preflight-results.md
.ralph/runs/2026-07-24_071133_normal_run/prompt.md
.ralph/runs/2026-07-24_071133_normal_run/protected-paths-check.md
.ralph/runs/2026-07-24_071133_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-24_071133_normal_run/review-packet.md
.ralph/runs/2026-07-24_071133_normal_run/risk-assessment.md
.ralph/runs/2026-07-24_071133_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-24_071133_normal_run/slice-status-transition-check.md
docs/working/API_CONTRACTS.md
sfpcl_credit/configurations/services.py
sfpcl_credit/configurations/views.py
sfpcl_credit/identity/audit_views.py
sfpcl_credit/identity/modules/audit_log.py
sfpcl_credit/reports/registry.py
sfpcl_credit/reports/selectors/audit_log.py
sfpcl_credit/reports/views.py
sfpcl_credit/shared/masking.py
sfpcl_credit/tests/test_audit_explorer_api.py
sfpcl_credit/tests/test_audit_logs_api.py
sfpcl_credit/tests/test_configurations_api.py
sfpcl_credit/tests/test_report_catalogue_api.py
sfpcl_credit/tests/test_workflow_events_api.py
sfpcl_credit/workflows/event_views.py
sfpcl_credit/workflows/events.py
```
