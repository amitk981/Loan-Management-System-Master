# Review Closure Evidence

## Finding Evidence

| Finding ID | Root ID | Permanent Test | RED Evidence | GREEN Evidence |
|---|---|---|---|---|
| AR-010-RATE-001 | ROOT-010-RATE-VERSION-OWNER | sfpcl_credit.tests.test_servicing_financial_owner_closure.RateEffectiveDatePostgreSQLAcceptanceTests.test_active_rate_write_paths_require_the_canonical_approval_decision | evidence/terminal-logs/ac-rate-1-red.log | evidence/terminal-logs/ac-rate-1-green.log |

## Acceptance Evidence

| Acceptance ID | Test | Evidence |
|---|---|---|
| AC-RATE-1 | sfpcl_credit.tests.test_servicing_financial_owner_closure.RateEffectiveDatePostgreSQLAcceptanceTests.test_active_rate_write_paths_require_the_canonical_approval_decision | evidence/terminal-logs/ac-rate-1-green.log |
| AC-RATE-2 | sfpcl_credit.tests.test_servicing_financial_owner_closure.RateEffectiveDatePostgreSQLAcceptanceTests.test_future_activation_waits_for_its_effective_date_in_the_loan_projection | evidence/terminal-logs/ac-rate-2-green.log |
| AC-RATE-3 | sfpcl_credit.tests.test_servicing_financial_owner_closure.RateEffectiveDatePostgreSQLAcceptanceTests.test_consumed_boundary_and_competing_successors_retain_one_decision | evidence/terminal-logs/postgresql-acceptance-run-1.log |
| AC-RATE-4 | sfpcl_credit.tests.test_servicing_financial_owner_closure.RateEffectiveDatePostgreSQLAcceptanceTests.test_consumed_boundary_and_competing_successors_retain_one_decision | evidence/terminal-logs/ac-rate-3-green.log |

The callable, audited due-date projection operation is additionally proven by
`RateEffectiveDatePostgreSQLAcceptanceTests.test_due_date_projection_convergence_is_public_idempotent_and_audited`
in `evidence/terminal-logs/ac-rate-2-convergence-green.log`.
