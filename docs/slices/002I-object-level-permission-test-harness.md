# Slice 002I: Object-Level Permission Test Harness

## Status
Complete

## Parent Epic
Epic 002: Platform Auth and Role Shell
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Add a narrow backend object-level permission harness that future member/application/loan slices can reuse in tests before real object-assignment tables arrive.

## User Value
Future workflow APIs can prove "has module permission" is not enough: object/team assignment scope must be checked independently and denied with the standard envelope when the user is outside scope.

## Depends On
- 002H
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
1. Add a small domain-neutral permission helper module (for example under `sfpcl_credit/identity/modules/`) that evaluates an actor's access to an object using explicit inputs only: actor user id, actor team codes, required canonical permission code, object owner user id, object team code, and an optional `allow_global` flag.
2. The helper must return an allow/deny result with a reason code; it must not query loan/member/application models and must not invent final business rules for future domains.
3. Add a thin test-only fixture or service-level test harness around the helper; do not add public production endpoints solely for the harness.
4. Reuse `auth_service.effective_permission_codes()` for the module-permission side, and `auth_service.team_payload()` / `User.team_codes()` shape for team membership inputs.
5. Keep object access separate from 002H's workflow transition guard: 002H checks action/state/permission, while 002I checks whether the actor is allowed to touch the specific object after permission passes.
6. Start only after 002G2 closes the admin action-permission granularity finding. This helper must accept the exact required canonical permission from the caller and must not collapse distinct permissions into a broad UI/prototype permission such as `manage_users`.

### Verified backend context (2026-07-04, from 002G2)
- Reuse existing symbols (all confirmed present): `auth_service.effective_permission_codes(user)` returns the sorted canonical codes for the active primary role; `User.team_codes()` (`sfpcl_credit/identity/models.py:107`) returns the actor's active team codes; `auth_service.team_payload(user)` returns `[{team_code, team_name}]`.
- Follow the 002G2 pattern for action-specific gating: `admin_users.user_has_action_permission(user, required_codes)` intersects a required-code set with `effective_permission_codes` — the object helper's module-permission side should behave the same way (accept an explicit required code, not a role name).
- Error envelope: use `sfpcl_credit/api.error_response(request, 403, "PERMISSION_DENIED", ...)` for the missing-permission path if any thin test endpoint is added; the helper itself should return a typed result/reason code and let callers translate (mirrors `workflows/guard.py` typed errors from 002H).

## Database/Model Impact
None.

## API Contracts
No new public API endpoint expected. Update `docs/working/API_CONTRACTS.md` only if a shared internal error translation convention is documented.

## Permissions
Apply `docs/source/auth-permissions.md` object/team scope language:
- Source says team/assignment scope limits users to relevant queue/team work.
- If the actor lacks the required canonical permission, deny with `PERMISSION_DENIED`.
- If the actor has the module permission but does not own the object, is not on the object's team, and no explicit global override is supplied, deny as object access denied.
- Unknown access must default to deny and be recorded as approval-required, not auto-allowed.

## Audit Requirements
No audit rows required for the helper itself; future endpoints that call it remain responsible for auditing successful critical actions.

## Validation Rules
Enforce source-doc access-control rules without adding domain business rules.
- The helper accepts only explicit object-scope facts supplied by callers.
- Missing object owner/team facts default to deny unless `allow_global` is true and the actor has the required permission.
- The helper must make the deny reason test-visible (`missing_permission`, `owner_mismatch`, `team_mismatch`, or `scope_unknown`) so future endpoint tests can assert the correct error path.
- Use the 002H boundary explicitly: call the object-scope helper after module permission is known and before future workflow transitions are executed. Do not make the object helper call `evaluate_transition()` or know workflow state names.
- Treat `allow_global=True` as a caller-supplied fact only; the helper must not infer global rights from role names such as `system_admin`, `it_head`, or `credit_manager`.
- Source trace to use in the review packet: `auth-permissions.md` §3/§3.1 says the backend enforces role, team/assignment, object-level, and workflow-state checks; `technical-architecture.md` §7.2 says permissions and services are separate backend layers; `api-contracts.md` §44 says frontend action availability is only UX and backend remains authoritative.
- Regression trace from 002G2: canonical permission codes remain action-specific on the backend; object-scope checks must not use the frontend's coarse prototype permission names as authorization inputs.

## Test Cases
Unit/service/API/permission tests plus frontend tests where UI is touched.
- Backend TDD: actor with required permission and object owner id matches -> allowed.
- Backend TDD: actor with required permission and active team membership matching the object team -> allowed.
- Backend TDD: actor without the required canonical permission -> denied as missing permission.
- Backend TDD: actor with permission but mismatched owner/team -> denied as object access denied.
- Backend TDD: unknown/missing object scope -> denied unless an explicit global override is passed.
- Regression: this helper must not alter existing `/auth/me/`, admin user-management, or tracer permission behavior.

## Visual Acceptance Criteria
None.

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched.

## Risk Level
High

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
