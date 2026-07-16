# Failure Summary

- Run: 2026-07-16_190027_normal_run
- Mode: normal_run
- Slice: 009B3A-sap-model-owner-and-state-migration
- Failed checks: 2

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=6, skipped=52)
```

## Last 50 lines: typecheck-results.md

```
# typecheck Results

Command: npm run typecheck --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 typecheck
> tsc --noEmit

playwright.browser.ts(1,28): error TS2307: Cannot find module 'node:fs' or its corresponding type declarations.
playwright.browser.ts(46,35): error TS2580: Cannot find name 'process'. Do you need to install type definitions for node? Try `npm i --save-dev @types/node`.

Duration milliseconds: 4523
Exit code: 2
```

## Last 50 lines: backend-coverage-results.md

```
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/models/manager.py", line 87, in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/models/query.py", line 679, in create
    obj.save(force_insert=True, using=self.db)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/models/base.py", line 822, in save
    self.save_base(
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/models/base.py", line 909, in save_base
    updated = self._save_table(
              ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/models/base.py", line 1071, in _save_table
    results = self._do_insert(
              ^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/models/base.py", line 1112, in _do_insert
    return manager._insert(
           ^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/models/manager.py", line 87, in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/models/query.py", line 1847, in _insert
    return query.get_compiler(using=using).execute_sql(returning_fields)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/models/sql/compiler.py", line 1823, in execute_sql
    cursor.execute(sql, params)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/backends/utils.py", line 79, in execute
    return self._execute_with_wrappers(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/backends/utils.py", line 92, in _execute_with_wrappers
    return executor(sql, params, many, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/backends/utils.py", line 100, in _execute
    with self.db.wrap_database_errors:
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/utils.py", line 91, in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/backends/utils.py", line 105, in _execute
    return self.cursor.execute(sql, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/backends/sqlite3/base.py", line 329, in execute
    return super().execute(query, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
django.db.utils.OperationalError: table witnesses has no column named verification_folio_number

----------------------------------------------------------------------
Ran 1008 tests in 390.588s

FAILED (errors=6, skipped=52)
Destroying test database for alias 'default'...

Duration milliseconds: 409801
Exit code: 1
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/009B3A-sap-model-owner-and-state-migration.md
docs/slices/009B3B-sap-policy-adapter-and-dependency-closure.md
docs/slices/009D2-readiness-evidence-and-loan-scope-closure.md
docs/working/HANDOFF.md
docs/working/digests/epic-009-sap-loan-account-disbursement.md
sfpcl_credit/finance/models.py
sfpcl_credit/loans/models.py
sfpcl_credit/sap_workflow/modules/sap_customer_profile.py
.ralph/runs/2026-07-16_190027_normal_run/
sfpcl_credit/sap_workflow/migrations/
sfpcl_credit/sap_workflow/models.py
sfpcl_credit/tests/test_sap_model_ownership_migration.py
```
