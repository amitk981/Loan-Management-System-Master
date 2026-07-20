# Review Closure Evidence

## Finding Evidence

| Finding ID | Root ID | Permanent Test | RED Evidence | GREEN Evidence |
|---|---|---|---|---|
| AR-010-ALLOCATION-001 | ROOT-010-ALLOCATION-ADMISSION | sfpcl_credit.tests.test_repayment_allocation_api.RepaymentAllocationApiTests.test_replay_after_later_status_change_returns_frozen_original_response | evidence/terminal-logs/allocation-replay-red.log | evidence/terminal-logs/financial-owner-focused-green.log |
| AR-010-STATEMENT-001 | ROOT-010-STATEMENT-EVIDENCE | sfpcl_credit.tests.test_statement_evidence_owner_scope_closure.StatementEvidenceOwnerScopeClosureTests.test_subsidiary_auto_match_requires_borrower_and_application_facts | evidence/terminal-logs/statement-ambiguity-red.log | evidence/terminal-logs/financial-owner-focused-green.log |
| AR-010-RATE-001 | ROOT-010-RATE-VERSION-OWNER | sfpcl_credit.tests.test_interest_rate_config_api.InterestRateConfigApiTests.test_open_predecessor_cannot_be_closed_before_a_retained_consumption | evidence/terminal-logs/rate-owner-red.log | evidence/terminal-logs/financial-owner-focused-green.log |
| AR-010-LEDGER-001 | ROOT-010-LEDGER-PAGINATION | sfpcl_credit.tests.test_repayment_adjustment_api.RepaymentAdjustmentApiTests.test_reversal_appends_compensating_truth_and_preserves_original_rows | evidence/terminal-logs/ledger-window-red.log | evidence/terminal-logs/financial-owner-focused-green.log |
| AR-010-SERVICING-SEAM-001 | ROOT-010-SERVICING-OWNER-SEAM | sfpcl_credit.tests.test_servicing_financial_owner_closure.ServicingOwnerBuilderTests.test_public_builder_produces_distinct_active_financial_owners | evidence/terminal-logs/servicing-owner-builder-red.log | evidence/terminal-logs/servicing-owner-builder-green.log |

## Acceptance Evidence

| Acceptance ID | Test | Evidence |
|---|---|---|
| AC-FIN-1 | sfpcl_credit.tests.test_repayment_allocation_api.RepaymentAllocationApiTests.test_replay_after_later_status_change_returns_frozen_original_response | evidence/terminal-logs/financial-owner-focused-green.log |
| AC-FIN-2 | sfpcl_credit.tests.test_statement_evidence_owner_scope_closure.StatementEvidenceOwnerScopeClosureTests.test_subsidiary_auto_match_requires_borrower_and_application_facts | evidence/terminal-logs/financial-owner-focused-green.log |
| AC-FIN-3 | sfpcl_credit.tests.test_interest_rate_config_api.InterestRateConfigApiTests.test_active_rate_versions_reject_model_and_queryset_mutation | evidence/terminal-logs/financial-owner-focused-green.log |
| AC-FIN-4 | sfpcl_credit.tests.test_interest_rate_config_api.InterestRateConfigApiTests.test_open_predecessor_cannot_be_closed_before_a_retained_consumption | evidence/terminal-logs/financial-owner-focused-green.log |
| AC-FIN-5 | sfpcl_credit.tests.test_interest_rate_config_api.InterestRateConfigApiTests.test_invoice_and_accrual_consumers_retain_the_historical_rate_snapshot | evidence/terminal-logs/financial-owner-focused-green.log |
| AC-FIN-6 | sfpcl_credit.tests.test_servicing_financial_owner_closure.ServicingOwnerBuilderTests.test_mixed_ledger_windows_are_exact_at_one_twenty_one_and_one_hundred_one | evidence/terminal-logs/ledger-cardinality-green.log |
| AC-FIN-7 | sfpcl_credit.tests.test_servicing_financial_owner_closure.ServicingOwnerBuilderTests.test_public_builder_produces_distinct_active_financial_owners | evidence/terminal-logs/servicing-owner-builder-green.log |

The declared PostgreSQL class is
`sfpcl_credit.tests.test_servicing_financial_owner_closure.ServicingFinancialOwnerPostgreSQLAcceptanceTests`
with exactly five tests. Local SQLite collection skipped those tests truthfully; Ralph's independent
`postgresql-five-race-acceptance` gate owns the required twice-run PostgreSQL result.
