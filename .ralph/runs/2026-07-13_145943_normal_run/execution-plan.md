# Execution Plan

Selected slice: `007D3-returned-approval-cycle-and-resubmission-closure`

## Outcome

Make return-for-clarification a closed, immutable approval cycle and allow a corrected appraisal,
fresh Credit Manager review, and sanction resubmission to create a distinct numbered cycle without
rewriting prior case, action, audit, workflow, or communication evidence.

## Plan

1. Inspect the existing appraisal history, sanction handoff, approval case/action models, public
   projections, migrations, and tests to identify the narrow existing module seams.
2. RED -> GREEN: add one public workflow test for return, correction, fresh review, and resubmit;
   introduce positive cycle numbering and application/cycle uniqueness with deterministic cycle-1
   migration, then create cycle N+1 only through the sanction-handoff boundary.
3. RED -> GREEN incrementally for resubmission denials, old-cycle immutability, fresh-review
   provenance, API cycle projection, and final sanction creation from the latest cycle only.
4. Add concurrency-focused coverage at the strongest locally available boundary, preserving the
   application -> appraisal -> case lock order and proving one new cycle/evidence set.
5. Update the working API contract and Epic 007 digest with the delivered numbered-cycle contract;
   create migration and reviewable RED/GREEN/migration/API evidence in the run folder.
6. Run targeted tests throughout, then backend check, migration sync, full backend coverage suite,
   and all frontend build/typecheck/lint/test gates.
7. Perform the required two-axis standards/spec review, resolve material findings, sharpen the next
   one or two Not Started slices using already-opened Epic 007 material, and finalize Ralph state,
   progress, handoff, slice status, changed-files, risk assessment, review packet, and summary.

## TDD Behaviours

- A returned cycle can re-enter sanction only after maker correction and a newer independent
  `reviewed` decision matching the corrected appraisal.
- Pending, approved, rejected, uncorrected, and not-freshly-reviewed attempts are stable denials
  with exact zero-write ledgers.
- Successful resubmission creates exactly cycle N+1; cycle N and its evidence remain unchanged.
- The same snapshotted approvers may act in a later cycle, but earlier actions never satisfy it.
- List/detail/action responses expose `cycle_number`; returned history is readable but never
  assigned or actionable.
- Final approval links the application-unique sanction decision only to the latest cycle.
