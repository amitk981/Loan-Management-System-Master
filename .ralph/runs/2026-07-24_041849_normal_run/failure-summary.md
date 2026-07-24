# Failure Summary

- Run: 2026-07-24_041849_normal_run
- Mode: normal_run
- Slice: 012B-register-exports
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAIL: test_production_code_does_not_use_legacy_permission_denied_literal (sfpcl_credit.tests.test_api_contract_harness.ApiContractHarnessUnitTests.test_production_code_does_not_use_legacy_permission_denied_literal)
backend-coverage-results.md:FAILED (failures=1)
```

## Last 50 lines: backend-coverage-results.md

```
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 579, in _callTestMethod
    if method() is not None:
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_041849_normal_run/sfpcl_credit/tests/test_api_contract_harness.py", line 42, in test_production_code_does_not_use_legacy_permission_denied_literal
    self.assertEqual(offenders, [], f"legacy permission literals: {offenders}")
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 873, in assertEqual
    assertion_func(first, second, msg=msg)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 1079, in assertListEqual
    self.assertSequenceEqual(list1, list2, msg, seq_type=list)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 1061, in assertSequenceEqual
    self.fail(msg)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 703, in fail
    raise self.failureException(msg)
    ^^^^^^^^^^^^^^^^^
AssertionError: Lists differ: ['reports/modules/report_export.py'] != []

First list contains 1 additional elements.
First extra element 0:
'reports/modules/report_export.py'

- ['reports/modules/report_export.py']
+ [] : legacy permission literals: ['reports/modules/report_export.py']

----------------------------------------------------------------------
Ran 61 tests in 2.207s

FAILED (failures=1)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 79.236s
  Creating 'default' took 79.159s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.012s
  Cloning 'default' took 0.013s
  Cloning 'default' took 0.014s
  Cloning 'default' took 0.013s
  Cloning 'default' took 0.014s
Total database teardown took 0.002s
Total run took 82.321s

Duration milliseconds: 82997
Exit code: 1
```

## Changed files (git status)

```
.ralph/runs/2026-07-24_041849_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-24_041849_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-24_041849_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-24_041849_normal_run/changed-files.txt
.ralph/runs/2026-07-24_041849_normal_run/codex-settings.md
.ralph/runs/2026-07-24_041849_normal_run/diff-limits-results.md
.ralph/runs/2026-07-24_041849_normal_run/evidence/report-export-evidence.md
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/01-request-replay-red.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/02-request-replay-green.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/03-request-replay-green.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/04-request-replay-green.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/05-worker-download-red.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/06-worker-download-green.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/07-worker-download-green.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/08-format-matrix-red.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/09-format-matrix-green.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/10-retention-red.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/11-retention-green.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/12-permission-audit-red.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/13-permission-audit-green.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/14-failure-retry-red.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/15-failure-retry-green.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/16-failure-retry-green.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/17-focused-export-api.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/18-django-check.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/19-migrations-check.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/20-postgresql-five-race.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/21-report-selector-regressions.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/22-running-lease-red.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/23-running-lease-green.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/24-running-lease-green-keepdb.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/25-running-lease-green-freshdb.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/26-postgresql-final.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/27-focused-export-final.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/28-django-check-final.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/29-migrations-final.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/30-focused-export-post-review.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/31-django-check-post-review.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/32-migrations-post-review.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/33-focused-export-worker-registration.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/34-django-check-worker-registration.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/35-migrations-worker-registration.txt
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-24_041849_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-24_041849_normal_run/execution-plan.md
.ralph/runs/2026-07-24_041849_normal_run/final-summary.md
.ralph/runs/2026-07-24_041849_normal_run/no-op-check-results.md
.ralph/runs/2026-07-24_041849_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-24_041849_normal_run/preflight-results.md
.ralph/runs/2026-07-24_041849_normal_run/prompt.md
.ralph/runs/2026-07-24_041849_normal_run/protected-paths-check.md
.ralph/runs/2026-07-24_041849_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-24_041849_normal_run/review-packet.md
.ralph/runs/2026-07-24_041849_normal_run/risk-assessment.md
.ralph/runs/2026-07-24_041849_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-24_041849_normal_run/slice-status-transition-check.md
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
sfpcl_credit/config/settings.py
sfpcl_credit/config/urls.py
sfpcl_credit/processes/tasks.py
sfpcl_credit/reports/apps.py
sfpcl_credit/reports/migrations/0001_initial.py
sfpcl_credit/reports/migrations/__init__.py
sfpcl_credit/reports/models.py
sfpcl_credit/reports/modules/__init__.py
sfpcl_credit/reports/modules/report_export.py
sfpcl_credit/reports/storage.py
sfpcl_credit/reports/views.py
sfpcl_credit/tests/test_report_export_postgresql_acceptance.py
sfpcl_credit/tests/test_report_exports_api.py
```
