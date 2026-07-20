# Review Closure Evidence

## Finding Evidence

| Finding ID | Root ID | Permanent Test | RED Evidence | GREEN Evidence |
|---|---|---|---|---|
| AR-010-INTEREST-001 | ROOT-010-INTEREST-CALCULATION-OWNER | sfpcl_credit/tests/test_interest_capitalisation_api.py::InterestCapitalisationApiTests::test_interest_allocation_after_invoice_through_cutoff_reduces_capitalisation_once | evidence/terminal-logs/review-closure-finding-red.log | evidence/terminal-logs/review-closure-acceptance-green.log |

## Acceptance Evidence

| Acceptance ID | Test | Evidence |
|---|---|---|
| AC-INT-1 | sfpcl_credit/tests/test_interest_invoice_api.py::InterestInvoiceApiTests::test_generation_segments_each_approved_rate_period_without_retroactive_scalar | evidence/terminal-logs/review-closure-acceptance-green.log |
| AC-INT-2 | sfpcl_credit/tests/test_interest_accrual_api.py::MonthlyInterestAccrualApiTests::test_single_month_segments_an_approved_mid_month_rate_change | evidence/terminal-logs/review-closure-acceptance-green.log |
| AC-INT-3 | sfpcl_credit/tests/test_interest_capitalisation_api.py::InterestCapitalisationApiTests::test_interest_allocation_after_invoice_through_cutoff_reduces_capitalisation_once | evidence/terminal-logs/review-closure-acceptance-green.log |
| AC-INT-4 | sfpcl_credit/tests/test_interest_capitalisation_api.py::InterestCapitalisationApiTests::test_capitalisation_reclassifies_existing_interest_and_schedule_without_total_inflation | evidence/terminal-logs/review-closure-acceptance-green.log |
| AC-INT-5 | sfpcl_credit/tests/test_interest_invoice_api.py::InterestInvoiceApiTests::test_issue_binds_one_document_communication_job_and_audit_chain | evidence/terminal-logs/review-closure-acceptance-green.log |
| AC-INT-6 | sfpcl_credit/tests/test_interest_invoice_api.py::InterestInvoiceApiTests::test_issue_binds_one_document_communication_job_and_audit_chain | evidence/terminal-logs/review-closure-acceptance-green.log |
| AC-INT-7 | sfpcl_credit/tests/test_servicing_postgresql_acceptance.py::InterestAccountingOwnerPostgreSQLAcceptanceTests::test_partial_delivery_replay_and_reverse_consumers_keep_original_truth | evidence/terminal-logs/review-closure-postgresql-green.log |
