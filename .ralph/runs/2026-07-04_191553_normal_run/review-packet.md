# Review Packet

Run ID: 2026-07-04_191553_normal_run

Slice: 002K2-demo-tracer-permission-isolation

## Change Summary

`seed_demo_users` no longer grants `tracer.lifecycle.run` to the shared
`sales_team_user` role. The command now creates/updates local/dev-only role
`local_demo_tracer_user`, grants that role exactly `tracer.lifecycle.run`, assigns
`demo.tracer@sfpcl.example` to it, and removes stale tracer-permission role links from
any other role.

Backend tests now cover a non-demo active Sales user with a stale old Sales-role tracer
grant before the corrected seed runs. After rerun and real login/current-user calls, that
user receives `permissions: []` and `available_actions: []`.

## Traceability

The slice says `demo.tracer@sfpcl.example` should authenticate with exactly
`tracer.lifecycle.run` while any non-demo `sales_team_user` remains permission-neutral.
The code does this in `sfpcl_credit/identity/management/commands/seed_demo_users.py` by
isolating the grant on `local_demo_tracer_user` and deleting stale links from other roles.
Verified by:

- RED: `red-seed-demo-sales-neutral-stale-grant.log`
- GREEN: `green-seed-demo-sales-neutral-stale-grant.log`
- Focused regression suite: `green-seed-demo-users-focused.log`

The source/digest assumption says `sales_team_user` has no source-defined permission
links and the tracer permission is a dev/test smoke exception. Working docs now state
that the exception is the local/dev-only role, not the shared source role:

- `docs/working/API_CONTRACTS.md`
- `docs/working/ASSUMPTIONS.md` A-011
- `docs/working/digests/epic-002-platform-auth.md`

## Tests And Gates

- Backend check: passed (`backend-check.log`)
- Migration sync: passed (`backend-makemigrations-check.log`)
- Backend tests: 108/108 passed (`backend-tests.log`)
- Backend coverage: 96%, floor 85 (`backend-coverage.log`)
- Frontend typecheck: passed (`frontend-typecheck.log`)
- Frontend lint: passed (`frontend-lint.log`)
- Frontend unit tests: 26/26 passed (`frontend-tests.log`)
- Frontend build: passed (`frontend-build.log`)
- `git diff --check`: passed (`git-diff-check.log`)

## API / Schema Impact

No public API response shape changed. No schema migration was needed.

## Protected Paths

No protected files were modified. `docs/source/**`, scripts, `.ralph/config.yaml`, and
`.ralph/permissions.json` were not changed.

## Next Slices

`003A-audit-log-foundation` and `003B-workflow-event-foundation` were sharpened to avoid
using the local demo tracer role as a production permission fixture.
