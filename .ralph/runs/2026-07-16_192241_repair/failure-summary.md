# Failure Summary

- Run: 2026-07-16_192241_repair
- Mode: repair
- Slice: 009B3A-sap-model-owner-and-state-migration
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=1, skipped=52)
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
django.db.utils.OperationalError: no such table: sap_customer_codes

----------------------------------------------------------------------
Ran 1008 tests in 515.007s

FAILED (errors=1, skipped=52)
Destroying test database for alias 'default'...

Duration milliseconds: 533921
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
sfpcl-lms/playwright.browser.ts
sfpcl_credit/finance/models.py
sfpcl_credit/loans/models.py
sfpcl_credit/sap_workflow/modules/sap_customer_profile.py
sfpcl_credit/tests/test_credit_model_ownership_migration.py
sfpcl_credit/tests/test_witness_evidence_migration.py
.ralph/runs/2026-07-16_190027_normal_run/
.ralph/runs/2026-07-16_192241_repair/
sfpcl-lms/src/node-fs.d.ts
sfpcl_credit/sap_workflow/migrations/
sfpcl_credit/sap_workflow/models.py
sfpcl_credit/tests/test_sap_model_ownership_migration.py
```
