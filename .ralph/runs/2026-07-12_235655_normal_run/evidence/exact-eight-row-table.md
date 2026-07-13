# Exact Eight-Row Credit Object-Scope Table

| Action code | Independently selectable test identifier |
|---|---|
| `credit.eligibility.run` | `EligibilityActionWriteMatrixTests.test_object_scope_projects_disabled_action_before_matching_public_run_denial` |
| `credit.loan_limit.calculate` | `LoanLimitActionWriteMatrixTests.test_state_stale_state_and_object_scope_execute_calculation_without_loser_evidence` |
| `credit.appraisal.create` | `AppraisalActionWriteMatrixTests.test_create_object_scope_row` |
| `credit.appraisal.update` | `AppraisalActionWriteMatrixTests.test_update_object_scope_row` |
| `revalidate_appraisal_prerequisites` | `AppraisalActionWriteMatrixTests.test_revalidate_object_scope_row` |
| `credit.appraisal.submit_review` | `AppraisalActionWriteMatrixTests.test_submit_review_object_scope_row` |
| `credit.appraisal.review` | `AppraisalActionWriteMatrixTests.test_review_object_scope_denial_follows_an_enabled_projection_without_evidence` |
| `credit.appraisal.submit_sanction` | `SanctionActionWriteMatrixTests.test_permission_object_scope_and_stale_state_invoke_the_public_sanction_write` |

Every identifier owns a fresh Django `TestCase` transaction and executes projection, public write,
denial-category, and complete evidence assertions before returning its row result.
