# Ralph Handoff

## Last Run
2026-07-13_122527_normal_run

## Current Status

007C2 is complete. Approval-case read permission no longer implies global object scope: ordinary
collections are scope-filtered before counts/pagination, assigned actors retain their own acted
history, and unassigned Directors, makers, and arbitrary permission holders receive empty lists
plus canonical object denial on detail without business writes.

The approval-owned deep module now exposes one coherent routability predicate, one object-access
predicate, and one pending-actor predicate. It reconciles the complete immutable matrix,
committee, approver, case, application, decision, exception, and loan-limit provenance snapshot;
injected, duplicate, mismatched, or incomplete rows are hidden and non-actionable. Enrichment,
list, and detail compose one canonical routing projection with source-required `current_status`.
Exact enrichment replay compares every locked reviewed/assessment/policy provenance field.

## Validation

Evidence is under `.ralph/runs/2026-07-13_122527_normal_run/evidence/terminal-logs/`. RED captures
unassigned global reads, injected authority routing, incomplete replay comparison, and the missing
§25.2 status/parity field. Focused approval suites pass (49 contract-closure rows; 74 broader
approval rows). Backend check/migration sync and 585 tests pass with 16 expected PostgreSQL-only
skips and 93% coverage. Frontend build/typecheck/lint and 208 tests pass. No frontend or schema
change was introduced.

## Next Run

Run `007D-approval-action-api-approve-reject-return`, then
`007E-conflict-of-interest-blocking`. Both received 007C2 run-ahead sharpening. 007D must re-run
the public coherent-route/object-scope/pending-actor predicates after locking and return the
canonical serializer; 007E must preserve required authority history and layer exclusions without
reconstructing live authority.
