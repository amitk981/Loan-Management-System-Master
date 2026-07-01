# Epic 002-platform-auth-shell: 002: Platform Auth and Role Shell

This parent epic preserves the broad planning context from the earlier Ralph slice. Actual implementation work is broken into smaller child slices under `docs/slices/`.

## Source Broad Slice

# Slice 002: Platform Auth and Role Shell

## Status
Not Started

## Goal
Introduce the production platform foundation: backend project scaffold, JWT auth, users, roles, permissions, protected frontend shell, and health checks.

## User Value
Staff and member users can enter the system through a real authentication boundary, and every later slice can rely on shared RBAC, audit context, and app shell patterns.

## Depends On
- Slice 001

## Source References
- `docs/source/implementation-roadmap.md` sections 10, 20.1, 20.2, 20.3, 21.1, 22.1
- `docs/source/technical-architecture.md` sections 8, 9, 10, 11, 12, 17, 18, 29
- `docs/source/auth-permissions.md`
- `docs/source/api-contracts.md` sections 11, 12, 43, 44
- `docs/source/data-model.md` identity, access, audit, and workflow event tables

## Screens Involved
- Staff login
- Member portal login entry
- Role dashboard
- Sidebar/header/app shell
- Admin user/role management shell

## Prototype Reference
- `sfpcl-lms/src/pages/auth/LoginScreen.tsx`
- `sfpcl-lms/src/pages/Dashboard.tsx`
- `sfpcl-lms/src/components/layout/*`
- `sfpcl-lms/src/contexts/RoleContext.tsx`
- `sfpcl-lms/src/pages/settings/SettingsHub.tsx`

## Frontend Scope
- Replace demo-only auth assumptions with API-backed session state.
- Add protected route handling and role-aware navigation from backend permissions.
- Preserve the current visual shell while adding loading, expired-session, unauthorized, and empty dashboard states.
- Keep demo/mock role switching only behind an explicit development flag if retained.

## Backend/API Scope
- Add backend scaffold following the source architecture direction.
- Implement auth endpoints: login, refresh, logout, current user.
- Implement users, roles, teams, permissions, and seeded permission catalogue.
- Implement permission service and object-access extension point.
- Implement health endpoints and basic audit/workflow event foundation.

## Database/Model Impact
- Users, roles, permissions, role permissions, teams, user-team memberships, sessions/tokens, audit logs, workflow events.
- Non-destructive initial migrations only.

## API Contracts
- Authentication API
- User, role, team APIs
- Current user/dashboard action availability contract

## Permissions
- High-control auth/RBAC area. Backend must reject unauthorized API calls; frontend hiding is not sufficient.

## Validation Rules
- Inactive users cannot authenticate.
- Current-user response includes role, permissions, teams, and available actions.
- Unauthorized users cannot access protected pages or APIs.
- Sensitive user/admin actions create audit events.

## Test Cases
- Auth success/failure/refresh/logout.
- Inactive user blocked.
- Role permission seed and permission service tests.
- Route guard and role-aware nav tests.
- Health endpoint tests.

## Visual Acceptance Criteria
- Login and shell remain visually aligned with the prototype.
- Unauthorized/expired states are clear and do not expose restricted data.

## Evidence Required
- API test output.
- Frontend route guard evidence.
- Build/typecheck/lint/test outputs where configured.
- Screenshot of login, dashboard, and unauthorized state.

## Risk Level
High

## Acceptance Criteria
- Backend scaffold and auth foundation exist.
- Users can log in, refresh, log out, and fetch current user.
- UI shell uses real auth/permissions.
- Backend rejects unauthorized calls.
- Audit logs capture critical auth/admin actions.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates

