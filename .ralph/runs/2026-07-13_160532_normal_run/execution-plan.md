# Execution Plan

Selected slice: `007E-conflict-of-interest-blocking`

## Scope and public boundaries

1. Add the `approvals.modules.conflict_of_interest` deep-module seam and persisted declarations
   needed to evaluate borrower, Director-relative, material-interest, own-application, and
   maker-checker conflicts against the exact approval cycle's frozen application/appraisal facts.
2. Apply the assessment during sanction-case enrichment without changing the ordered immutable
   `required_approvers_json` snapshot. Store unique `{user_id, reason, conflict_code}` exclusions,
   expose the general-meeting-evidence requirement, and preserve the matrix role/count threshold
   by selecting only eligible users from the frozen committee projection.
3. Extend the existing case coherence, read-scope, queue, availability, and action boundaries so
   excluded users receive limited case read only, never enter `assigned_to_me`, and cannot record
   approve/reject/return decisions.
4. Return the exact `CONFLICTED_APPROVER_NOT_ALLOWED` API error for every excluded/conflicted write
   and append only the source-required COI-006 denial audit evidence, including case and cycle.
5. Add conflict abstention through the existing immutable action ledger. A satisfiable abstention
   excludes the actor and leaves the case pending for frozen alternate authority; an unsatisfiable
   abstention records the action/exclusion and moves the case to an explicit conflict-blocked state.
6. Update the API contract/digest and migration, then sharpen the next two Not Started Epic 007
   slices using only already-open source requirements.

## TDD tracer bullets

- RED -> GREEN: enrichment detects maker-checker and declared conflict classes, records reasons,
  preserves the required snapshot, and flags Director/relative cases.
- RED -> GREEN: detail/queue/action parity excludes conflicted actors, returns the exact source
  error body, and records a narrowly scoped denial audit without any action or state mutation.
- RED -> GREEN: eligible frozen alternates can satisfy the original role/count rule; abstention is
  immutable and either keeps the rule satisfiable or blocks the case without sanction creation.
- RED -> GREEN: cycle N conflict evidence remains immutable and is recomputed independently for
  cycle N+1.

Each backend cycle will use `/Users/amitkallapa/LMS/.ralph/venv/bin/python`; red and green outputs
will be saved under `evidence/terminal-logs/`.

## Gates and evidence

- Focused approval tests after every tracer bullet, then backend check, migration sync, full
  coverage suite, frontend build/typecheck/lint/vitest, and slice-queue/protected-path review.
- Save error-contract examples, changed-files, risk assessment, review packet, final summary,
  progress/state/handoff updates, and exact source-to-test traceability.
