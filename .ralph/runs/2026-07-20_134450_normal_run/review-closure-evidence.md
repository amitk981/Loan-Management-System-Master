# Review Closure Evidence

## Finding Evidence

| Finding ID | Root ID | Permanent Test | RED Evidence | GREEN Evidence |
|---|---|---|---|---|
| AR-010-INTEREST-001 | ROOT-010-INTEREST-CALCULATION-OWNER | sfpcl_credit.tests.test_interest_capitalisation_api.InterestCapitalisationApiTests.test_interest_allocation_after_invoice_through_cutoff_reduces_capitalisation_once | evidence/terminal-logs/ac-int-3-cutoff-payment-red.log | evidence/terminal-logs/acceptance-focused-verbose.log |

## Acceptance Evidence

| Acceptance ID | Test | Evidence |
|---|---|---|
| AC-INT-1 | sfpcl_credit.tests.test_interest_invoice_api.InterestInvoiceApiTests.test_generation_segments_each_approved_rate_period_without_retroactive_scalar | evidence/terminal-logs/acceptance-focused-verbose.log |
| AC-INT-2 | sfpcl_credit.tests.test_interest_accrual_api.MonthlyInterestAccrualApiTests.test_single_month_segments_an_approved_mid_month_rate_change | evidence/terminal-logs/acceptance-focused-verbose.log |
| AC-INT-3 | sfpcl_credit.tests.test_interest_capitalisation_api.InterestCapitalisationApiTests.test_interest_allocation_after_invoice_through_cutoff_reduces_capitalisation_once | evidence/terminal-logs/acceptance-focused-verbose.log |
| AC-INT-4 | sfpcl_credit.tests.test_interest_capitalisation_api.InterestCapitalisationApiTests.test_capitalisation_reclassifies_existing_interest_and_schedule_without_total_inflation | evidence/terminal-logs/acceptance-focused-verbose.log |
| AC-INT-5 | sfpcl_credit.tests.test_interest_invoice_api.InterestInvoiceApiTests.test_issue_binds_one_document_communication_job_and_audit_chain | evidence/terminal-logs/acceptance-focused-verbose.log |
| AC-INT-6 | sfpcl_credit.tests.test_interest_invoice_api.InterestInvoiceApiTests.test_issue_binds_one_document_communication_job_and_audit_chain | evidence/terminal-logs/acceptance-focused-verbose.log |
| AC-INT-7 | sfpcl_credit.tests.test_servicing_postgresql_acceptance.InterestAccountingOwnerPostgreSQLAcceptanceTests | evidence/terminal-logs/postgresql-owner-pass-2.log |

## Supplementary Evidence

Additional AC-INT-1 leap/principal evidence is retained in
`evidence/terminal-logs/ac-int-1-principal-leap-green.log`; AC-INT-3's tax/fee exclusion proof is
`evidence/terminal-logs/ac-int-3-interest-only-green.log`; AC-INT-5's accrual and capitalisation
replay proofs are `evidence/terminal-logs/ac-int-5-accrual-replays-green.log` and
`evidence/terminal-logs/ac-int-5-capitalisation-replay-green.log`. The declared PostgreSQL class
passed all five tests twice in `postgresql-owner-pass-1.log` and `postgresql-owner-pass-2.log`.
