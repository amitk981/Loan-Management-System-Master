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
- 002F

## Concrete Requirements
1. Read-only list endpoint `GET /api/v1/admin/users/` returning each user's `user_id`, `full_name`, `email`, `mobile_number` (masked per existing masking rules if applicable), `status`, `roles[{role_code, role_name}]`, and `teams[{team_code, team_name}]` in the standard envelope with pagination per `api-contracts.md` §7-8. Reuse the same role/team serialization shape already built for `/auth/me/` (002D3) — do not fork a second shape.
2. Detail endpoint `GET /api/v1/admin/users/{user_id}/` returning the same shape for one user.
3. Assignment endpoints that only bind existing catalogue rows (no free-text role/permission creation): assign/remove a `Role` (`role_permissions` are NOT edited here — the catalogue seed owns them), add/remove a `UserTeamMembership`, and set `status` (active/suspended) — each writing an `AuditLog` row (`actor_type="user"`, action like `admin.user.role_assigned` / `admin.user.status_changed`, old/new value JSON) exactly as the tracer and auth services already do.
4. Every endpoint requires the `manage_users` canonical permission (seeded to `system_admin`); a session without it returns `403 PERMISSION_DENIED`; unauthenticated returns the standard `401`. Reuse the session-bound `validate_access_session` + `effective_permission_codes` gate from the auth/tracer views.
5. Suspending a user must revoke that user's active `UserSession` rows so a suspended user cannot keep calling protected APIs (consistent with the 002D/A-008 active-session rule). Do not let an admin suspend or remove the last `system_admin` (lock-out guard) — record this guard's exact rule in `ASSUMPTIONS.md` if the source docs are silent.
6. Frontend: wire the admin shell using existing prototype patterns only (`RoleContext`, existing table/list and status-badge components); no new styling. Gate the screen and its actions behind `manage_users`. A non-admin never sees the nav item or action buttons.

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
Relevant prototype screen area for this capability.

## Frontend Scope
Small UI wiring for the named workflow, if applicable.

## Backend/API Scope
Implement the named backend/API capability only.

## Database/Model Impact
Non-destructive model/migration changes for this capability, if needed.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Apply the role and object-access rules from `docs/source/auth-permissions.md`; classify unknown access as approval-required.

## Audit Requirements
Record audit/workflow events for critical create/update/approval/access actions.

## Validation Rules
Enforce source-doc business rules and block invalid state transitions.

## Test Cases
Unit/service/API/permission tests plus frontend tests where UI is touched.

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
