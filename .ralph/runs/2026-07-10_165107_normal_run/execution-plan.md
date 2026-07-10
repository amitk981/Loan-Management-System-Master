# Execution Plan

Selected slice: 006D3-credit-assessment-model-ownership-state-migration

## Scope and constraints

- Move only `EligibilityAssessment` and `LoanLimitAssessment` Django state ownership from
  `applications` to `credit`; preserve the established credit module interfaces.
- Preserve the physical tables, UUID primary keys, one-to-one application links, member,
  shareholding, user, audit, and workflow references. No database operations, data copy, rename,
  backfill, drop, or recreate are permitted.
- Stay within the one-migration limit and keep the 006D2B static import seam green.
- No frontend or API contract change is expected.

## TDD tracer bullets

1. Add one migration-executor test that creates both assessment rows in the pre-move historical
   state, migrates forward, and asserts credit owns the models while the same rows, UUIDs, and
   foreign keys remain readable. Run it alone and capture RED.
2. Implement the minimal state-only ownership migration and credit-owned model definitions, then
   update the credit module implementations and tests to import the new owner. Run the migration
   test and capture GREEN.
3. Extend the same migration proof with reverse migration: applications regains state ownership,
   credit loses it, and the exact rows/UUIDs/FKs remain in the unchanged tables. Capture the
   focused rollback proof.
4. Run the existing credit module and loan-application API suites to prove behavior remains behind
   `EligibilityAssessmentModule`, `LoanLimitCalculator`, `LoanLimitAssessmentResult`,
   `LoanLimitSnapshot`, and `AppraisalWorkflow`; run the static boundary regression.

## Verification and closeout

- Run backend check, migration sync, full coverage suite at the configured floor, and all frontend
  lint/typecheck/test/build gates with the mandated interpreters/tooling.
- Save all red/green and gate outputs under the run evidence folder; save changed-files,
  risk-assessment, review-packet, and final-summary artifacts.
- Update the Epic 006 digest, slice status, Ralph state/progress/handoff, and sharpen the next one or
  two Not Started slices only from already-opened source material.
