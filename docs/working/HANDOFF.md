# Ralph Handoff

## Last Run
2026-07-13_081756_normal_run

## Current Status

007A4 is complete. Approval configuration now has current proposal-decision concurrency proof for
rule and committee create/supersede, canonical authority errors, a participant/checker/reader
proposal-detail boundary, and immutable open-case configuration snapshot fields.

## Validation

Evidence is under `.ralph/runs/2026-07-13_081756_normal_run/`. Proposal-detail and canonical-code
RED/GREEN logs, case snapshot RED/GREEN, sequential matrices, migration `0005`/`0006` proof, and two
governed PostgreSQL runs are retained. Frontend build/typecheck/lint and 208 tests pass. Backend
check/migration sync and 535 tests pass with 16 expected PostgreSQL-only skips and 93% coverage.

## Next Run

Run `007B-approval-case-creation-from-appraisal`, then `007C-cfo-and-director-threshold-routing`.
Both are sharpened to reuse the 007A4 snapshot columns and treat stored case projections, not live
configuration, as routing authority.
