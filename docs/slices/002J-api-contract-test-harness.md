# Slice 002J: API Contract Test Harness

## Status
Complete

## Parent Epic
Epic 002: Platform Auth and Role Shell
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Add a narrow backend API contract test harness so future endpoint slices can assert the standard SFPCL response envelope, error shape, pagination metadata, and `available_actions` shape without duplicating ad hoc assertions.

## User Value
Future API slices can prove contract fidelity consistently: every protected endpoint keeps the same `success`/`data`/`error`/`meta` conventions, and frontend code can rely on stable error and action-availability shapes.

## Depends On
- 002I
- 002G2

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
1. Add a test-only contract assertion helper module under `sfpcl_credit/tests/` or a shared testing utility path. It must not be imported by production views/services.
2. Cover standard success envelopes: `success: true`, `data`, and `meta.request_id`, `meta.timestamp`, `meta.api_version == "v1"`.
3. Cover standard error envelopes: `success: false`, `error.code`, `error.message`, and the same required `meta` keys.
4. Cover common protected-endpoint errors already present in the platform: `401 AUTH_REQUIRED`/`INVALID_TOKEN`, `403 PERMISSION_DENIED`, and `409 INVALID_STATE_TRANSITION`.
5. Cover pagination metadata shape for list endpoints using the existing admin users list as the concrete current endpoint.
6. Cover `available_actions` item shape from `api-contracts.md` §44 using an internal helper/sample, not a new public endpoint.
7. Add regression tests proving existing auth/me, admin users, and tracer endpoints satisfy the helper without changing their public response bodies.
8. Include an admin-users permission-denied fixture from 002G2: a partial user-admin role that lacks the action-specific permission must produce the same standard `403 PERMISSION_DENIED` envelope as fully unauthorized users. Reuse `test_admin_users_api._partial_admin_headers(role_code, permission_codes)` (added in 002G2) as the fixture pattern for a single-permission role, e.g. `["users.user.create"]` calling a `users.user.update`-gated action.

### Verified current envelope shapes (2026-07-04, from `sfpcl_credit/api.py`)
Assert against the shapes the platform actually returns today; do not invent fields:
- Success (`success_response`): `{ "success": true, "data": <obj>, "meta": {request_id, timestamp, api_version} }`. `meta.request_id` is `null` unless the request sent an `X-Request-ID` header.
- List (`list_response`): adds a TOP-LEVEL `pagination` object (sibling of `data`, not inside `meta`) with keys `page, page_size, total_count, total_pages, has_next, has_previous`. Admin users list is the concrete endpoint.
- Error (`error_response`): `{ "success": false, "error": {code, message, details, field_errors}, "meta": {...} }`. `details` defaults to `{}`; `field_errors` defaults to `{}` and carries per-field messages for `400 VALIDATION_ERROR` (e.g. admin `status`/`role_code`).
- `available_actions`: the current `/auth/me/` payload returns `available_actions` as a FLAT list of canonical permission-code strings (equal to `permissions`), NOT objects. The §44 item shape (`action_code`, `label`, `enabled`, `disabled_reason`, `required_permission`) is the TARGET contract — assert it against an internal sample/helper only, and record in ASSUMPTIONS if the harness sample diverges from current `/auth/me/` output so a later slice reconciles `available_actions`.

### Verified permission-harness context (2026-07-04, from 002I)
- `sfpcl_credit.identity.modules.object_permissions.evaluate_object_access(...)` is the reusable object-scope helper. It returns `ObjectAccessResult(allowed, reason, error_code, required_permission, approval_required)` and never queries domain models.
- Missing module permission returns reason `missing_permission` and error code `PERMISSION_DENIED`.
- Object-scope denials return error code `OBJECT_ACCESS_DENIED` with reason `owner_mismatch`, `team_mismatch`, or `scope_unknown`; `scope_unknown` also sets `approval_required=True`.
- Future API slices should translate helper results into the standard error envelope asserted by this 002J harness. Do not add a public endpoint only to test 002I.

## Database/Model Impact
None.

## API Contracts
No new public API endpoint is expected. Update `docs/working/API_CONTRACTS.md` only if the run discovers a mismatch in existing documented envelope/error/action examples.

## Permissions
Use existing session-bound auth and seeded permissions only. The harness must assert permission-denied response shape, not introduce new permission codes or grant rules.

## Audit Requirements
No production audit rows are required for the harness itself. Regression tests may assert that existing tracer success paths still create audit/workflow rows, but the harness must not add new audited actions.

## Validation Rules
- Helper assertions must fail with clear messages naming the missing contract field.
- Do not relax endpoint behavior to satisfy the helper; if an endpoint is non-compliant, fix the endpoint or document a follow-up according to source contracts.
- Keep the helper test-only and independent from Django model business rules.
- Source trace to use in the review packet: `api-contracts.md` §6.1 for success envelopes (also captured in `docs/working/digests/epic-002-platform-auth.md`), §7.3 for `INVALID_STATE_TRANSITION`, §42 for audit/workflow response item conventions, §43 for dashboard response examples, and §44 for `available_actions`.

## Test Cases
- Backend TDD: write a failing helper test against a deliberately incomplete sample envelope, then implement the helper.
- Backend API regression: `/api/v1/auth/me/` success passes the success-envelope assertion.
- Backend API regression: unauthenticated protected endpoint returns a helper-validated `401` error envelope.
- Backend API regression: admin users without manage-user permission returns helper-validated `403 PERMISSION_DENIED`.
- Backend API regression: admin user-management partial-permission denials from 002G2 return helper-validated `403 PERMISSION_DENIED` and do not leak a non-standard validation shape.
- Backend API regression: tracer invalid state returns helper-validated `409 INVALID_STATE_TRANSITION`.
- Backend API regression: admin users list passes pagination-shape assertions.
- Backend helper unit: `available_actions` sample with `action_code`, `label`, `enabled`, `disabled_reason`, and `required_permission` passes; missing required fields fail.

## Visual Acceptance Criteria
None.

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched.

## Risk Level
Medium

## Acceptance Criteria
- The named capability works through the intended backend/API/frontend path, where applicable.
- Source-doc business rules are enforced or documented as assumptions.
- Permissions and audit expectations are tested when applicable.
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
