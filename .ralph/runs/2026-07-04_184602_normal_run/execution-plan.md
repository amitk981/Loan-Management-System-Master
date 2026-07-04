# Execution Plan

Selected slice: 002K-seed-data-and-demo-users

## Scope
- Add a guarded local/dev management command for deterministic demo staff users.
- Reuse existing catalogue rows for roles, teams, and permissions; do not add schema or ad hoc catalogue data.
- Keep demo users separate from E2E users with distinct emails and `SFPCL_ALLOW_DEMO_SEED=true`.
- Prove real login, `/api/v1/auth/me/`, admin permission denial, idempotency, and auth audit behavior through backend tests.

## Permission Check
Allowed edit paths from `.ralph/permissions.json`:
- `sfpcl_credit/**`
- `.ralph/runs/**`
- `docs/working/**`
- `docs/slices/**`
- `.ralph/state.json`

Protected or forbidden paths will not be modified:
- `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`
- `docs/working/HIGH_RISK_APPROVALS.md`, `docs/working/DECISION_POLICY.md`, `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/source/**`, `.git/**`, secret files

## TDD Plan
1. RED: add `test_seed_demo_users.py` proving `seed_demo_users` refuses without `SFPCL_DEBUG=true` and `SFPCL_ALLOW_DEMO_SEED=true`.
2. GREEN: implement the management command guard and minimal command shell.
3. RED/GREEN: extend tests for guarded seed contents, idempotent reruns, active memberships, exact tracer/zero permissions, real auth login + `/auth/me`, auth audit rows, and standard 403 envelope for a read-only demo user attempting an update-gated admin action.
4. Run targeted backend tests after each cycle and save red/green logs.

## Validation
- Backend: `manage.py check`, targeted tests, full test suite, `makemigrations --check`, coverage with the Ralph interpreter.
- Frontend: run configured typecheck, lint, tests, and build even though no frontend code is expected to change.
- Save API examples for system-admin, tracer-only, and zero-permission demo login + `/auth/me`.

## Finish
- Update risk assessment, review packet, final summary, changed files, state/progress/handoff, and slice status.
- Sharpen the next one or two `Not Started` slices using only already opened source/digest context.
