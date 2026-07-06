# Execution Plan

Selected slice: 002D-current-user-api-with-permissions-and-teams

## Scope
- Implement only `GET /api/v1/auth/me/`.
- No frontend wiring in this slice.
- Keep token/session/permission orchestration behind `sfpcl_credit.identity.modules.auth_service`.
- Use the shared API envelope helpers in `sfpcl_credit/api.py`.

## Source/Context Basis
- Slice file: `docs/slices/002D-current-user-api-with-permissions-and-teams.md`.
- Parent epic: `docs/epics/002-platform-auth-shell.md`.
- Digest: `docs/working/digests/epic-002-platform-auth.md`.
- Source spot-checks: auth JWT/session/current-user requirements, standard envelope, service-layer boundary, and identity/access tables.

## Edit Permission Check
- Allowed by `.ralph/permissions.json`: `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`, `.ralph/runs/**`, `.ralph/state.json`, `.ralph/progress.md`.
- Forbidden/protected paths will not be edited: `docs/source/**`, `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/working/HIGH_RISK_APPROVALS.md`, `docs/working/DECISION_POLICY.md`, `docs/working/FRONTEND_DESIGN_RULES.md`.

## TDD Plan
1. Add one failing API test proving an active logged-in user can call `/api/v1/auth/me/` and receives the standard envelope with profile, roles, teams, permissions, and available actions.
2. Implement the minimal service/view/url path to pass it.
3. Add focused failure tests for missing bearer token, expired access token, refresh-token misuse, inactive user, and revoked session.
4. Add module-level tests for session-bound access validation/current-user payload and deterministic permission resolution, including inactive-role and A-007 zero-link roles.
5. Keep the view thin: parse `Authorization: Bearer <token>`, call `auth_service.current_user_payload_for_access_token`, translate `TokenError`.

## Implementation Notes
- Resolve A-008 by making `/auth/me/` session-bound: access tokens must reference an active `UserSession`, and the bound user must still be active.
- Effective permissions come from `RolePermission` for the user's active `primary_role`, sorted and de-duplicated. Inactive roles and roles with no links return `[]`.
- `available_actions` will be a deterministic list derived from effective permission codes, not invented workflow decisions.
- Update `docs/working/API_CONTRACTS.md`, `docs/working/ASSUMPTIONS.md`, handoff/progress/state/slice status, and required run artifacts.

## Gates/Evidence
- Save red and green backend test logs under `.ralph/runs/2026-07-03_175127_normal_run/evidence/terminal-logs/`.
- Save API response examples for success, missing token, expired token, refresh misuse, and revoked session.
- Run backend check, full backend tests, migration check, backend coverage with `/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python`.
- Run frontend `npm test`, `npm run typecheck`, and `npm run build` from `sfpcl-lms/`.
