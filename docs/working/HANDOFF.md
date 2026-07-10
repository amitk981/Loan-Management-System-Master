# Ralph Handoff

## Last Run
2026-07-10_195330_normal_run

## Current Status
`006F3-appraisal-lock-order-and-postgresql-concurrency-closure` failed its mandatory PostgreSQL
acceptance gate and remains `Not Started`; it must not be committed, merged, or treated as complete.

- The ungated worktree contains a candidate private `AppraisalWorkflow` lock implementation using
  application -> appraisal -> existing review history -> optional rejection-note work. Submit,
  prerequisite revalidation, review, create, and update use the same application-first order.
- Two PostgreSQL-only public-interface transaction tests cover rejected review versus stale draft
  PATCH and competing terminal decisions. They assert deterministic serialization, one native
  winning history row, one optional rejection note, matching audit/workflow UUIDs, unchanged
  pre-race history, and no loser success evidence.
- PostgreSQL row locks that join nullable related users use `FOR UPDATE OF self`; the same necessary
  correction was applied to the application lock exercised by the unchanged 006D2C loan-limit
  concurrency tests.

## Validation
Standard gates passed: 365 default backend tests with four PostgreSQL-only skips, 94% coverage,
Django check, migration sync, frontend lint/typecheck, 107 tests, build, and diff checks. The
mandatory combined PostgreSQL command found four tests but executed none because the AFK sandbox
denied the live PostgreSQL 14 Unix socket with `Operation not permitted`. An isolated server could
not bootstrap because the same sandbox forbids PostgreSQL's required SysV shared-memory segment.
Evidence is in `.ralph/runs/2026-07-10_195330_normal_run/`.

## Next Run
Run Ralph repair for `006F3` in an agent environment permitted to connect to PostgreSQL. Start by
reading the failed run packet, then execute the exact combined four-test command with zero skips;
diagnose any real PostgreSQL failures before reusing the candidate worktree changes. Only after a
green authoritative run and all standard gates may 006F3 complete. `006G` and `006H` were sharpened
but remain downstream and must not start first.
