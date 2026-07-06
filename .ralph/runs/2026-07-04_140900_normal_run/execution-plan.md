# Execution Plan — 002G2 Admin User Action Permission Granularity

## Slice
`002G2-admin-user-action-permission-granularity` (High risk). Corrective slice from
architecture review `2026-07-04_135247`.

## Problem (as merged in 002G)
`sfpcl_credit/identity/admin_views.py::_authenticated_admin` gates every admin
user-management endpoint (list, detail, assign_role, add/remove team, set_status)
behind a single `has_manage_users_permission()` check that returns true if the actor
holds **any** of `users.user.create`, `users.user.update`, `users.user.disable`.
`auth-permissions.md` §12.1 defines those as distinct risk-rated permissions, so a
future partial user-admin role could suspend users or reassign roles/teams with only
one unrelated grant.

## Target behavior (action-aware gating)
Per-action required canonical permission codes (module `admin_users.py`):
- **Read** (`GET` list + detail): `users.user.read` OR any of create/update/disable.
  `system_admin` is seeded with create/update/disable but NOT `users.user.read`
  (`catalogue.py` lines 434-451), so read must accept the write set to preserve
  current access. Recorded as A-015 compatibility assumption.
- **Assignment** (assign_role, add_team, remove_team): `users.user.update`.
- **Status -> suspended** (set_status "suspended"): `users.user.disable`.
- **Status -> active restore** (set_status "active"): `users.user.update`.
- **Status -> unknown value**: require update OR disable so the service still returns
  the existing `400 VALIDATION_ERROR` for the bad status rather than masking it as 403.

Ordering preserved: `401` (auth) -> `403` (permission) -> `400`/`404` (body/validation).
Permission is enforced BEFORE any mutation, so forbidden partial-permission writes
create no `AuditLog` row and revoke no target session.

## Files to change
1. `sfpcl_credit/identity/modules/admin_users.py`
   - Add per-action permission-code sets + `user_has_action_permission(user, codes)`
     and `status_permission_codes(status)`. Keep `has_manage_users_permission` +
     `MANAGE_USERS_PERMISSION_CODES` (still exported) as the read union set; add
     read/assignment/suspend/restore sets.
2. `sfpcl_credit/identity/admin_views.py`
   - `_authenticated_admin(request, required_codes)` — authenticate session, then check
     the passed action codes. Each view passes its action's codes; `set_status` parses
     the body first to pick suspend vs restore codes.
3. `sfpcl_credit/tests/test_admin_users_api.py` — add partial-role regression tests
   (TDD: written first, red, then green).
4. `docs/working/API_CONTRACTS.md` — note action-specific permission gating.
5. `docs/working/ASSUMPTIONS.md` — A-015 (read gate accepts write set because
   `system_admin` lacks the seeded `users.user.read` grant).
6. `docs/working/digests/epic-002-platform-auth.md` — 002G2 done note.

## Frontend
No frontend change. Requirement 6 permits nav/route visibility to keep using prototype
`manage_users`; the default seeded `system_admin` holds all three write permissions so
no button implies rejected authority today. Recorded in risk assessment.

## TDD sequence
1. Write failing tests: partial roles (create-only, update-only, disable-only) plus the
   negative side-effect assertions. Save RED log.
2. Implement action-aware gate. Save GREEN log + full-suite + coverage logs.
3. Save API `403` example for a partial-permission suspend attempt.

## Gates
Backend: `manage.py check`, full test suite, `makemigrations --check` (no schema
change expected), coverage >= 85%. Frontend gates unaffected (no FE change) but run
build/typecheck/lint/test to confirm green. Interpreter:
`/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python`.
