# Execution Plan

Selected slice: 002D3-current-user-contract-fidelity

## Source Basis
- `docs/source/api-contracts.md` §5.3, §6.1, §6.4, §11.4: protected APIs use `Authorization: Bearer <access_token>`, standard success/error envelopes, and `/auth/me/` returns current user profile, roles, teams, and permissions.
- `docs/source/auth-permissions.md` §5.3, §8.2, §34.1, §38.1: JWTs stay minimal, sessions are tracked/revocable, `/auth/me/` is authenticated, and MVP seed roles/teams are canonical.
- `docs/source/technical-architecture.md` §10.2-10.4, §13.1 plus `docs/source/codebase-design.md` §6.3, §26.3: auth/session behavior belongs behind service functions and tests should exercise module/public API behavior.

## Scope
- Backend only: enrich `GET /api/v1/auth/me/` success `data`.
- No schema changes, new endpoints, frontend wiring, role grants, object permissions, or read audit events.
- Preserve 002D security behavior and compatibility fields.

## TDD Plan
1. RED: Add an API contract assertion proving `/auth/me/` returns `mobile_number`, `roles[{role_code, role_name}]`, and `teams[{team_code, team_name}]` in the standard envelope, while keeping compatibility fields.
2. GREEN: Move payload shaping into `identity.modules.auth_service`, deriving roles, teams, and compatibility codes from the same role/team source.
3. RED/GREEN: Add module-level helper tests for deterministic sorting and exclusion of inactive primary roles, inactive teams, and inactive memberships.
4. Run focused auth API/module tests, then full backend and frontend gates using the required backend interpreter.

## Documentation and Evidence
- Update `docs/working/API_CONTRACTS.md` and save API response examples for success, missing token, expired token, refresh-token misuse, and revoked session.
- Update the epic digest with the 002D3 correction.
- Sharpen the next 1-2 `Not Started` slices using only source/digest material already opened.
- Save terminal logs under `.ralph/runs/2026-07-03_214932_normal_run/evidence/terminal-logs/`.
- Finish with `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, `final-summary.md`, state/progress/handoff updates, and slice status.
