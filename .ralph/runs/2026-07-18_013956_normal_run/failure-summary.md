# Failure Summary

- Run: 2026-07-18_013956_normal_run
- Mode: normal_run
- Slice: 009H3A-communications-advice-persistence-and-provider-identity
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=5, skipped=62)
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
Ran 1123 tests in 265.805s

FAILED (errors=5, skipped=62)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 27.616s
  Creating 'default' took 27.573s
  Cloning 'default' took 0.006s
  Cloning 'default' took 0.007s
  Cloning 'default' took 0.006s
  Cloning 'default' took 0.006s
  Cloning 'default' took 0.007s
  Cloning 'default' took 0.009s
Total database teardown took 0.015s
Total run took 293.944s

Duration milliseconds: 294430
Exit code: 1
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/009H3A-communications-advice-persistence-and-provider-identity.md
docs/working/HANDOFF.md
docs/working/digests/epic-009-sap-loan-account-disbursement.md
sfpcl_credit/communications/adapters.py
sfpcl_credit/communications/models.py
sfpcl_credit/disbursements/models.py
sfpcl_credit/disbursements/modules/disbursement_advice.py
.ralph/runs/2026-07-18_013956_normal_run/
sfpcl_credit/communications/migrations/0004_advice_outbox_and_receipt_owner.py
sfpcl_credit/tests/test_communication_advice_persistence.py
sfpcl_credit/tests/test_communication_receipt_owner_migration.py
```
