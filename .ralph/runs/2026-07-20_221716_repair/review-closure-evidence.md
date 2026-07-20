# Review Closure Evidence

## Finding Evidence

| Finding ID | Root ID | Permanent Test | RED Evidence | GREEN Evidence |
|---|---|---|---|---|
| AR-010-RATE-001 | ROOT-010-RATE-VERSION-OWNER | sfpcl_credit.tests.test_servicing_financial_owner_closure.RateCurrentDateFinalizerPostgreSQLAcceptanceTests.test_competing_portfolio_runs_keep_stale_account_visible_and_singular | evidence/terminal-logs/rate-finalizer-postgresql-repair-red.log | evidence/terminal-logs/rate-finalizer-postgresql-repair-selector-green.log |

The repair retains the public race seam while replacing its invalid collection expectation with
assertions that distinguish two financial owner identities from one canonical read identity.

## Acceptance Evidence

| Acceptance ID | Test | Evidence |
|---|---|---|
| AC-RATE-F-1 | sfpcl_credit.tests.test_servicing_financial_owner_closure.RateCurrentDateFinalizerTests.test_before_date_after_matrix_aligns_reads_and_interest_consumers | evidence/terminal-logs/rate-finalizer-repair-focused-green.log |
| AC-RATE-F-2 | sfpcl_credit.tests.test_servicing_financial_owner_closure.RateCurrentDateFinalizerTests.test_due_owner_keeps_stale_account_in_collection_and_detail | evidence/terminal-logs/rate-finalizer-repair-focused-green.log |
| AC-RATE-F-3 | sfpcl_credit.tests.test_servicing_financial_owner_closure.RateCurrentDateFinalizerTests.test_public_owner_retains_one_immutable_idempotency_decision | evidence/terminal-logs/rate-finalizer-repair-focused-green.log |
| AC-RATE-F-4 | sfpcl_credit.tests.test_servicing_financial_owner_closure.RateCurrentDateFinalizerPostgreSQLAcceptanceTests.test_one_account_exact_due_run_race_retains_one_replayable_decision | evidence/terminal-logs/rate-finalizer-postgresql-repair-green-1.log |
| AC-RATE-F-5 | sfpcl_credit.tests.test_servicing_financial_owner_closure.RateCurrentDateFinalizerPostgreSQLAcceptanceTests.test_competing_portfolio_runs_keep_stale_account_visible_and_singular | evidence/terminal-logs/rate-finalizer-postgresql-repair-selector-green.log |

The exact declared five-test PostgreSQL class passed twice against PostgreSQL 14.20.
