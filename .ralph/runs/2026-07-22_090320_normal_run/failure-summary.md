# Failure Summary

- Run: 2026-07-22_090320_normal_run
- Mode: normal_run
- Slice: 011A-default-case-opening
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=1, skipped=89)
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
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_090320_normal_run/sfpcl_credit/tests/test_credit_model_ownership_migration.py", line 42, in setUp
    self.identifiers = self._create_pre_move_rows(old_apps)
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_090320_normal_run/sfpcl_credit/tests/test_credit_model_ownership_migration.py", line 146, in _create_pre_move_rows
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
Ran 1484 tests in 835.046s

FAILED (errors=1, skipped=89)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 63.726s
  Creating 'default' took 63.647s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.017s
  Cloning 'default' took 0.018s
  Cloning 'default' took 0.017s
Total database teardown took 0.036s
Total run took 899.662s

Duration milliseconds: 900608
Exit code: 1
```

## Changed files (git status)

```
.ralph/runs/2026-07-22_090320_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-22_090320_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-22_090320_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-22_090320_normal_run/changed-files.txt
.ralph/runs/2026-07-22_090320_normal_run/codex-settings.md
.ralph/runs/2026-07-22_090320_normal_run/diff-limits-results.md
.ralph/runs/2026-07-22_090320_normal_run/evidence/api-response-examples.md
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/catalogue-seed-regression.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/django-check-final.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/django-check.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/focused-default-api-complete.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/focused-default-api-final.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/focused-default-api-final2.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/focused-default-api-rerun.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/focused-default-api.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/fully-paid-no-open.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/green-01-missed-principal-open.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/green-02-exact-replay.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/green-03-detail-list.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/migration-forward-reverse-reapply.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/migration-sync-final.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/migration-sync-final2.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/migration-sync.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/postgres-race-final.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/postgres-race-final2.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/postgres-race.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/red-01-missed-principal-open.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/red-03-detail-list.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/reverse-consumers.log
.ralph/runs/2026-07-22_090320_normal_run/execution-plan.md
.ralph/runs/2026-07-22_090320_normal_run/final-summary.md
.ralph/runs/2026-07-22_090320_normal_run/no-op-check-results.md
.ralph/runs/2026-07-22_090320_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-22_090320_normal_run/preflight-results.md
.ralph/runs/2026-07-22_090320_normal_run/prompt.md
.ralph/runs/2026-07-22_090320_normal_run/protected-paths-check.md
.ralph/runs/2026-07-22_090320_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-22_090320_normal_run/review-packet.md
.ralph/runs/2026-07-22_090320_normal_run/risk-assessment.md
.ralph/runs/2026-07-22_090320_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-22_090320_normal_run/slice-status-transition-check.md
docs/working/API_CONTRACTS.md
sfpcl_credit/config/settings.py
sfpcl_credit/config/urls.py
sfpcl_credit/defaults/__init__.py
sfpcl_credit/defaults/apps.py
sfpcl_credit/defaults/migrations/0001_initial.py
sfpcl_credit/defaults/migrations/__init__.py
sfpcl_credit/defaults/models.py
sfpcl_credit/defaults/modules/__init__.py
sfpcl_credit/defaults/modules/default_workflow.py
sfpcl_credit/defaults/views.py
sfpcl_credit/identity/catalogue.py
sfpcl_credit/tests/test_default_case_opening_api.py
sfpcl_credit/tests/test_default_recovery_postgresql_acceptance.py
```
