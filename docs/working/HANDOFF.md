# Ralph Handoff

## Last Run
2026-07-11_090234_normal_run

## Current Status

006G3 is complete. Credit no longer imports approvals. The approvals-owned sanction handoff now
owns the atomic case, status, audit, and workflow-event writes and stores the exact event UUID on
the unique pending case. Submit and reload return that durable identity without a latest-event
query. Shared errors moved below both apps, and the five PostgreSQL races passed twice with exact
canonical evidence assertions.

## Validation

TDD, API/migration, two PostgreSQL five-race runs, and configured gate logs are under
`.ralph/runs/2026-07-11_090234_normal_run/`. The full backend suite passed 394 tests with five
expected skips at 94% coverage; frontend build/typecheck/lint and 130 tests passed.

## Next Run

Run `006H4-workbench-authoritative-actions-and-container-tests`, then 006H3 and 006X in dependency
order. Sanction dependency/evidence ownership is accepted; the current Workbench action UI remains
unaccepted until its corrective slices pass.
