# Credit Action / Write Trace

| Projected action | Public write | Shared authority / denial proof | Success / concurrency proof |
|---|---|---|---|
| `credit.eligibility.run` | `EligibilityAssessmentModule.run` | `evaluate_eligibility_run`; formal LO reference, complete documentation, credit stage, reference-generated state, object scope and permission; `CreditEligibilityModuleTests.test_eligibility_action_and_write_share_the_locked_transition_evaluation` | eligible/ineligible/pending runs plus rollback tests in `CreditEligibilityModuleTests` |
| `credit.loan_limit.calculate` | `LoanLimitCalculator.calculate_for_application` | `evaluate_loan_limit_calculation`; stored eligible result, no appraisal, object scope and permission | `CreditEligibilityModuleTests.test_loan_limit_calculates_through_module_with_one_public_audit_projection`; two PostgreSQL loan-limit races |
| `credit.appraisal.create` | `AppraisalWorkflow.create_or_update(partial=False)` | loan-limit projection plus create/risk permissions; frozen eligible/limit source facts | appraisal create/source/provenance tests in `AppraisalApiTests` |
| `credit.appraisal.update` | `AppraisalWorkflow.create_or_update(partial=True)` | `evaluate_appraisal_update`; exact permission denial now matches projection; draft state, risk authority, object scope | 006X4 matrix plus stale patch/rejected-review PostgreSQL race |
| `revalidate_appraisal_prerequisites` | `AppraisalWorkflow.revalidate_prerequisites` | `evaluate_appraisal_revalidation`; update+risk authority, legacy provenance and non-terminal state | legacy draft/pending/reviewed and rollback tests in `AppraisalApiTests` |
| `credit.appraisal.submit_review` | `AppraisalWorkflow.submit_for_review` | `evaluate_appraisal_submission`; complete verified draft and exact permission | submit, validation, rollback and returned-cycle tests in `AppraisalApiTests` |
| `credit.appraisal.review` (`reviewed`) | `AppraisalWorkflow.review(decision="reviewed")` | `evaluate_appraisal_review`; Credit Manager role, exact permission/object scope, maker-checker, verified provenance | review metadata/history tests plus duplicate-terminal PostgreSQL race |
| `credit.appraisal.review` (`returned`) | `AppraisalWorkflow.review(decision="returned")` | same locked review predicate and authority; immutable decision append | returned/revise/resubmit/review cycle test |
| `credit.appraisal.review` (`rejected`) | `AppraisalWorkflow.review(decision="rejected")` | same locked review predicate plus explicit rejection fields; zero rejection-note/history/audit/workflow evidence on denial | rejection validation/rollback tests plus rejected-review/stale-patch PostgreSQL race |
| `credit.appraisal.submit_sanction` | `SanctionHandoffModule.submit_reviewed_appraisal` -> public `AppraisalWorkflow.prepare_sanction_handoff` | `evaluate_sanction_submission` after locked immutable history; Credit Manager role, exact permission/object scope, frozen facts and latest-decision consistency | sanction API matrix plus duplicate-submission PostgreSQL race; ADR-0005 dependency scan green |

All projections use the exact six fields: `action_code`, `label`, `enabled`, `disabled_reason`,
`required_permission`, and `required_role`. Denial tests assert no success state, audit, workflow,
review-history, rejection-note, or approval-case evidence according to the affected action.
