# Execution Plan

Selected slice: 002G-admin-user-and-role-management-shell

## Scope
- Add the admin user-management API under `/api/v1/admin/users/`.
- Reuse the existing identity models, `/auth/me/` role/team serialization shape, standard API envelope, pagination metadata, session-bound access validation, effective permission checks, and `AuditLog`.
- Add frontend route, navigation item, and admin shell behind canonical `manage_users` permission mapping only, using existing page/table/status/modal/form patterns.
- Update API contracts, assumptions, run evidence, state, progress, handoff, and slice status.

## TDD Plan
1. Backend RED/GREEN cycles:
   - permission gate: unauthenticated `401`, authenticated without `manage_users` `403`, system admin list/detail success envelope.
   - assignment actions: role assign/remove, team add/remove, status change.
   - audit/session safety: audit log on assignment/status changes, suspend revokes active sessions, last active `system_admin` guard blocks lock-out.
2. Frontend RED/GREEN cycles:
   - navigation contract exposes Admin Users only when canonical backend permissions map to `manage_users`.
   - direct route guard falls back to Dashboard with access-blocked banner without `manage_users`.
   - admin shell renders for permitted sessions and hides action controls without `manage_users`.

## Implementation Plan
1. Inspect existing identity tests, auth service helpers, URL routing, API helpers, frontend auth-session mapping, navigation contract, and page patterns.
2. Record the last-system-admin guard assumption before implementing because the digest says source docs are silent.
3. Add focused backend API tests first, capture red output, then implement thin views/service helpers.
4. Add focused frontend tests first, capture red output, then implement route/nav/page wiring with existing styles.
5. Save API examples for list, detail, assignment, `401`, `403`, validation failure, and lock-out under this run folder.
6. Run quality gates with the mandated backend interpreter:
   - `/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python sfpcl_credit/manage.py check`
   - backend tests, migration check, and coverage
   - `npm run lint`, `npm run typecheck`, `npm test`, `npm run build` in `sfpcl-lms/`
7. Sharpen the next 1-2 Not Started slices using only the source/digest context opened for this run.
