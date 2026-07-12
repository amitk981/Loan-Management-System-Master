# Failure Summary

- Run: 2026-07-12_130806_normal_run
- Mode: normal_run
- Slice: 006X5-credit-public-action-write-matrix-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
postgresql-acceptance-results.md:- FAIL: first independent run did not satisfy all acceptance predicates.
postgresql-acceptance-results.md:- FAIL: second independent run did not satisfy all acceptance predicates.
postgresql-acceptance-results.md:- FAIL: PostgreSQL environment evidence is missing.
```

## Last 50 lines: postgresql-acceptance-results.md

```
# PostgreSQL Acceptance Results

- FAIL: first independent run did not satisfy all acceptance predicates.
- FAIL: second independent run did not satisfy all acceptance predicates.
- FAIL: PostgreSQL environment evidence is missing.
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/006X5-credit-public-action-write-matrix-closure.md
docs/working/HANDOFF.md
docs/working/digests/epic-006-eligibility-loan-limit-appraisal.md
sfpcl_credit/credit/modules/loan_limit_calculator.py
sfpcl_credit/tests/test_credit_action_parity_matrix.py
sfpcl_credit/tests/test_sanction_submission_api.py
.ralph/runs/2026-07-12_130806_normal_run/
```
