# Execution Plan

Selected slice: 006G-submit-to-sanction

1. Extract only the source sections named by 006G and inspect the existing appraisal, permission,
   audit/workflow, API-envelope, and migration seams established through 006F3.
2. Write failing backend tests first for the service and endpoint contracts: reviewed-only state,
   complete immutable review provenance, independent permission/object scope, strict remarks,
   one pending case, exception flagging, rejected/repeated/no-side-effect paths, rollback, and
   metadata-only evidence. Save the red output under `evidence/terminal-logs/`.
3. Add the smallest approval-case model/migration and implement
   `AppraisalWorkflow.submit_to_sanction(...)` with the established application -> appraisal ->
   history -> approval-case lock order, then expose the strict POST endpoint and permission seed.
4. Run focused tests to green and save output; add PostgreSQL concurrency coverage when the
   repository's established harness can execute it, without treating SQLite skips as concurrency
   proof.
5. Update API contracts and durable project documentation, then run all configured backend and
   frontend gates plus migration/diff checks. Preserve evidence in the run folder.
6. Review the final diff for source fidelity, protected paths, risk, and slice boundaries; write
   changed-files, risk assessment, review packet, final summary, state/progress/handoff updates,
   complete the slice checklist, and sharpen the next one or two Not Started slices using only
   source material opened during this run.

Permissions checked against `.ralph/permissions.json`: edits are limited to `sfpcl_credit/**`,
`docs/working/**`, `docs/slices/**`, `.ralph/state.json`, `.ralph/progress.md`, and this run folder.
No protected or forbidden path will be modified.
