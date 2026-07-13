# Ralph Handoff

## Last Run
2026-07-13_135007_normal_run

## Current Status

007C3 is complete. Credit Manager, Company Secretary, and Internal Auditor now receive the source-
required `approvals.case.read`, while object scope remains separately attributable to the immutable
approver snapshot, Credit Manager application/case ownership, or an active persisted role grant.
Only Company Secretary legal read-only and Internal Auditor audit read-only grants seed by default.

The approval-owned selector uses an exact required-approver UUID index plus a save-maintained
coherence projection to perform scoped SQL count and pagination. Appraisal changes refresh that
projection, and detail/actions still run the complete live snapshot predicate. Read-only grants
never enable actions, enter assigned queues, or write approval evidence; arbitrary readers and
unassigned Directors retain 007C2 empty-list/403 nondisclosure.

## Validation

Evidence is under `.ralph/runs/2026-07-13_135007_normal_run/`. Retained RED/GREEN logs cover
Credit Manager scope, source permission/grant seeding, role/grant revocation, read-only action
ledgers, exact selector behavior, query bounds, and historical migration backfill. Independent
Standards and Spec reviews have no remaining findings. Frontend build/typecheck/lint and 208 tests
pass. Backend check/migration sync and 602 tests pass with 16 expected PostgreSQL-only skips and
93% coverage.

## Next Run

Run `007D2-approval-action-boundary-and-postgresql-race-closure`, then
`007D3-returned-approval-cycle-and-resubmission-closure`. 007E now depends on 007D3 so conflict
exclusions and abstentions use the history-aware, communication-backed, multi-cycle boundary.
