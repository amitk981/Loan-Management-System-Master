# Risk Assessment

Risk level: Medium

- Selected slice: 002G-admin-user-and-role-management-shell
- Mode: normal_run
- Manual review required: no blocker; orchestrator validation and normal review are sufficient.

## Risk Drivers
- RBAC/admin surface: user role/team/status changes can affect access to the platform.
- Session safety: suspending a user must revoke active sessions so a suspended user cannot keep using protected APIs.
- Frontend route/nav surface: the new admin page must not appear for users without mapped `manage_users`.

## Controls Implemented
- Backend gates every admin endpoint through session-bound `validate_access_session()` and canonical user-admin permissions (`users.user.create`, `users.user.update`, `users.user.disable`).
- Frontend maps those canonical permissions to prototype `manage_users` and adds `admin-users` to the existing `allNavItems` / `PAGE_PERMISSIONS` / `visibleStaffNavItems` contract.
- All assignment endpoints bind existing active `Role`/`Team` rows only; no free-text catalogue creation.
- Audit rows are written for role assignment, team add/remove, and status changes.
- Suspending a user revokes active `UserSession` rows with reason `admin_status_suspended`.
- A-014 records and tests the source-silent last active `system_admin` lock-out guard.

## Residual Risk
- The current source data model has one required `primary_role`, not a multi-role assignment table. 002G therefore implements role assignment as changing `users.primary_role` and does not add a role-removal endpoint that would leave a user without a primary role.
- Browser screenshots could not be captured because the in-app browser target was unavailable; visual limitation is recorded in `visual-evidence.md`.
