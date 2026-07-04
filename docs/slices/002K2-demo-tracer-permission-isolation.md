# Slice 002K2: Demo Tracer Permission Isolation

## Status
Not Started

## Parent Epic
Epic 002: Platform Auth and Role Shell
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Fix the 002K demo seed so the local/demo tracer capability stays isolated to the intended
demo tracer account and does not grant `tracer.lifecycle.run` to every user with the
shared `sales_team_user` role.

## User Value
Local demos and future smoke tests can rely on one tracer-capable demo staff user without
masking permission bugs for other Sales users or weakening the neutral-role assumptions
used by the frontend shell.

## Depends On
- 002K

## Review Finding
Created by architecture review `2026-07-04_190302_architecture_review`.

## Source / Digest References
- `docs/working/ASSUMPTIONS.md` A-007: `sales_team_user` has no source-defined seeded
  permission links until the source catalogue defines grants.
- `docs/working/ASSUMPTIONS.md` A-011: `tracer.lifecycle.run` is a dev/test smoke
  permission and later production slices must replace or remove the tracer route.
- `docs/slices/002K-seed-data-and-demo-users.md` requires demo users to avoid broad
  aliases, keep E2E/demo users separate, and keep zero/neutral permission behavior
  explicit.

## Current Drift
`seed_demo_users` currently grants `tracer.lifecycle.run` by adding a `RolePermission` to
the shared `sales_team_user` role. Because `/auth/me/` derives permissions from
`primary_role`, every local user with `sales_team_user` becomes tracer-capable after the
demo seed runs, not only `demo.tracer@sfpcl.example`.

## Backend/API Scope
1. Keep `seed_demo_users` guarded by both `SFPCL_DEBUG=true` and
   `SFPCL_ALLOW_DEMO_SEED=true`.
2. Isolate tracer demo authority so `demo.tracer@sfpcl.example` can authenticate with
   exactly `tracer.lifecycle.run` while a pre-existing or newly created non-demo
   `sales_team_user` remains permission-neutral after the seed command.
3. Do not grant broad prototype aliases such as `manage_users`.
4. Do not weaken the 002E/002F neutral-role frontend mapping or the 002G2 action-specific
   admin permission gate.
5. If the fix needs a guarded demo-only role, name and document it as local/dev-only,
   keep it out of the source RBAC catalogue seed, and record/adjust the relevant
   assumption. Do not add production role grants that the source documents do not state.

## Database/Model Impact
No schema change expected. Use existing `Role`, `Permission`, `RolePermission`, `User`,
and `UserTeamMembership` tables.

## API Contracts
Update `docs/working/API_CONTRACTS.md` only if the documented local-demo seed behavior or
demo role description changes. Auth response shapes must not change.

## Permissions
- `demo.tracer@sfpcl.example`: exactly `tracer.lifecycle.run`.
- Existing non-demo `sales_team_user`: no permissions unless a source-backed future slice
  defines Sales permissions.
- `demo.zero@sfpcl.example`: still no permissions and no team.

## Test Cases
- Backend TDD: create a non-demo active `sales_team_user`, run the guarded seed, login as
  that user, and assert `/api/v1/auth/me/` returns `permissions: []` and
  `available_actions: []`.
- Backend regression: `demo.tracer@sfpcl.example` still returns exactly
  `["tracer.lifecycle.run"]`.
- Backend regression: `demo.zero@sfpcl.example` remains neutral.
- Backend regression: rerunning the seed remains idempotent and does not duplicate roles,
  permissions, memberships, or demo users.
- Backend regression: the command still refuses without the explicit local/demo guard.

## Risk Level
Medium

## Acceptance Criteria
- Demo tracer authority is isolated to the intended demo user/role path.
- Shared source catalogue roles are not accidentally granted tracer authority by the demo
  seed.
- Red/green TDD evidence and full backend/frontend gates are saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written first (RED saved, then GREEN)
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Permissions tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
