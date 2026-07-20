# Failure Summary

- Run: 2026-07-20_204224_normal_run
- Mode: normal_run
- Slice: CR-014-rate-current-date-terminal-finalizer
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
postgresql-acceptance-results.md:- FAIL: first independent run did not satisfy the slice contract and exact count.
postgresql-acceptance-results.md:- FAIL: second independent run did not satisfy the slice contract and exact count.
postgresql-acceptance-results.md:- FAIL: PostgreSQL environment evidence is missing.
```

## Last 50 lines: postgresql-acceptance-results.md

```
# PostgreSQL Acceptance Results

- Contract expected tests: 5
- Contract labels:
  - sfpcl_credit.tests.test_servicing_financial_owner_closure.RateCurrentDateFinalizerPostgreSQLAcceptanceTests
- FAIL: first independent run did not satisfy the slice contract and exact count.
- FAIL: second independent run did not satisfy the slice contract and exact count.
- FAIL: PostgreSQL environment evidence is missing.
```

## Changed files (git status)

```
sfpcl_credit/configurations/models.py
sfpcl_credit/configurations/modules/interest_rate_configuration.py
sfpcl_credit/processes/loan_account_360.py
sfpcl_credit/processes/tasks.py
sfpcl_credit/tests/servicing_builders.py
sfpcl_credit/tests/test_servicing_financial_owner_closure.py
.ralph/runs/2026-07-20_204224_normal_run/
sfpcl_credit/configurations/migrations/0008_current_rate_projection_decision.py
sfpcl_credit/loans/current_rate_projection.py
```
