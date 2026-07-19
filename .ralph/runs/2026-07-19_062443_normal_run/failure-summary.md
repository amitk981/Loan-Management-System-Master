# Failure Summary

- Run: 2026-07-19_062443_normal_run
- Mode: normal_run
- Slice: 009L-epic-009-staff-workflow-and-sap-posting-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=1, skipped=80)
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
django.db.utils.OperationalError: no such table: initial_loan_payment_sap_postings

----------------------------------------------------------------------
Ran 1277 tests in 491.300s

FAILED (errors=1, skipped=80)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 31.445s
  Creating 'default' took 31.406s
  Cloning 'default' took 0.007s
  Cloning 'default' took 0.006s
  Cloning 'default' took 0.006s
  Cloning 'default' took 0.006s
  Cloning 'default' took 0.006s
  Cloning 'default' took 0.007s
Total database teardown took 0.005s
Total run took 523.333s

Duration milliseconds: 523966
Exit code: 1
```

## Changed files (git status)

```
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
docs/working/digests/epic-009-sap-loan-account-disbursement.md
sfpcl-lms/src/pages/disbursement/DisbursementHub.tsx
sfpcl-lms/src/pages/loan-accounts/LoanAccount360.test.tsx
sfpcl-lms/src/pages/loan-accounts/LoanAccount360.tsx
sfpcl-lms/src/services/disbursementApi.test.ts
sfpcl-lms/src/services/disbursementApi.ts
sfpcl_credit/disbursements/models.py
sfpcl_credit/disbursements/modules/disbursement_transfer_success.py
sfpcl_credit/processes/disbursement_workspace.py
sfpcl_credit/processes/loan_account_360.py
sfpcl_credit/sap_workflow/modules/sap_customer_profile.py
sfpcl_credit/tests/test_disbursement_transfer_success_api.py
sfpcl_credit/tests/test_disbursement_workspace_api.py
sfpcl_credit/tests/test_loan_account_reads_api.py
.ralph/runs/2026-07-19_062443_normal_run/
sfpcl-lms/e2e/epic-009-staff-disbursement-closure.e2e.spec.ts
sfpcl_credit/disbursements/migrations/0008_initial_loan_payment_sap_posting.py
```
