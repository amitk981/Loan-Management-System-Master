# Failure Summary

- Run: 2026-07-22_095219_repair
- Mode: repair
- Slice: 011A-default-case-opening
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=1, skipped=154)
execution-plan.md:Failed validation domain: backend complete-suite coverage, specifically
risk-assessment.md:- Failed validation domain: backend complete-suite coverage; one historical migration ownership test
```

## Last 50 lines: backend-coverage-results.md

```
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/models/query.py", line 1847, in _insert
    return query.get_compiler(using=using).execute_sql(returning_fields)
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/models/sql/compiler.py", line 1823, in execute_sql
    cursor.execute(sql, params)
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/backends/utils.py", line 79, in execute
    return self._execute_with_wrappers(
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/backends/utils.py", line 92, in _execute_with_wrappers
    return executor(sql, params, many, context)
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/backends/utils.py", line 100, in _execute
    with self.db.wrap_database_errors:
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/utils.py", line 91, in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/backends/utils.py", line 105, in _execute
    return self.cursor.execute(sql, params)
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/backends/sqlite3/base.py", line 329, in execute
    return super().execute(query, params)
    ^^^^^^^^^^^^^^^^^
django.db.utils.OperationalError: table witnesses has no column named verification_folio_number

----------------------------------------------------------------------
Ran 1569 tests in 1222.779s

FAILED (errors=1, skipped=154)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 61.500s
  Creating 'default' took 61.384s
  Cloning 'default' took 0.014s
  Cloning 'default' took 0.014s
  Cloning 'default' took 0.022s
  Cloning 'default' took 0.018s
  Cloning 'default' took 0.026s
  Cloning 'default' took 0.020s
Total database teardown took 0.045s
Total run took 1284.960s

Duration milliseconds: 1285876
Exit code: 1
```

## Changed files (git status)

```
.ralph/runs/2026-07-22_090320_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-22_090320_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-22_090320_normal_run/backend-check-results.md
.ralph/runs/2026-07-22_090320_normal_run/backend-coverage-results.md
.ralph/runs/2026-07-22_090320_normal_run/backend-impacted-results.md
.ralph/runs/2026-07-22_090320_normal_run/backend-migrations-results.md
.ralph/runs/2026-07-22_090320_normal_run/backend-test-results.md
.ralph/runs/2026-07-22_090320_normal_run/backend-validation-lane-results.md
.ralph/runs/2026-07-22_090320_normal_run/build-results.md
.ralph/runs/2026-07-22_090320_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-22_090320_normal_run/candidate-hash-results.md
.ralph/runs/2026-07-22_090320_normal_run/changed-files.txt
.ralph/runs/2026-07-22_090320_normal_run/codex-settings.md
.ralph/runs/2026-07-22_090320_normal_run/diff-limits-results.md
.ralph/runs/2026-07-22_090320_normal_run/e2e-results.md
.ralph/runs/2026-07-22_090320_normal_run/evidence/api-response-examples.md
.ralph/runs/2026-07-22_090320_normal_run/evidence/postgresql-environment-validation.md
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
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/postgresql-acceptance-validation-1.txt
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/postgresql-acceptance-validation-2.txt
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/red-01-missed-principal-open.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/red-03-detail-list.log
.ralph/runs/2026-07-22_090320_normal_run/evidence/terminal-logs/reverse-consumers.log
.ralph/runs/2026-07-22_090320_normal_run/execution-plan.md
.ralph/runs/2026-07-22_090320_normal_run/failure-summary.md
.ralph/runs/2026-07-22_090320_normal_run/final-summary.md
.ralph/runs/2026-07-22_090320_normal_run/install-results.md
.ralph/runs/2026-07-22_090320_normal_run/lint-results.md
.ralph/runs/2026-07-22_090320_normal_run/no-op-check-results.md
.ralph/runs/2026-07-22_090320_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-22_090320_normal_run/postgresql-acceptance-results.md
.ralph/runs/2026-07-22_090320_normal_run/preflight-results.md
.ralph/runs/2026-07-22_090320_normal_run/prompt.md
.ralph/runs/2026-07-22_090320_normal_run/protected-paths-check.md
.ralph/runs/2026-07-22_090320_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-22_090320_normal_run/review-packet.md
.ralph/runs/2026-07-22_090320_normal_run/risk-assessment.md
.ralph/runs/2026-07-22_090320_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-22_090320_normal_run/slice-status-transition-check.md
.ralph/runs/2026-07-22_090320_normal_run/test-results.md
.ralph/runs/2026-07-22_090320_normal_run/typecheck-results.md
.ralph/runs/2026-07-22_090320_normal_run/validated-commit-candidate.sha256
.ralph/runs/2026-07-22_095219_repair/agent-declared-result-check.md
.ralph/runs/2026-07-22_095219_repair/artifact-quality-check.md
.ralph/runs/2026-07-22_095219_repair/candidate-fast-check-results.md
.ralph/runs/2026-07-22_095219_repair/changed-files.txt
.ralph/runs/2026-07-22_095219_repair/codex-settings.md
.ralph/runs/2026-07-22_095219_repair/diff-limits-results.md
.ralph/runs/2026-07-22_095219_repair/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-22_095219_repair/evidence/terminal-logs/green-credit-ownership-migration.log
.ralph/runs/2026-07-22_095219_repair/evidence/terminal-logs/migration-domain-regression.log
.ralph/runs/2026-07-22_095219_repair/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-22_095219_repair/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-22_095219_repair/evidence/terminal-logs/red-credit-ownership-migration.log
.ralph/runs/2026-07-22_095219_repair/execution-plan.md
.ralph/runs/2026-07-22_095219_repair/final-summary.md
.ralph/runs/2026-07-22_095219_repair/orchestrator-ownership-check.md
.ralph/runs/2026-07-22_095219_repair/preflight-results.md
.ralph/runs/2026-07-22_095219_repair/prompt.md
.ralph/runs/2026-07-22_095219_repair/protected-paths-check.md
.ralph/runs/2026-07-22_095219_repair/ralph-artifact-validation.md
.ralph/runs/2026-07-22_095219_repair/review-packet.md
.ralph/runs/2026-07-22_095219_repair/risk-assessment.md
.ralph/runs/2026-07-22_095219_repair/slice-queue-lint.md
.ralph/runs/2026-07-22_095219_repair/slice-status-transition-check.md
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
sfpcl_credit/tests/test_credit_model_ownership_migration.py
sfpcl_credit/tests/test_default_case_opening_api.py
sfpcl_credit/tests/test_default_recovery_postgresql_acceptance.py
```
