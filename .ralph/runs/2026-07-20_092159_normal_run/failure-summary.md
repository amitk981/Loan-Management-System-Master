# Failure Summary

- Run: 2026-07-20_092159_normal_run
- Mode: normal_run
- Slice: 010H-interest-capitalisation-after-30-april
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

- Contract expected tests: 1
- Contract labels:
  - sfpcl_credit.tests.test_servicing_postgresql_acceptance.InterestCapitalisationPostgreSQLAcceptanceTests
- FAIL: first independent run did not satisfy the slice contract and exact count.
- FAIL: second independent run did not satisfy the slice contract and exact count.
- FAIL: PostgreSQL environment evidence is missing.
```

## Changed files (git status)

```
docs/working/API_CONTRACTS.md
sfpcl_credit/config/urls.py
sfpcl_credit/identity/catalogue.py
sfpcl_credit/interest/models.py
sfpcl_credit/interest/modules/interest_engine.py
sfpcl_credit/interest/views.py
sfpcl_credit/loans/modules/loan_account_read.py
sfpcl_credit/processes/loan_account_360.py
sfpcl_credit/processes/loan_servicing.py
sfpcl_credit/tests/test_servicing_postgresql_acceptance.py
.ralph/runs/2026-07-20_092159_normal_run/
sfpcl_credit/interest/migrations/0003_interestcapitalisation_and_more.py
sfpcl_credit/tests/test_interest_capitalisation_api.py
```
