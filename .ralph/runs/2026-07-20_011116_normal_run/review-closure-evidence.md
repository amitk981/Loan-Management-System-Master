# Review Finding Closure Evidence

## Finding Evidence

| Finding ID | Root ID | Permanent Test | RED Evidence | GREEN Evidence |
|---|---|---|---|---|
| AR-010-ALLOCATION-001 | ROOT-010-ALLOCATION-ADMISSION | `sfpcl_credit.tests.test_repayment_adjustment_api.RepaymentAdjustmentApiTests.test_allocation_requires_posted_sap_decision_and_idempotency_key` | `evidence/terminal-logs/allocation-admission-red.log` | `evidence/terminal-logs/acceptance-matrix-green.log` |

## Acceptance Evidence

| Acceptance ID | Test | Evidence |
|---|---|---|
| AC-ALLOC-1 | `sfpcl_credit.tests.test_repayment_adjustment_api.RepaymentAdjustmentApiTests.test_allocation_requires_posted_sap_decision_and_idempotency_key` | `evidence/terminal-logs/acceptance-matrix-green.log` |
| AC-ALLOC-2 | `sfpcl_credit.tests.test_repayment_adjustment_api.RepaymentAdjustmentPostgreSQLAcceptanceTests.test_cross_receipt_idempotency_reuse_is_zero_write_conflict` | `evidence/terminal-logs/postgresql-adjustment-run-1.log` |
| AC-ALLOC-3 | `sfpcl_credit.tests.test_repayment_adjustment_api.RepaymentAdjustmentApiTests.test_allocation_fails_closed_when_schedule_cannot_absorb_exact_amount` | `evidence/terminal-logs/acceptance-matrix-green.log` |
| AC-ALLOC-4 | `sfpcl_credit.tests.test_repayment_adjustment_api.RepaymentAdjustmentApiTests.test_manual_exception_allocation_requires_exact_terminal_approval` | `evidence/terminal-logs/acceptance-matrix-green.log` |
| AC-ALLOC-5 | `sfpcl_credit.tests.test_repayment_adjustment_api.RepaymentAdjustmentApiTests.test_reversal_appends_compensating_truth_and_preserves_original_rows` | `evidence/terminal-logs/acceptance-matrix-green.log` |
| AC-ALLOC-6 | `sfpcl_credit.tests.test_repayment_adjustment_api.RepaymentAdjustmentCatalogueTests.test_default_role_catalogue_grants_only_source_allocation_authority` | `evidence/terminal-logs/acceptance-matrix-green.log` |
