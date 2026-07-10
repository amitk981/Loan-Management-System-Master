# ADR-0002: Stage Credit Assessment Model Ownership

## Status
Accepted

## Context
Slice `006D2-credit-assessment-deep-module-boundary` establishes the source-named deep credit
module seams:

- `sfpcl_credit.credit.modules.eligibility_assessment`
- `sfpcl_credit.credit.modules.loan_limit_calculator`
- `sfpcl_credit.credit.modules.appraisal_workflow`

The source data model says credit-assessment state belongs to the credit bounded context, but the
existing Django models were created under `sfpcl_credit.applications.models`:

- `EligibilityAssessment`, backed by existing table `eligibility_assessments`
- `LoanLimitAssessment`, backed by existing table `loan_limit_assessments`

Moving Django model state inside the same behavior-refactor slice would consume the slice's single
migration allowance and risks turning a source-code ownership correction into accidental table
rename/drop/recreate behavior.

## Decision
For `006D2`, move behavior, transaction orchestration, configuration resolution, snapshot
projection, audit, workflow coordination, and public interfaces into the credit modules, but keep
the Django model classes in `applications.models` for now.

Create a separately queued slice for model ownership migration using a state-only,
data-preserving strategy.

## Required Follow-Up Strategy
The model-ownership slice must:

- Target owner: move `EligibilityAssessment` and `LoanLimitAssessment` model state to
  `sfpcl_credit.credit.models` or an equivalent credit-owned model module.
- Preserve database tables exactly as `eligibility_assessments` and `loan_limit_assessments`.
- Preserve every existing `eligibility_assessment_id`, `loan_limit_assessment_id`, FK, one-to-one
  application relationship, audit `entity_id`, and workflow `entity_id`.
- Use Django state-only operations such as `SeparateDatabaseAndState` where needed; it must not
  rename, drop, recreate, or copy the existing tables.
- Include a migration/data-preservation test that creates rows through the pre-move state, applies
  the ownership migration, and proves the same UUIDs/FKs remain readable through the credit-owned
  model state.
- Include rollback proof that reversing the migration returns Django model state ownership without
  destructive database operations.

## Consequences
`006E` and later appraisal work must import credit module interfaces, not `applications.services`,
even while the concrete Django model classes remain temporarily in `applications.models`.
