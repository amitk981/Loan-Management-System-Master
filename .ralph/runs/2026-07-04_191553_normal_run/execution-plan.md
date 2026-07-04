# Execution Plan

Selected slice: 002K2-demo-tracer-permission-isolation

## Permissions Check

- Allowed edit paths for this slice: `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`, `.ralph/state.json`, `.ralph/progress.md`, `.ralph/runs/**`.
- Protected/forbidden paths will not be edited: `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/source/**`, `docs/working/HIGH_RISK_APPROVALS.md`, `docs/working/DECISION_POLICY.md`, `docs/working/FRONTEND_DESIGN_RULES.md`.
- No frontend production changes are planned.

## Scope

Fix the guarded `seed_demo_users` command so `tracer.lifecycle.run` is isolated to `demo.tracer@sfpcl.example` through a local/dev-only role path, instead of being granted to the shared source-catalogue `sales_team_user` role.

## TDD Plan

1. RED: add a backend regression that creates a non-demo active `sales_team_user`, runs the guarded seed, logs in through `/api/v1/auth/login/`, and asserts `/api/v1/auth/me/` returns `permissions: []` and `available_actions: []`.
2. GREEN: update `seed_demo_users` to create/use a guarded local/demo-only tracer role with exactly `tracer.lifecycle.run`; leave `sales_team_user` permission-neutral.
3. Extend/update existing demo seed assertions for tracer-only, zero-permission, and idempotency so they reflect the isolated local/demo role and no duplicate role/permission/user/membership rows.
4. Update working API contract/assumption text if needed to document that the seed's narrow exception uses a local/dev-only role, not the shared source role.

## Verification

- Save RED and GREEN focused test logs under `.ralph/runs/2026-07-04_191553_normal_run/evidence/terminal-logs/`.
- Run backend gates with `/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python`.
- Run frontend gates because Ralph validation requires them, even though no frontend code changes are planned.
- Save changed files, risk assessment, review packet, final summary, and update handoff/state/progress/slice status.
