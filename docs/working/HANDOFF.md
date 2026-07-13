# Ralph Handoff

## Last Run
2026-07-13_091510_normal_run

## Current Status

007B is complete. Source §25.2 now enriches the existing 006G shell without a second create path.
Credit owns the locked appraisal/review/provenance projection; approvals then snapshots the dated
approved rule and committee, ordered concrete approvers, amount, related entity, exception route,
and policy provenance atomically while preserving the submission workflow-event identity.

## Validation

Evidence is under `.ralph/runs/2026-07-13_091510_normal_run/`. RED/GREEN logs cover the absent
adapter, idempotent exception repeat, no-rule atomic loser, and decided-case rejection. Exact
₹500,000, above-threshold, and same-amount exception routes pass. Frontend build/typecheck/lint and
208 tests pass; backend check/migration sync and 553 tests pass with 16 expected PostgreSQL-only
skips and 93% coverage.

## Next Run

Run `007C-cfo-and-director-threshold-routing`: exclude unrouted version-1 shells and derive queue,
detail provenance, assignment, and actions only from the complete stored 007B snapshots.
