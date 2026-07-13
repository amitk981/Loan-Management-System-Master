# Ralph Handoff

## Last Run
2026-07-13_061140_normal_run

## Current Status

006Z13 is complete. Persisted member scope now has database-enforced shape and conditional
uniqueness across global, created-by, assigned, and team grants, with a non-destructive exact-
duplicate cleanup migration. Real evaluator coverage includes inactive team membership and scoped
list totals. Staff calculation has an explicit actor/scope boundary, while dependency proof limits
actorless domain calculation to application-scoped eligibility and authenticated portal-owned
member paths. Existing public member action and maker-provenance suites remain green.

## Validation

Evidence is under `.ralph/runs/2026-07-13_061140_normal_run/`. The database and staff-calculation
tracer bullets retain RED/GREEN logs; the focused public matrix passes 85 tests. Frontend build,
typecheck, lint, and 207 tests pass. Backend check/migration sync and 531 tests pass with 16 expected
PostgreSQL-only skips and 93% coverage.

## Next Run

Run `007A4-approval-governance-concurrency-and-case-snapshot-closure`, then
`007B-approval-case-creation-from-appraisal`. Both remain concrete and source-linked; 007B already
requires the governed, concurrency-proven configuration versions produced by 007A4.
