# Ralph Handoff

## Last Run
2026-07-13_090059_normal_run

## Current Status

007A5 is complete. All four governed rule/committee create/supersede races now prove the complete
winner-only configuration ledger and publicly read back the unchanged pending loser. Every race
carries a discriminating open case whose stored rule, committee, approvers, decision date, workflow
event, and version remain identical. Historical/current committee resolution, conflicting backfill,
duplicate membership, and swapped authority are independently attributable.

## Validation

Evidence is under `.ralph/runs/2026-07-13_090059_normal_run/`. RED proves the public loser omitted
its immutable payload. GREEN proves the complete ledger, and the exact four PostgreSQL race methods
pass twice after approvals migrations 0005/0006. Frontend build/typecheck/lint and 208 tests pass;
backend check/migration sync and 548 tests pass with 16 expected PostgreSQL-only skips and 93%
coverage.

## Next Run

Run `007B-approval-case-creation-from-appraisal`: enrich the existing unrouted case shell through
the real approval-case seam using approved resolver projections only. Then 007C excludes empty
shells and derives queues/actions only from the stored historical snapshot.
