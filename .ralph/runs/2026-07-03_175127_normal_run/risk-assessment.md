# Risk Assessment

Risk level: High

- Selected slice: 002D-current-user-api-with-permissions-and-teams
- Mode: normal_run
- Standing approval: covered by `docs/working/HIGH_RISK_APPROVALS.md`; no veto entry exists for this slice.

## Why High
- Auth/RBAC endpoint: exposes current user, roles, teams, permissions, and action availability.
- Incorrect behavior could expose protected navigation/actions or allow a revoked/suspended session to continue.

## Controls
- Endpoint is additive: only `GET /api/v1/auth/me/` was added; no schema migration, dependency, or frontend behavior change.
- Token/session orchestration remains behind `sfpcl_credit.identity.modules.auth_service`, with a thin HTTP view.
- `/auth/me/` uses session-bound validation: signed/unexpired access token, `token_type == "access"`, active `UserSession`, matching user, and active user status.
- Effective permissions are read from existing `RolePermission` catalogue links; no object-level or business grants were invented.
- A-007 zero-link roles explicitly return `[]`.
- Standard response helper is used for success/error envelopes.

## Verification
- RED evidence: `.ralph/runs/2026-07-03_175127_normal_run/evidence/terminal-logs/red-auth-me-api-test.log`.
- Focused green tests: `.ralph/runs/2026-07-03_175127_normal_run/evidence/terminal-logs/green-auth-me-focused-tests-with-guardrail.log`.
- Backend gates: check, full tests (46/46), migrations check, coverage 96%.
- Frontend gates: vitest (5/5), typecheck, build.

## Residual Risk
- `available_actions` currently mirrors effective permission codes; later workflow/object-level slices must narrow actions per resource/stage.
- Frontend still uses demo auth until 002E wires the shell to the backend.
- Backend tests still duplicate manual schema setup; 002D2 is sharpened to remove that infrastructure debt.
