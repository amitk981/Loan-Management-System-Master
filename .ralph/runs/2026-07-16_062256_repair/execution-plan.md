# Execution Plan

Selected slice: `009B-sap-customer-code-confirmation-and-reuse`

## Repair diagnosis

- The newest available failed-run summary is
  `.ralph/runs/2026-07-16_044126_repair/failure-summary.md`; it concerns completed slice `008M2`
  and only reports the changed-line limit. Later runs repaired and completed that slice.
- There is no failed 009B implementation, no registered repair context, no tracked product diff, and
  no leftover worktree other than this active worktree. This run therefore implements the selected
  concrete 009B slice fresh while preserving the repair-mode evidence trail.

## Plan

1. Inspect the 009A finance model/service/API tests and the existing document, communication, task,
   permission, audit, workflow, and PostgreSQL race seams. Confirm whether the existing 009A
   migration already contains every source-required 009B field and constraint.
2. Add a focused public-API regression test for the exact missing send/complete/read behavior. Run
   it with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`, save deterministic RED output under
   `evidence/terminal-logs/`, and keep that command as the tight feedback loop.
3. Add the remaining tests for send ownership/replay/change/zero-write behavior; completion with a
   new or reused member code; duplicate/conflicting codes; restricted evidence; masked scoped read;
   unknown/invalid fields; stale cycle/state/assignee/object denial; secret-free ledgers; prohibited
   downstream side effects; and twice-run PostgreSQL race families.
4. Implement the smallest finance deep-module boundary needed to pass those tests: narrow seeded
   permissions, exact retained-Annexure send, adapter communication/task provenance, immutable
   completion/reuse ledgers, one normalized active member code, scoped masked read, and the required
   API routes/envelopes. Add at most one migration only if the 009A shell cannot express source truth.
5. Run focused GREEN tests, Django check, migration drift, the full backend coverage gate, and the
   unchanged frontend build/typecheck/lint/test gates. Run the declared PostgreSQL race contract
   twice and preserve all outputs and sanitized API/ledger examples in this run folder.
6. Review the diff for protected paths, secrets, scope creep, downstream loan/disbursement writes,
   migration/constraint integrity, and configured diff limits. Update API contracts if changed.
7. Sharpen the next one or two Not Started slices only from the Epic 009 source material already
   opened; then finalize changed-files, risk assessment, review packet, summary, assumptions (if
   any), progress, handoff, state, and the 009B slice status without invoking git add/commit/push.
