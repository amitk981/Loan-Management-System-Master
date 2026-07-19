# Failure Summary

- Run: 2026-07-19_135000_normal_run
- Mode: normal_run
- Slice: 009L6-epic-009-owner-selector-equivalence-and-matrix-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=5, skipped=84)
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
django.db.utils.IntegrityError: NOT NULL constraint failed: audit_logs.selector_manifest_json

----------------------------------------------------------------------
Ran 1309 tests in 495.707s

FAILED (errors=5, skipped=84)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 33.584s
  Creating 'default' took 33.538s
  Cloning 'default' took 0.013s
  Cloning 'default' took 0.006s
  Cloning 'default' took 0.006s
  Cloning 'default' took 0.006s
  Cloning 'default' took 0.006s
  Cloning 'default' took 0.007s
Total database teardown took 0.023s
Total run took 529.780s

Duration milliseconds: 531050
Exit code: 1
```

## Changed files (git status)

```
docs/working/API_CONTRACTS.md
sfpcl_credit/disbursements/migrations/0010_enable_pgcrypto_for_exact_selector.py
sfpcl_credit/disbursements/modules/current_disbursement_evidence.py
sfpcl_credit/disbursements/modules/disbursement_initiation.py
sfpcl_credit/identity/models.py
sfpcl_credit/loans/modules/loan_account_lifecycle.py
sfpcl_credit/loans/modules/loan_account_read.py
sfpcl_credit/processes/loan_account_360.py
sfpcl_credit/sap_workflow/modules/sap_customer_code.py
sfpcl_credit/sap_workflow/modules/sap_customer_profile.py
sfpcl_credit/tests/test_epic009_postgresql_acceptance.py
sfpcl_credit/tests/test_loan_account_reads_api.py
sfpcl_credit/tests/test_portal_disbursement_status_api.py
.ralph/runs/2026-07-19_135000_normal_run/
sfpcl_credit/identity/migrations/0004_auditlog_selector_manifest_sha256.py
sfpcl_credit/tests/test_epic009_exact_selector_postgresql.py
sfpcl_credit/tests/test_epic009_owner_selector_equivalence.py
sfpcl_credit/tests/test_pgcrypto_migration_ownership.py
```
