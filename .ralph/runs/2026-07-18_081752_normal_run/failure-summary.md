# Failure Summary

- Run: 2026-07-18_081752_normal_run
- Mode: normal_run
- Slice: 009H3BA-communications-dispatcher-outbox-freeze
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=1, skipped=62)
```

## Last 50 lines: backend-coverage-results.md

```
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/models/query.py", line 91, in __iter__
    results = compiler.execute_sql(
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/models/sql/compiler.py", line 1562, in execute_sql
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
django.db.utils.OperationalError: no such table: communication_delivery_outboxes

----------------------------------------------------------------------
Ran 1128 tests in 419.057s

FAILED (errors=1, skipped=62)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 29.339s
  Creating 'default' took 29.211s
  Cloning 'default' took 0.022s
  Cloning 'default' took 0.013s
  Cloning 'default' took 0.017s
  Cloning 'default' took 0.035s
  Cloning 'default' took 0.028s
  Cloning 'default' took 0.012s
Total database teardown took 0.061s
Total run took 448.993s

Duration milliseconds: 449561
Exit code: 1
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/009H3BA-communications-dispatcher-outbox-freeze.md
docs/working/HANDOFF.md
docs/working/digests/epic-009-sap-loan-account-disbursement.md
sfpcl_credit/disbursements/modules/disbursement_advice.py
sfpcl_credit/tests/test_communication_advice_persistence.py
sfpcl_credit/tests/test_disbursement_advice_api.py
.ralph/runs/2026-07-18_081752_normal_run/
sfpcl_credit/communications/modules/
sfpcl_credit/disbursements/modules/disbursement_advice_context.py
```
