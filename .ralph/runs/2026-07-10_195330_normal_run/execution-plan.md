# Execution Plan

Selected slice: `006F3-appraisal-lock-order-and-postgresql-concurrency-closure`

## Scope and constraints

- Preserve the public `AppraisalWorkflow` interface, review/rejection payloads, permissions,
  appraisal states, frozen snapshots, and the public rejection-note module seam.
- Normalize every appraisal mutation to the lock order `LoanApplication` ->
  `LoanAppraisalNote` -> rejection-note/review-history rows.
- Add PostgreSQL-only transactional outcome tests through `AppraisalWorkflow`; do not use mocked
  lock assertions as acceptance evidence.
- Execute the new appraisal concurrency tests together with the unchanged
  `LoanLimitConcurrencyTests` on PostgreSQL with zero skips. The slice remains incomplete if a real
  PostgreSQL run is unavailable or fails.

## TDD tracer bullets

1. Add one concurrent rejected-review versus stale draft-PATCH test. Coordinate two independent
   database connections so rejection owns the application lock first; assert deterministic order,
   no deadlock/server exception, terminal rejection, unchanged draft fields, exactly one rejection
   note/history row, matching audit/workflow history UUID, and no loser success evidence. Save the
   failing PostgreSQL output before changing production code, then make the smallest lock-order
   implementation change and save green output.
2. Add one concurrent duplicate terminal review/rejection test through `AppraisalWorkflow.review`.
   Assert exactly one terminal outcome, one native immutable history row, at most one rejection
   note, a complete matching audit/workflow set, and no success evidence from the losing request.
   Save RED then GREEN PostgreSQL output.
3. Run the combined PostgreSQL acceptance command for `LoanLimitConcurrencyTests` and the new
   appraisal concurrency class, recording server version, non-secret connection settings,
   deterministic ordering, test count, and zero skips.

## Implementation shape

- Keep lock acquisition inside the deep `AppraisalWorkflow` module. Resolve an appraisal's
  application identifier without acquiring a row lock, acquire the application row lock, then
  acquire the appraisal row lock with existing related projections.
- Reuse that internal implementation for submit, prerequisite revalidation, and review; retain
  create/update's existing application-first order. Rejection-note creation and append-only review
  history remain after both owning rows are locked.
- Do not add a public method or expose concrete models to callers.

## Verification and handoff

- Run the appraisal regression suite and all standard backend/frontend gates with the mandated
  backend interpreter.
- Save terminal logs, PostgreSQL evidence, changed-files list, risk assessment, review packet, and
  final summary in this run folder.
- Update the Epic 006 digest with the lock-order/concurrency result, then update assumptions only if
  a new source-silent decision is necessary.
- Sharpen the next one or two `Not Started` slices using only already-opened Epic 006/source
  material, then update progress, handoff, state, and this slice status after every acceptance gate
  is green.
