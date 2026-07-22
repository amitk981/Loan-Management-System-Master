# Failure Summary

- Run: 2026-07-23_024025_repair
- Mode: repair
- Slice: 011K-compliance-control-tracker-foundation
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=1, skipped=171)
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
Ran 1664 tests in 1361.574s

FAILED (errors=1, skipped=171)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 72.856s
  Creating 'default' took 72.775s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.014s
  Cloning 'default' took 0.014s
  Cloning 'default' took 0.014s
  Cloning 'default' took 0.015s
  Cloning 'default' took 0.013s
Total database teardown took 0.016s
Total run took 1435.003s

Duration milliseconds: 1435655
Exit code: 1
```

## Changed files (git status)

```
.ralph/runs/2026-07-23_014100_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-23_014100_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-23_014100_normal_run/backend-check-results.md
.ralph/runs/2026-07-23_014100_normal_run/backend-coverage-results.md
.ralph/runs/2026-07-23_014100_normal_run/backend-impacted-results.md
.ralph/runs/2026-07-23_014100_normal_run/backend-migrations-results.md
.ralph/runs/2026-07-23_014100_normal_run/backend-test-results.md
.ralph/runs/2026-07-23_014100_normal_run/backend-validation-lane-results.md
.ralph/runs/2026-07-23_014100_normal_run/build-results.md
.ralph/runs/2026-07-23_014100_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-23_014100_normal_run/candidate-hash-results.md
.ralph/runs/2026-07-23_014100_normal_run/changed-files.txt
.ralph/runs/2026-07-23_014100_normal_run/codex-settings.md
.ralph/runs/2026-07-23_014100_normal_run/diff-limits-results.md
.ralph/runs/2026-07-23_014100_normal_run/e2e-results.md
.ralph/runs/2026-07-23_014100_normal_run/evidence/postgresql-environment-validation.md
.ralph/runs/2026-07-23_014100_normal_run/evidence/terminal-logs/01-task-generation-red.txt
.ralph/runs/2026-07-23_014100_normal_run/evidence/terminal-logs/02-task-generation-green.txt
.ralph/runs/2026-07-23_014100_normal_run/evidence/terminal-logs/03-frequency-escalation-red-green.txt
.ralph/runs/2026-07-23_014100_normal_run/evidence/terminal-logs/04-evidence-api-red-green.txt
.ralph/runs/2026-07-23_014100_normal_run/evidence/terminal-logs/05-final-focused-gates.txt
.ralph/runs/2026-07-23_014100_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-23_014100_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-23_014100_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-23_014100_normal_run/evidence/terminal-logs/postgresql-acceptance-validation-1.txt
.ralph/runs/2026-07-23_014100_normal_run/evidence/terminal-logs/postgresql-acceptance-validation-2.txt
.ralph/runs/2026-07-23_014100_normal_run/execution-plan.md
.ralph/runs/2026-07-23_014100_normal_run/failure-summary.md
.ralph/runs/2026-07-23_014100_normal_run/final-summary.md
.ralph/runs/2026-07-23_014100_normal_run/install-results.md
.ralph/runs/2026-07-23_014100_normal_run/lint-results.md
.ralph/runs/2026-07-23_014100_normal_run/no-op-check-results.md
.ralph/runs/2026-07-23_014100_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-23_014100_normal_run/postgresql-acceptance-results.md
.ralph/runs/2026-07-23_014100_normal_run/preflight-results.md
.ralph/runs/2026-07-23_014100_normal_run/prompt.md
.ralph/runs/2026-07-23_014100_normal_run/protected-paths-check.md
.ralph/runs/2026-07-23_014100_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-23_014100_normal_run/review-packet.md
.ralph/runs/2026-07-23_014100_normal_run/risk-assessment.md
.ralph/runs/2026-07-23_014100_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-23_014100_normal_run/slice-status-transition-check.md
.ralph/runs/2026-07-23_014100_normal_run/test-results.md
.ralph/runs/2026-07-23_014100_normal_run/typecheck-results.md
.ralph/runs/2026-07-23_014100_normal_run/validated-commit-candidate.sha256
.ralph/runs/2026-07-23_024025_repair/agent-declared-result-check.md
.ralph/runs/2026-07-23_024025_repair/artifact-quality-check.md
.ralph/runs/2026-07-23_024025_repair/candidate-fast-check-results.md
.ralph/runs/2026-07-23_024025_repair/changed-files.txt
.ralph/runs/2026-07-23_024025_repair/codex-settings.md
.ralph/runs/2026-07-23_024025_repair/diff-limits-results.md
.ralph/runs/2026-07-23_024025_repair/evidence/terminal-logs/01-credit-ownership-migration-red.txt
.ralph/runs/2026-07-23_024025_repair/evidence/terminal-logs/02-credit-ownership-migration-green.txt
.ralph/runs/2026-07-23_024025_repair/evidence/terminal-logs/03-focused-repair-gates.txt
.ralph/runs/2026-07-23_024025_repair/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-23_024025_repair/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-23_024025_repair/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-23_024025_repair/execution-plan.md
.ralph/runs/2026-07-23_024025_repair/final-summary.md
.ralph/runs/2026-07-23_024025_repair/orchestrator-ownership-check.md
.ralph/runs/2026-07-23_024025_repair/preflight-results.md
.ralph/runs/2026-07-23_024025_repair/prompt.md
.ralph/runs/2026-07-23_024025_repair/protected-paths-check.md
.ralph/runs/2026-07-23_024025_repair/ralph-artifact-validation.md
.ralph/runs/2026-07-23_024025_repair/review-packet.md
.ralph/runs/2026-07-23_024025_repair/risk-assessment.md
.ralph/runs/2026-07-23_024025_repair/slice-queue-lint.md
.ralph/runs/2026-07-23_024025_repair/slice-status-transition-check.md
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
sfpcl_credit/closure/compliance_evidence_facade.py
sfpcl_credit/compliance/__init__.py
sfpcl_credit/compliance/apps.py
sfpcl_credit/compliance/catalogue.py
sfpcl_credit/compliance/migrations/0001_initial.py
sfpcl_credit/compliance/migrations/__init__.py
sfpcl_credit/compliance/models.py
sfpcl_credit/compliance/modules/__init__.py
sfpcl_credit/compliance/modules/compliance_control_tracker.py
sfpcl_credit/compliance/modules/compliance_task_engine.py
sfpcl_credit/compliance/views.py
sfpcl_credit/config/settings.py
sfpcl_credit/config/urls.py
sfpcl_credit/identity/catalogue.py
sfpcl_credit/legal_documents/compliance_evidence_facade.py
sfpcl_credit/recovery/compliance_evidence_facade.py
sfpcl_credit/tests/test_compliance_api.py
sfpcl_credit/tests/test_compliance_postgresql_acceptance.py
sfpcl_credit/tests/test_compliance_task_engine.py
sfpcl_credit/tests/test_credit_model_ownership_migration.py
```
