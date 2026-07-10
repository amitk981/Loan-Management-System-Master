# Slice 006D3: Credit Assessment Model Ownership State Migration

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Move credit-assessment Django model ownership from `applications` to the credit bounded context
without changing existing database tables, UUIDs, foreign keys, audit references, or workflow
references.

## Source / Review References
- `docs/source/codebase-design.md` §§6.2-6.3, §7.3, §§12.1-12.3, §26, and §42.2
- `docs/source/data-model.md` §14.1-§14.4 and §34
- `docs/adr/ADR-0002-staged-credit-assessment-model-ownership.md`
- `006D2A-credit-eligibility-module-and-configuration-seam` and
  `006D2B-credit-loan-limit-calculator-and-appraisal-seam` (the split successors of the
  superseded 006D2)

## Scope
- Preserve `LoanLimitCalculator`, `LoanLimitAssessmentResult`, `LoanLimitSnapshot`, and
  `EligibilityAssessmentModule` as the only behavior interfaces while moving Django state.
- Keep the 006D2B AST boundary green: no credit-helper aliases in `applications.services`, no
  private/aliased imports in views/appraisal, and no direct `LoanPolicyConfig` query outside the
  configuration resolver.
- Target model owner: `sfpcl_credit.credit.models` or an equivalent credit-owned model module.
- Existing tables must remain named `eligibility_assessments` and `loan_limit_assessments`.
- Preserve existing primary keys:
  - `eligibility_assessment_id`
  - `loan_limit_assessment_id`
- Preserve all existing one-to-one and foreign-key relationships to loan applications, members,
  shareholdings, and users.
- Use Django state-only migration operations such as `SeparateDatabaseAndState` when required.
- Do not rename, drop, recreate, copy, truncate, or backfill the existing tables.
- Keep `006D2` module interfaces as the public behavior seam; callers must not start importing
  model internals directly.

## Test Cases
- Migration/data-preservation test creates eligibility and loan-limit rows before the state move,
  applies the model-ownership migration, and reads the same UUIDs and FKs through the credit-owned
  model state.
- Reverse-migration proof shows rollback changes Django state ownership only and leaves the same
  database tables and UUIDs intact.
- Existing eligibility and loan-limit module/API tests remain green after ownership changes.
- Static import-boundary test continues to prove application views and future appraisal code use
  credit module interfaces rather than `applications.services` credit aliases.

## Acceptance Criteria
- `EligibilityAssessment` and `LoanLimitAssessment` are credit-owned in Django state.
- Physical tables remain `eligibility_assessments` and `loan_limit_assessments`.
- Existing row UUIDs, application one-to-one relationships, audit entity IDs, and workflow entity
  IDs are preserved.
- No destructive migration operation is introduced.

## Risk Level
High

## Done Checklist
- [ ] Execution plan written
- [ ] Red migration/data-preservation test captured
- [ ] State-only migration implemented
- [ ] Rollback proof captured
- [ ] Existing credit module/API tests passed
- [ ] Full backend and frontend gates passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
