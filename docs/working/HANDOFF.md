# Ralph Handoff

## Last Run
2026-07-04_191553_normal_run

## Current Status
Slice `002K2-demo-tracer-permission-isolation` completed successfully. The guarded
`seed_demo_users` command now isolates the tracer smoke permission on local/dev-only role
`local_demo_tracer_user` instead of the shared source-catalogue `sales_team_user` role.
The command also removes stale `tracer.lifecycle.run` links from any non-demo role when
rerun, so databases that previously ran the old 002K seed are repaired by rerunning the
guarded seed.

## Current Slice
None selected.

## What Completed
`demo.tracer@sfpcl.example` authenticates through the real `/auth/login/` and `/auth/me/`
path and receives exactly `["tracer.lifecycle.run"]`. A non-demo active
`sales_team_user` remains permission-neutral (`permissions: []`,
`available_actions: []`) even if a stale Sales-role tracer grant existed before the seed
rerun. `demo.zero@sfpcl.example` remains neutral with no team.

Working docs were updated:
- `docs/working/API_CONTRACTS.md` now documents `local_demo_tracer_user` as the narrow
  local/demo exception.
- `docs/working/ASSUMPTIONS.md` A-011 now records that shared source roles stay neutral.
- `docs/working/digests/epic-002-platform-auth.md` records the 002K2 correction.
- `docs/slices/003A-audit-log-foundation.md` and
  `docs/slices/003B-workflow-event-foundation.md` were sharpened to avoid using the
  local demo tracer role as an audit/workflow permission fixture.

## Evidence
See `.ralph/runs/2026-07-04_191553_normal_run/`.

Gates passed:
- Backend `manage.py check`
- Backend `makemigrations --check --dry-run`
- Backend tests: 108/108
- Backend coverage: 96% (floor 85)
- Frontend `npm run typecheck`
- Frontend `npm run lint`
- Frontend `npm test`: 26/26
- Frontend `npm run build`

## Current Blocker
None.

## Next Recommended Action
Run `003A-audit-log-foundation` next. Then run `003B-workflow-event-foundation`.
