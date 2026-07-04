# Slice 002G: Admin User and Role Management Shell

## Status
Not Started

## Parent Epic
Epic 002: Platform Auth and Role Shell
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Give a `system_admin` a read + assignment shell over the existing seeded identity catalogue: list staff users, view one user's roles/teams/status, and change a user's role assignments, team memberships, and active status — all through the backend service/envelope path, never by inventing new business rules.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 002EYA
- 002F
- 002F2
- 002FL

## Concrete Requirements
1. Read-only list endpoint `GET /api/v1/admin/users/` returning each user's `user_id`, `full_name`, `email`, `mobile_number` (masked per existing masking rules if applicable), `status`, `roles[{role_code, role_name}]`, and `teams[{team_code, team_name}]` in the standard envelope with pagination per `api-contracts.md` §7-8. Reuse the same role/team serialization shape already built for `/auth/me/` (002D3) — do not fork a second shape.
2. Detail endpoint `GET /api/v1/admin/users/{user_id}/` returning the same shape for one user.
3. Assignment endpoints that only bind existing catalogue rows (no free-text role/permission creation): assign/remove a `Role` (`role_permissions` are NOT edited here — the catalogue seed owns them), add/remove a `UserTeamMembership`, and set `status` (active/suspended) — each writing an `AuditLog` row (`actor_type="user"`, action like `admin.user.role_assigned` / `admin.user.status_changed`, old/new value JSON) exactly as the tracer and auth services already do.
4. Every endpoint requires the `manage_users` canonical permission (seeded to `system_admin`); a session without it returns `403 PERMISSION_DENIED`; unauthenticated returns the standard `401`. Reuse the session-bound `validate_access_session` + `effective_permission_codes` gate from the auth/tracer views.
5. Suspending a user must revoke that user's active `UserSession` rows so a suspended user cannot keep calling protected APIs (consistent with the 002D/A-008 active-session rule). Do not let an admin suspend or remove the last `system_admin` (lock-out guard) — record this guard's exact rule in `ASSUMPTIONS.md` if the source docs are silent.
6. Frontend: wire the admin shell using existing prototype patterns only (`RoleContext`, existing table/list and status-badge components); no new styling. Gate the screen and its actions behind explicit backend canonical permissions mapped through `authSession.ts` (no role-name checks).
7. Navigation: add the admin user-management entry only for sessions whose canonical permissions map to `manage_users`; non-admin, zero-permission, and unknown-role sessions must not see the nav item or action buttons. Keep the existing Settings shortcut gated by `view_settings`.
8. Route guard: add the new admin page to the same shared page-permission contract introduced in 002F/002F2 (`navigationPermissions.ts`) and extend its render/visibility tests so direct navigation without `manage_users` falls back to Dashboard with the access-blocked banner.
9. Current-user compatibility: continue using `/auth/me/` `roles`, `teams`, `permissions`, and `available_actions`; do not introduce frontend grants for unmapped canonical permissions.
10. Save concrete API examples for list, detail, successful assignment, `401`, `403`, validation failure, and last-system-admin lock-out under the run folder, and reference those files from the review packet.
11. If source documents remain silent on the exact last-system-admin rule, record the chosen guard in `docs/working/ASSUMPTIONS.md` before implementation; default to blocking any change that would leave zero active users with the `system_admin` primary role.
12. Extend the 002F2 navigation contract rather than adding a parallel admin visibility path: the Admin user-management nav item must be in `allNavItems`, the page must be in `PAGE_PERMISSIONS`, `Sidebar` must expose it only through `visibleStaffNavItems(allNavItems, can)`, and regression tests must prove zero-permission, unknown-role, tracer-only, and users lacking `manage_users` cannot see or directly navigate to it.

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
Admin user/role management shell reachable from the existing staff app shell only when the current backend session maps to `manage_users`.

## Frontend Scope
Add the admin user-management page using existing app-shell, table/list, status badge, alert, modal, and form-control patterns only. Show list, detail, role assignment, team membership, and active/suspended controls from backend data; include loading, empty, error, unauthorized, validation, and success states without new styling.

## Backend/API Scope
Implement only the admin user catalogue read/assignment endpoints named above. Reuse the existing identity models, session-bound auth helper, standard envelope helper, and audit-log model; do not add free-text role, permission, or team creation.

## Database/Model Impact
Prefer no schema change. If a gap is found, keep it non-destructive and limited to existing identity/access needs; do not alter the seeded permission catalogue except through existing `Role`/`Permission` rows.

## API Contracts
Update `docs/working/API_CONTRACTS.md` with the admin user list/detail/assignment routes, pagination shape, success examples, and `401`/`403`/validation/lock-out errors.

## Permissions
Apply the role and object-access rules from `docs/source/auth-permissions.md`; classify unknown access as approval-required.

## Audit Requirements
Record audit/workflow events for critical create/update/approval/access actions.

## Validation Rules
Enforce source-doc business rules and block invalid state transitions.
- Assignments must reference existing active `Role`/`Team` rows by code or id; unknown values return a standard validation error.
- Status changes are limited to active/suspended unless source documents explicitly define another admin-settable state.
- The last active `system_admin` lock-out guard must be tested and recorded in `ASSUMPTIONS.md` if still source-doc-silent.

## Test Cases
Unit/service/API/permission tests plus frontend tests where UI is touched.
- Backend TDD: unauthenticated `401`, missing `manage_users` `403`, list/detail success envelope, assignment success, audit-log write, session revocation when status becomes suspended, and lock-out guard for last `system_admin`.
- Frontend TDD: system-admin user can reach the admin shell; non-admin/zero-permission/tracer-only users cannot see or navigate to it; role/team/status actions are hidden without `manage_users`.
- Navigation TDD: add a red/green assertion to `navigationPermissions.test.ts` that the new admin route is hidden and guarded without `manage_users`, and visible/allowed when canonical `users.user.create|update|disable` maps to prototype `manage_users`.
- Contract evidence: saved API response examples match `docs/working/API_CONTRACTS.md` and the frontend consumes the same role/team serialization shape as `/auth/me/`.

## Visual Acceptance Criteria
Match the existing prototype patterns and include loading, empty, error, unauthorized, validation, and success states where relevant.

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
