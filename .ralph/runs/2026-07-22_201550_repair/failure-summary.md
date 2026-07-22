# Failure Summary

- Run: 2026-07-22_201550_repair
- Mode: repair
- Slice: 011G-closure-readiness
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=1, skipped=101)
```

## Last 50 lines: backend-coverage-results.md

```
    ^^^^^^^^^^^^^^^^^
KeyError: 'eligibilityassessment'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 57, in testPartExecutor
    yield
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 619, in run
    self._callSetUp()
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 576, in _callSetUp
    self.setUp()
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_191406_normal_run/sfpcl_credit/tests/test_credit_model_ownership_migration.py", line 44, in setUp
    self.identifiers = self._create_pre_move_rows(old_apps)
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_191406_normal_run/sfpcl_credit/tests/test_credit_model_ownership_migration.py", line 148, in _create_pre_move_rows
    EligibilityAssessment = old_apps.get_model("applications", "EligibilityAssessment")
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/apps/registry.py", line 213, in get_model
    return app_config.get_model(model_name, require_ready=require_ready)
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/apps/config.py", line 237, in get_model
    raise LookupError(
    ^^^^^^^^^^^^^^^^^
LookupError: App 'applications' doesn't have a 'EligibilityAssessment' model.

----------------------------------------------------------------------
Ran 1530 tests in 801.432s

FAILED (errors=1, skipped=101)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 65.328s
  Creating 'default' took 65.254s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.014s
  Cloning 'default' took 0.015s
  Cloning 'default' took 0.014s
Total database teardown took 0.021s
Total run took 867.327s

Duration milliseconds: 868013
Exit code: 1
```

## Changed files (git status)

```
.ralph/runs/2026-07-22_191406_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-22_191406_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-22_191406_normal_run/backend-check-results.md
.ralph/runs/2026-07-22_191406_normal_run/backend-coverage-results.md
.ralph/runs/2026-07-22_191406_normal_run/backend-impacted-results.md
.ralph/runs/2026-07-22_191406_normal_run/backend-migrations-results.md
.ralph/runs/2026-07-22_191406_normal_run/backend-test-results.md
.ralph/runs/2026-07-22_191406_normal_run/backend-validation-lane-results.md
.ralph/runs/2026-07-22_191406_normal_run/build-results.md
.ralph/runs/2026-07-22_191406_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-22_191406_normal_run/candidate-hash-results.md
.ralph/runs/2026-07-22_191406_normal_run/changed-files.txt
.ralph/runs/2026-07-22_191406_normal_run/codex-settings.md
.ralph/runs/2026-07-22_191406_normal_run/diff-limits-results.md
.ralph/runs/2026-07-22_191406_normal_run/e2e-results.md
.ralph/runs/2026-07-22_191406_normal_run/evidence/behavior-matrix.md
.ralph/runs/2026-07-22_191406_normal_run/evidence/postgresql-environment-validation.md
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/01-readiness-red.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/02-readiness-green.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/03-close-red.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/04-close-green.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/05-closure-focused.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/06-closure-focused-green.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/07-closed-mutation-red.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/08-closed-mutation-green.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/09-closure-and-postgres-label.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/10-postgresql-acceptance-first.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/11-postgresql-acceptance-green.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/12-postgresql-acceptance-second.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/13-django-check-migrations.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/14-focused-reverse-consumers.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/15-closure-post-review.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/16-closure-post-review-green.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/17-postgresql-post-review-first.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/18-postgresql-final-first.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/19-postgresql-final-second.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/20-final-focused-reverse-consumers.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/21-repaired-focused-consumers.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/22-final-static-checks.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/23-lock-safe-focused.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/24-lock-safe-postgresql-first.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/25-lock-safe-postgresql-second.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/26-final-static-checks.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/postgresql-acceptance-validation-1.txt
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/postgresql-acceptance-validation-2.txt
.ralph/runs/2026-07-22_191406_normal_run/execution-plan.md
.ralph/runs/2026-07-22_191406_normal_run/failure-summary.md
.ralph/runs/2026-07-22_191406_normal_run/final-summary.md
.ralph/runs/2026-07-22_191406_normal_run/install-results.md
.ralph/runs/2026-07-22_191406_normal_run/lint-results.md
.ralph/runs/2026-07-22_191406_normal_run/no-op-check-results.md
.ralph/runs/2026-07-22_191406_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-22_191406_normal_run/postgresql-acceptance-results.md
.ralph/runs/2026-07-22_191406_normal_run/preflight-results.md
.ralph/runs/2026-07-22_191406_normal_run/prompt.md
.ralph/runs/2026-07-22_191406_normal_run/protected-paths-check.md
.ralph/runs/2026-07-22_191406_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-22_191406_normal_run/review-packet.md
.ralph/runs/2026-07-22_191406_normal_run/risk-assessment.md
.ralph/runs/2026-07-22_191406_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-22_191406_normal_run/slice-status-transition-check.md
.ralph/runs/2026-07-22_191406_normal_run/test-results.md
.ralph/runs/2026-07-22_191406_normal_run/typecheck-results.md
.ralph/runs/2026-07-22_191406_normal_run/validated-commit-candidate.sha256
.ralph/runs/2026-07-22_200332_repair/agent-declared-result-check.md
.ralph/runs/2026-07-22_200332_repair/artifact-quality-check.md
.ralph/runs/2026-07-22_200332_repair/backend-check-results.md
.ralph/runs/2026-07-22_200332_repair/backend-coverage-results.md
.ralph/runs/2026-07-22_200332_repair/backend-impacted-results.md
.ralph/runs/2026-07-22_200332_repair/backend-migrations-results.md
.ralph/runs/2026-07-22_200332_repair/backend-test-results.md
.ralph/runs/2026-07-22_200332_repair/backend-validation-lane-results.md
.ralph/runs/2026-07-22_200332_repair/build-results.md
.ralph/runs/2026-07-22_200332_repair/candidate-fast-check-results.md
.ralph/runs/2026-07-22_200332_repair/candidate-hash-results.md
.ralph/runs/2026-07-22_200332_repair/changed-files.txt
.ralph/runs/2026-07-22_200332_repair/codex-settings.md
.ralph/runs/2026-07-22_200332_repair/diff-limits-results.md
.ralph/runs/2026-07-22_200332_repair/e2e-results.md
.ralph/runs/2026-07-22_200332_repair/evidence/postgresql-environment-validation.md
.ralph/runs/2026-07-22_200332_repair/evidence/repair-diagnosis.md
.ralph/runs/2026-07-22_200332_repair/evidence/terminal-logs/01-default-grace-closed-fixture-red.log
.ralph/runs/2026-07-22_200332_repair/evidence/terminal-logs/02-default-grace-closed-fixture-green.log
.ralph/runs/2026-07-22_200332_repair/evidence/terminal-logs/03-focused-regression-green.log
.ralph/runs/2026-07-22_200332_repair/evidence/terminal-logs/04-static-checks-green.log
.ralph/runs/2026-07-22_200332_repair/evidence/terminal-logs/05-repair-artifact-checks-green.log
.ralph/runs/2026-07-22_200332_repair/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-22_200332_repair/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-22_200332_repair/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-22_200332_repair/evidence/terminal-logs/postgresql-acceptance-validation-1.txt
.ralph/runs/2026-07-22_200332_repair/evidence/terminal-logs/postgresql-acceptance-validation-2.txt
.ralph/runs/2026-07-22_200332_repair/execution-plan.md
.ralph/runs/2026-07-22_200332_repair/failure-summary.md
.ralph/runs/2026-07-22_200332_repair/final-summary.md
.ralph/runs/2026-07-22_200332_repair/install-results.md
.ralph/runs/2026-07-22_200332_repair/lint-results.md
.ralph/runs/2026-07-22_200332_repair/orchestrator-ownership-check.md
.ralph/runs/2026-07-22_200332_repair/postgresql-acceptance-results.md
.ralph/runs/2026-07-22_200332_repair/preflight-results.md
.ralph/runs/2026-07-22_200332_repair/prompt.md
.ralph/runs/2026-07-22_200332_repair/protected-paths-check.md
.ralph/runs/2026-07-22_200332_repair/ralph-artifact-validation.md
.ralph/runs/2026-07-22_200332_repair/review-packet.md
.ralph/runs/2026-07-22_200332_repair/risk-assessment.md
.ralph/runs/2026-07-22_200332_repair/slice-queue-lint.md
.ralph/runs/2026-07-22_200332_repair/slice-status-transition-check.md
.ralph/runs/2026-07-22_200332_repair/test-results.md
.ralph/runs/2026-07-22_200332_repair/typecheck-results.md
.ralph/runs/2026-07-22_200332_repair/validated-commit-candidate.sha256
.ralph/runs/2026-07-22_201550_repair/agent-declared-result-check.md
.ralph/runs/2026-07-22_201550_repair/artifact-quality-check.md
.ralph/runs/2026-07-22_201550_repair/candidate-fast-check-results.md
.ralph/runs/2026-07-22_201550_repair/changed-files.txt
.ralph/runs/2026-07-22_201550_repair/codex-settings.md
.ralph/runs/2026-07-22_201550_repair/diff-limits-results.md
.ralph/runs/2026-07-22_201550_repair/evidence/repair-diagnosis.md
.ralph/runs/2026-07-22_201550_repair/evidence/terminal-logs/01-dpd-query-budget-red.log
.ralph/runs/2026-07-22_201550_repair/evidence/terminal-logs/02-dpd-query-debug.log
.ralph/runs/2026-07-22_201550_repair/evidence/terminal-logs/03-dpd-query-instrumented.log
.ralph/runs/2026-07-22_201550_repair/evidence/terminal-logs/04-dpd-query-budget-green.log
.ralph/runs/2026-07-22_201550_repair/evidence/terminal-logs/05-dpd-monitoring-focused-green.log
.ralph/runs/2026-07-22_201550_repair/evidence/terminal-logs/06-closure-repayment-reverse-consumers-green.log
.ralph/runs/2026-07-22_201550_repair/evidence/terminal-logs/07-backend-static-checks-green.log
.ralph/runs/2026-07-22_201550_repair/evidence/terminal-logs/08-repair-artifact-checks-green.log
.ralph/runs/2026-07-22_201550_repair/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-22_201550_repair/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-22_201550_repair/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-22_201550_repair/execution-plan.md
.ralph/runs/2026-07-22_201550_repair/final-summary.md
.ralph/runs/2026-07-22_201550_repair/orchestrator-ownership-check.md
.ralph/runs/2026-07-22_201550_repair/preflight-results.md
.ralph/runs/2026-07-22_201550_repair/prompt.md
.ralph/runs/2026-07-22_201550_repair/protected-paths-check.md
.ralph/runs/2026-07-22_201550_repair/ralph-artifact-validation.md
.ralph/runs/2026-07-22_201550_repair/review-packet.md
.ralph/runs/2026-07-22_201550_repair/risk-assessment.md
.ralph/runs/2026-07-22_201550_repair/slice-queue-lint.md
.ralph/runs/2026-07-22_201550_repair/slice-status-transition-check.md
docs/working/API_CONTRACTS.md
sfpcl_credit/closure/__init__.py
sfpcl_credit/closure/apps.py
sfpcl_credit/closure/migrations/0001_initial.py
sfpcl_credit/closure/migrations/__init__.py
sfpcl_credit/closure/models.py
sfpcl_credit/closure/modules/__init__.py
sfpcl_credit/closure/modules/loan_closure.py
sfpcl_credit/closure/views.py
sfpcl_credit/config/settings.py
sfpcl_credit/config/urls.py
sfpcl_credit/loans/models.py
sfpcl_credit/monitoring/modules/dpd_monitoring.py
sfpcl_credit/tests/test_closure_api.py
sfpcl_credit/tests/test_default_grace_assessment_api.py
sfpcl_credit/tests/test_default_recovery_postgresql_acceptance.py
sfpcl_credit/tests/test_direct_repayment_posting_api.py
```
