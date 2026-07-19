# Failure Summary

- Run: 2026-07-19_233905_normal_run
- Mode: normal_run
- Slice: 010D-bank-statement-matching-unmatched-receipts
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
  - sfpcl_credit.tests.test_servicing_postgresql_acceptance.BankStatementMatchingPostgreSQLAcceptanceTests
- FAIL: first independent run did not satisfy the slice contract and exact count.
- FAIL: second independent run did not satisfy the slice contract and exact count.
- FAIL: PostgreSQL environment evidence is missing.
```

## Changed files (git status)

```
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
sfpcl_credit/config/urls.py
sfpcl_credit/identity/catalogue.py
sfpcl_credit/loans/models.py
sfpcl_credit/loans/modules/direct_repayment_posting.py
sfpcl_credit/loans/views.py
sfpcl_credit/tests/test_servicing_postgresql_acceptance.py
.ralph/runs/2026-07-19_233905_normal_run/
sfpcl_credit/loans/migrations/0005_bankstatementimport_bankstatementline_and_more.py
sfpcl_credit/loans/modules/bank_statement_matching.py
sfpcl_credit/tests/test_bank_statement_matching_api.py
```
