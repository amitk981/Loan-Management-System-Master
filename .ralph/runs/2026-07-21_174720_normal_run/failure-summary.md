# Failure Summary

- Run: 2026-07-21_174720_normal_run
- Mode: normal_run
- Slice: 010N-global-search-api-and-ui
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=1, skipped=23)
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
django.db.utils.IntegrityError: NOT NULL constraint failed: members.aadhaar_last4

----------------------------------------------------------------------
Ran 1312 tests in 280.827s

FAILED (errors=1, skipped=23)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 57.883s
  Creating 'default' took 57.823s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.011s
Total database teardown took 0.007s
Total run took 339.473s

Duration milliseconds: 340104
Exit code: 1
```

## Changed files (git status)

```
.ralph/runs/2026-07-21_174720_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-21_174720_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-21_174720_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-21_174720_normal_run/changed-files.txt
.ralph/runs/2026-07-21_174720_normal_run/codex-settings.md
.ralph/runs/2026-07-21_174720_normal_run/diff-limits-results.md
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/backend-check.log
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/backend-focused-final.log
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/backend-global-search-green-attempt-1.log
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/backend-global-search-green.log
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/backend-global-search-red.log
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/backend-member-reverse-consumers.log
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/backend-migrations-check.log
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/frontend-build.log
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/frontend-focused-final.log
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/frontend-global-search-green.log
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/frontend-global-search-pagination-red.log
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/frontend-global-search-red.log
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/frontend-lint.log
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/frontend-typecheck.log
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/global-search-playwright-collection.log
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/mock-sensitive-removal-proof.log
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-21_174720_normal_run/evidence/terminal-logs/scope-and-diff-proof.log
.ralph/runs/2026-07-21_174720_normal_run/execution-plan.md
.ralph/runs/2026-07-21_174720_normal_run/final-summary.md
.ralph/runs/2026-07-21_174720_normal_run/no-op-check-results.md
.ralph/runs/2026-07-21_174720_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-21_174720_normal_run/preflight-results.md
.ralph/runs/2026-07-21_174720_normal_run/prompt.md
.ralph/runs/2026-07-21_174720_normal_run/protected-paths-check.md
.ralph/runs/2026-07-21_174720_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-21_174720_normal_run/review-packet.md
.ralph/runs/2026-07-21_174720_normal_run/risk-assessment.md
.ralph/runs/2026-07-21_174720_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-21_174720_normal_run/slice-status-transition-check.md
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
docs/working/PROTOTYPE_GAP_REPORT.md
docs/working/PROTOTYPE_INVENTORY.md
sfpcl-lms/e2e/global-search.e2e.spec.ts
sfpcl-lms/src/components/layout/Header.search.test.tsx
sfpcl-lms/src/components/layout/Header.tsx
sfpcl-lms/src/pages/search/GlobalSearchResults.test.tsx
sfpcl-lms/src/pages/search/GlobalSearchResults.tsx
sfpcl-lms/src/services/globalSearchApi.ts
sfpcl_credit/config/urls.py
sfpcl_credit/members/migrations/0015_member_aadhaar_last4.py
sfpcl_credit/members/models.py
sfpcl_credit/members/modules/member_registry.py
sfpcl_credit/members/services.py
sfpcl_credit/processes/global_search.py
sfpcl_credit/search_views.py
sfpcl_credit/tests/test_global_search_api.py
```
