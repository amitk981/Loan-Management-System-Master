# 002G2 — Admin user action permission granularity: API examples

All admin user-management endpoints require a session-bound bearer access token
(`Authorization: Bearer <access_token>`). Beyond that, each action now requires a
specific canonical user-admin permission (`auth-permissions.md` §12.1) rather than any
single user-admin grant:

| Action | Endpoint | Required permission (any one of) |
| --- | --- | --- |
| List / detail (read) | `GET /api/v1/admin/users/`, `GET /api/v1/admin/users/{id}/` | `users.user.read`, `users.user.create`, `users.user.update`, `users.user.disable` |
| Assign role | `POST /api/v1/admin/users/{id}/roles/` | `users.user.update` |
| Add / remove team | `POST` / `DELETE /api/v1/admin/users/{id}/teams/...` | `users.user.update` |
| Suspend user | `PATCH /api/v1/admin/users/{id}/status/` `{"status":"suspended"}` | `users.user.disable` |
| Restore user to active | `PATCH /api/v1/admin/users/{id}/status/` `{"status":"active"}` | `users.user.update` |

The read gate accepts the write permissions because the seeded `system_admin` role
holds create/update/disable but not `users.user.read` (see ASSUMPTIONS A-015).

## Example: partial-permission 403 (update-only role attempts to suspend)

Actor holds only `users.user.update`. Suspend requires `users.user.disable`.

Request:

```
PATCH /api/v1/admin/users/{target_user_id}/status/
Authorization: Bearer <update-only access token>
Content-Type: application/json

{ "status": "suspended" }
```

Response `403 Forbidden`:

```json
{
  "success": false,
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "You do not have permission to perform this user-management action.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-04T14:09:00Z",
    "api_version": "v1"
  }
}
```

No `AuditLog` row is written and no target `UserSession` is revoked (verified by
`test_update_only_role_can_assign_but_cannot_suspend`).

## Example: partial-permission 403 (disable-only role attempts role assignment)

Actor holds only `users.user.disable`. Assignment requires `users.user.update`.

Request:

```
POST /api/v1/admin/users/{target_user_id}/roles/
Authorization: Bearer <disable-only access token>
Content-Type: application/json

{ "role_code": "accounts_head" }
```

Response `403 Forbidden` (same envelope as above, `error.code = "PERMISSION_DENIED"`).
The target's `primary_role` is unchanged and no `admin.user.role_assigned` audit row is
written (verified by `test_disable_only_role_can_suspend_but_cannot_assign`).

## Example: allowed action (disable-only role suspends a user)

Same disable-only actor, `PATCH .../status/ {"status":"suspended"}` returns `200` with
the updated user item; the target's active `UserSession` rows are revoked with reason
`admin_status_suspended` and an `admin.user.status_changed` audit row is written.

Behaviour is covered by `sfpcl_credit/tests/test_admin_users_api.py`
(`backend-green.log`, `backend-full-coverage.log`).
