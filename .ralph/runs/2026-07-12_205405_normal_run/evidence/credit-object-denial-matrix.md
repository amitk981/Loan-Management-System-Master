# Credit object-denial action/write matrix

All rows use the persisted application's post-ownership-change facts. Each projection contains
exactly `action_code`, `label`, `enabled`, `disabled_reason`, `required_permission`, and
`required_role`. Every public write raises `CreditModuleObjectAccessDenied` with category
`OBJECT_ACCESS_DENIED`, and every before/after comparison uses `full_credit_evidence()` across the
application, eligibility assessment, loan-limit assessment, appraisal, risk assessment, review
history, rejection note, approval case, audit log, and workflow event rows.

| Public action | Executable case | Projection | Public write | Evidence delta |
|---|---|---|---|---|
| `credit.eligibility.run` | `EligibilityActionWriteMatrixTests.test_object_scope_projects_disabled_action_before_matching_public_run_denial` | disabled: `You do not have access to this loan application.` | eligibility `run` denied / `OBJECT_ACCESS_DENIED` | zero |
| `credit.loan_limit.calculate` | `LoanLimitActionWriteMatrixTests.test_state_stale_state_and_object_scope_execute_calculation_without_loser_evidence` | same exact disabled reason | loan-limit `calculate_for_application` denied / `OBJECT_ACCESS_DENIED` | zero |
| `credit.appraisal.create` | `AppraisalActionWriteMatrixTests.test_create_update_revalidate_and_submit_execute_state_provenance_and_scope_denials` | same exact disabled reason | appraisal `create_or_update` denied / `OBJECT_ACCESS_DENIED` | zero |
| `credit.appraisal.update` | same executable case | same exact disabled reason | appraisal partial `create_or_update` denied / `OBJECT_ACCESS_DENIED` | zero |
| `revalidate_appraisal_prerequisites` | `AppraisalActionWriteMatrixTests.test_revalidate_and_submit_object_scope_denials_preserve_the_draft` | same exact disabled reason | appraisal `revalidate_prerequisites` denied / `OBJECT_ACCESS_DENIED` | zero |
| `credit.appraisal.submit_review` | same executable case | same exact disabled reason | appraisal `submit_for_review` denied / `OBJECT_ACCESS_DENIED` | zero |
| `credit.appraisal.review` | `AppraisalActionWriteMatrixTests.test_review_object_scope_denial_follows_an_enabled_projection_without_evidence` | same exact disabled reason | appraisal `review` denied / `OBJECT_ACCESS_DENIED` | zero |
| `credit.appraisal.submit_sanction` | `SanctionActionWriteMatrixTests.test_permission_object_scope_and_stale_state_invoke_the_public_sanction_write` | same exact disabled reason | sanction `submit_reviewed_appraisal` denied / `OBJECT_ACCESS_DENIED` | zero |

The focused HTTP regressions additionally preserve standard `403` envelopes for eligibility,
loan-limit, appraisal, and pending-sanction reads/writes; the action projection is exercised only
through the public domain seam and does not serialize a denied application or credit resource.
