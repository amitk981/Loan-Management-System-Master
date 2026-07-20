# Failure Summary

- Run: 2026-07-20_225941_normal_run
- Mode: normal_run
- Slice: 010H3-interest-policy-and-reclassification-integrity-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
candidate-hash-results.md:FAIL: candidate content changed while validation was running.
```

## Last 50 lines: candidate-hash-results.md

```
# Candidate Hash Results

Before validation: e8e64bfa60de603f9590e45aaff4967335a91366beb3cdefeed66438e6aabfb4
Commit candidate before validation: f84d0b2595932c3903c30368e33b584c0c57ea298a722d695ba5c9cb78eca87b
After validation: f31b1b5c3127f310a679c07a7bac4029bc4467c7e06ddd3f6f25db1baef96573
FAIL: candidate content changed while validation was running.
```

## Changed files (git status)

```
sfpcl_credit/interest/models.py
sfpcl_credit/interest/modules/as_of_accounting.py
sfpcl_credit/interest/modules/interest_engine.py
sfpcl_credit/tests/servicing_builders.py
sfpcl_credit/tests/test_interest_accrual_api.py
sfpcl_credit/tests/test_interest_capitalisation_api.py
sfpcl_credit/tests/test_interest_invoice_api.py
sfpcl_credit/tests/test_servicing_postgresql_acceptance.py
.ralph/runs/2026-07-20_225941_normal_run/
sfpcl_credit/interest/migrations/0005_interest_calculation_rounding_policy.py
sfpcl_credit/shared/money.py
sfpcl_credit/tests/test_interest_policy_integrity_closure.py
```
