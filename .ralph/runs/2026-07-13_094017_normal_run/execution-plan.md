# Execution Plan

Selected slice: `007C-cfo-and-director-threshold-routing`

1. Add a public approval-case read module and source-defined immutable approval-action read model.
   Treat a case as routed only when every 007B snapshot/provenance field is complete; never call or
   import the live matrix or committee resolvers. Keep action creation and case transitions out of
   scope for 007D.
2. Drive the implementation through public HTTP tests, one behavior at a time: assigned pending
   queue and pagination; strict filter validation; acted/excluded/unrouted exclusion; snapshot-only
   routing across live configuration changes; detail permissions; §44 action projections; and
   checklist read-through facts.
3. Expose `GET /api/v1/approval-cases/` and `GET /api/v1/approval-cases/{id}/` using the shared
   success/list/error envelopes. Require `approvals.case.read`; allow global readers to inspect a
   routed case but enable approve/reject/return only for a still-pending snapshotted approver who
   also holds the matching action permission.
4. Document list/detail shapes and identify the checklist fields dynamically projected from the
   application/appraisal owners. Save representative API response examples and red/green terminal
   evidence.
5. Run scoped tests throughout, then Django check, migration sync, full backend coverage, frontend
   build/typecheck/lint/tests, and queue/protected-path checks available to the agent. Review the
   final diff against this slice and its source references.
6. Complete Ralph artifacts: risk assessment, changed-files list, review packet, final summary,
   progress/state/handoff, selected-slice status, and concrete run-ahead sharpening for the next
   one or two Not Started slices using only already-open source material.
