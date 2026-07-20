# Failure Summary

- Run: 2026-07-20_153054_normal_run
- Mode: normal_run
- Slice: 010I-dpd-calculation-and-monitoring-buckets
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=5, skipped=125)
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
Ran 1454 tests in 884.101s

FAILED (errors=5, skipped=125)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 51.992s
  Creating 'default' took 51.939s
  Cloning 'default' took 0.008s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.008s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.009s
Total database teardown took 0.008s
Total run took 936.774s

Duration milliseconds: 937368
Exit code: 1
```

## Changed files (git status)

```
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
sfpcl_credit/config/settings.py
sfpcl_credit/config/urls.py
sfpcl_credit/identity/catalogue.py
sfpcl_credit/tests/test_servicing_postgresql_acceptance.py
.ralph/runs/2026-07-20_153054_normal_run/
sfpcl_credit/monitoring/
sfpcl_credit/tests/test_dpd_monitoring_api.py
```
