# Slice 002D: Current User API with Permissions and Teams

## Status
Not Started

## Parent Epic
Epic 002: Platform Auth and Role Shell
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Add `GET /api/v1/auth/me/` so an authenticated user can retrieve their profile, role, team, permissions, and current action availability from the backend.

## User Value
The frontend shell can stop relying on mock role state and render navigation/actions from the authenticated backend session.

## Depends On
- 002C
- 002C2

## Concrete Requirements
1. Add bearer-token authentication for access tokens issued by the existing login/refresh endpoints.
2. Implement `GET /api/v1/auth/me/` with the standard `{ success, data, meta }` response envelope.
3. Response data must include user identity (`user_id`, `full_name`, `email`, `status`), `role_codes`, `team_codes`, effective permission codes from 002C, and an `available_actions` object/list suitable for the dashboard shell. Effective permissions = the `permission_code`s linked to the user's active `primary_role` via `RolePermission` (`sfpcl_credit/identity/models.py`, seeded by 002C's `catalogue.seed_catalogue`). Return `[]` when the role is inactive (mirror `User.role_codes()`), de-duplicate, and sort for determinism. Note (A-007): `sales_team_user`, `it_head`, and `management_viewer` currently seed with zero links, so `me` will return an empty permission list for them until A-007 is resolved — assert this explicitly rather than treating it as a bug.
4. Reject missing, malformed, expired, wrong-type, or revoked-session access tokens with the existing standard error envelope and `401`.
5. Preserve active-user-only access: suspended/inactive users must not receive current-user data, and their session should be treated consistently with refresh behavior.
6. Use the shared API response helper and auth module boundary from 002C2; do not add a third response helper or put token/session validation directly in the view.
7. Do not add frontend wiring in this slice unless tests require a small fixture update; route-shell wiring remains 002E.

## Source References
- docs/source/implementation-roadmap.md sections 10, 20-22
- docs/source/technical-architecture.md sections 8-12, 17-18
- docs/source/auth-permissions.md
- docs/source/api-contracts.md sections 11-12, 43-44
- docs/source/data-model.md identity/access tables

## Prototype Reference
- sfpcl-lms/src/pages/auth/LoginScreen.tsx
- sfpcl-lms/src/pages/Dashboard.tsx
- sfpcl-lms/src/components/layout/*
- sfpcl-lms/src/contexts/RoleContext.tsx

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
Implement the current-user endpoint only. Reuse the auth/access-token validation module from 002C2 and catalogue data from 002C.

## Database/Model Impact
Non-destructive model/migration changes for this capability, if needed.

## API Contracts
Update `docs/working/API_CONTRACTS.md` with the `/api/v1/auth/me/` request, success data, and auth error cases.

## Permissions
Return permissions from the seeded role-permission catalogue. Do not invent object-level access decisions here; leave object-level extension points to later slices.

## Audit Requirements
No audit event is required for ordinary `me` reads unless source docs opened during the slice explicitly require read auditing.

## Validation Rules
Only active users with active sessions and valid access tokens can call `me`. Token `token_type` must be `access`.

## Test Cases
- New test: logged-in active user can call `GET /api/v1/auth/me/` and receives profile, role codes, team codes, permissions, and available actions in the standard envelope.
- New test: missing bearer token returns `401` with the standard error envelope.
- New test: expired access token returns `401 TOKEN_EXPIRED`.
- New test: refresh tokens cannot be used against `me`.
- New test: inactive user or revoked session cannot retrieve current-user data.
- New test: `me` uses the standard meta keys, including `api_version`, through the shared response helper.

## Visual Acceptance Criteria
None.

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched.

## Risk Level
High

## Acceptance Criteria
- `/api/v1/auth/me/` is documented in `docs/working/API_CONTRACTS.md`.
- Backend tests cover success and auth failure cases.
- Existing login, refresh, logout, health, frontend test/typecheck/build gates remain green.
- The implementation stays within one small Ralph slice.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested, if needed
- [ ] Audit events tested, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
