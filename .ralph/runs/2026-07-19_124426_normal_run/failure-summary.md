# Failure Summary

- Run: 2026-07-19_124426_normal_run
- Mode: normal_run
- Slice: 009L5-epic-009-exact-selector-and-consumer-parity-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=18, skipped=82)
```

## Last 50 lines: backend-coverage-results.md

```
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/contrib/postgres/operations.py", line 46, in database_backwards
    if self.extension_exists(schema_editor, self.name):
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/contrib/postgres/operations.py", line 56, in extension_exists
    cursor.execute(
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
django.db.utils.OperationalError: no such table: pg_extension

----------------------------------------------------------------------
Ran 1294 tests in 270.160s

FAILED (errors=18, skipped=82)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 32.685s
  Creating 'default' took 32.620s
  Cloning 'default' took 0.007s
  Cloning 'default' took 0.007s
  Cloning 'default' took 0.007s
  Cloning 'default' took 0.023s
  Cloning 'default' took 0.007s
  Cloning 'default' took 0.014s
Total database teardown took 0.007s
Total run took 303.436s

Duration milliseconds: 304069
Exit code: 1
```

## Changed files (git status)

```
docs/working/API_CONTRACTS.md
sfpcl_credit/disbursements/modules/current_disbursement_evidence.py
sfpcl_credit/loans/modules/loan_account_lifecycle.py
sfpcl_credit/processes/disbursement_workspace.py
sfpcl_credit/processes/loan_account_360.py
sfpcl_credit/processes/portal_disbursement_status.py
sfpcl_credit/sap_workflow/modules/sap_customer_profile.py
sfpcl_credit/tests/test_disbursement_workspace_api.py
sfpcl_credit/tests/test_loan_account_reads_api.py
sfpcl_credit/tests/test_portal_disbursement_status_api.py
.ralph/runs/2026-07-19_124426_normal_run/
sfpcl_credit/disbursements/migrations/0010_enable_pgcrypto_for_exact_selector.py
```
