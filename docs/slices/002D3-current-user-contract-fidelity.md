# Slice 002D3: Current User Contract Fidelity

## Status
Not Started

## Parent Epic
Epic 002: Platform Auth and Role Shell
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Bring `GET /api/v1/auth/me/` into fidelity with the source API contract before frontend route-shell wiring depends on it.

## User Value
The frontend shell receives enough current-user profile, role, and team detail from one backend call, without baking in a reduced contract that later screens must undo.

## Depends On
- 002D
- 002D2

## Source References
- `docs/source/api-contracts.md` §5.3, §6.1, §6.4, §11.4
- `docs/source/auth-permissions.md` §5.3, §8.2, §34.1, §38.1
- `docs/source/technical-architecture.md` §10.2-10.4, §13.1
- `docs/source/codebase-design.md` §6.3, §26.3

## Concrete Requirements
1. Preserve all 002D security behavior: `Authorization: Bearer <access_token>`, signed/unexpired `access` token, active `UserSession`, active user, shared `{ success, data, meta }` envelope, `401 AUTH_REQUIRED`, `401 TOKEN_EXPIRED`, and `401 INVALID_TOKEN` cases.
2. Extend the `/api/v1/auth/me/` success `data` to include source-contract profile and relationship details:
   - `user_id`
   - `full_name`
   - `email`
   - `mobile_number`
   - `status`
   - `roles`: array of objects with at least `role_code` and `role_name`
   - `teams`: array of objects with at least `team_code` and `team_name`
   - `permissions`: sorted, de-duplicated effective permission codes
3. Keep `role_codes`, `team_codes`, and `available_actions` as additive compatibility fields for 002E unless a test proves they are unused. They must be derived from the same role/team/permission source, not duplicated logic.
4. Inactive primary roles must produce `roles: []`, `role_codes: []`, and `permissions: []`.
5. Active team memberships must produce deterministic `teams` sorted by `team_code`; inactive memberships or inactive teams must be excluded.
6. Update `docs/working/API_CONTRACTS.md` and API examples to show the enriched `/auth/me/` response.
7. Keep the auth view thin; payload shaping belongs in `auth_service` or a local auth module function, with module-level tests.

## Backend/API Scope
Backend current-user response shape only. Do not add new endpoints, new roles, new permissions, object-level permission rules, or frontend wiring.

## Frontend Scope
None. 002E consumes the corrected contract.

## Database/Model Impact
None expected.

## Permissions
Continue resolving permissions from active `RolePermission` links for the active primary role. Do not invent grants for A-007 zero-link roles.

## Audit Requirements
No audit event is required for ordinary current-user reads unless source docs are updated to require read auditing.

## Test Cases
- Backend API test: successful `/api/v1/auth/me/` returns `mobile_number`, `roles[{role_code, role_name}]`, and `teams[{team_code, team_name}]` in the standard envelope.
- Backend API test: compatibility fields `role_codes`, `team_codes`, and `available_actions` remain present and match the richer `roles`/`teams`/`permissions` data.
- Module test: role/team payload helpers return deterministic sorted data and exclude inactive roles, inactive teams, and inactive memberships.
- Regression tests from 002D remain green: missing token, expired token, refresh-token misuse, inactive user, revoked session, sorted permissions, and thin-view guardrail.
- API examples include success, missing token, expired token, refresh-token misuse, and revoked-session rejection.

## Evidence Required
- TDD red/green `/auth/me` contract test logs in `evidence/terminal-logs/`.
- Backend check/tests/migrations/coverage logs.
- Frontend typecheck/tests/build logs to prove no current frontend break.
- Updated API response examples.

## Risk Level
Medium

## Acceptance Criteria
- `/api/v1/auth/me/` matches the source contract's current-user profile, roles, teams, and permissions shape while preserving 002D security behavior.
- No frontend route-shell code is wired to the reduced 002D response shape.
- API contracts and examples match implemented behavior.
- All gates pass.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Database rules followed, if needed
- [ ] Permissions tested
- [ ] Audit events tested, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
