# Slice 002D: Current User API with Permissions and Teams

## Status
Complete

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

### Concrete starting points (observed 2026-07-03 after 002C2)
- Access-token validation is ready: call `from sfpcl_credit.identity.modules import auth_service` then `claims = auth_service.validate_access_token(access_token)`. It decodes/verifies signature, expiry, and `token_type == "access"`, raising `tokens.TokenError` (`.code` in `TOKEN_EXPIRED` / `INVALID_TOKEN`) on failure. Extract the raw token from the `Authorization: Bearer <token>` header in the view (thin), and translate `TokenError` via `sfpcl_credit.api.error_response(request, 401, exc.code, exc.message)`.
- A-008 is the open decision: `validate_access_token` is currently **stateless** (no session lookup), so a logged-out user's still-valid access token would pass. Requirement 5 ("revoked session cannot retrieve current-user data") means 002D should either extend `auth_service` with a session-bound validator (e.g. `validate_access_session(access_token)` that loads `UserSession` by `claims["session_id"]`, checks `is_active()` and `user.can_authenticate()`, mirroring `validate_refresh_session`) or add that check in a new `me` service function. Put the choice behind the auth module boundary, not in the view. Update A-008 to Resolved when done.
- Effective permissions query: `Permission.objects.filter(role_permissions__role=user.primary_role).values_list("permission_code", flat=True)` — return `sorted(set(...))`, and `[]` when `user.primary_role.status != "active"` (mirror `User.role_codes()`). Models: `RolePermission.role`/`.permission` in `sfpcl_credit/identity/models.py`.
- Envelope: success via `sfpcl_credit.api.success_response(data, request)`; meta keys `request_id`/`timestamp`/`api_version` come for free. Add a module-level test for the permission-resolution function (not just the HTTP view), consistent with 002C2's `test_auth_module.py`.
- URL: add `path("api/v1/auth/me/", me, name="auth-me")` in `sfpcl_credit/config/urls.py`; the view is GET-only (`@require_GET`).

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
- New module-level test: the permission-resolution function returns sorted, de-duplicated `RolePermission.permission.permission_code` values for the active primary role, and returns `[]` for inactive-role / A-007 zero-link roles.
- New guardrail test or assertion: no `/auth/me/` view logic performs direct token/session/permission orchestration that belongs in the auth module boundary.

## Visual Acceptance Criteria
None.

## Evidence Required
TDD red/green evidence must be saved in committed run artifacts with paths that actually exist in the final review packet:
- initial failing backend test output for `/api/v1/auth/me/`;
- green full backend test output, backend check, migration check, and coverage;
- frontend typecheck/tests/build output, even though no frontend files should change;
- API response examples for success, missing token, expired token, refresh-token misuse, and revoked-session rejection.
Screenshots are required only if frontend is touched.

## Risk Level
High

## Acceptance Criteria
- `/api/v1/auth/me/` is documented in `docs/working/API_CONTRACTS.md`.
- Backend tests cover success and auth failure cases.
- Existing login, refresh, logout, health, frontend test/typecheck/build gates remain green.
- The implementation stays within one small Ralph slice.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated, if needed
- [x] Database rules followed, if needed
- [x] Permissions tested, if needed
- [x] Audit events tested, if needed
- [x] Visual evidence saved, if frontend
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates
