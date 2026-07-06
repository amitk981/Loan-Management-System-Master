# Review Packet: 2026-07-04_140900_normal_run

## Result
Complete — all gates green.

## Slice
002G2-admin-user-action-permission-granularity (High risk, corrective from architecture
review 2026-07-04_135247).

## What was asked vs. what was built (traceability, for a non-developer)
The architecture review found that the admin user-management API (built in 002G) let a
staff member perform ANY user action — reassign roles, change teams, suspend accounts —
as long as they held ANY ONE of the three "user admin" permissions. The permission
document (`auth-permissions.md` §12.1) says those are four separate, risk-rated
permissions. So a future limited role could accidentally suspend users just because it
could, say, create them.

This slice makes each action check its OWN permission:

| The document says (auth-permissions.md) | The code now does | Proven by test |
| --- | --- | --- |
| §12.1: `users.user.read`, `.create`, `.update`, `.disable` are distinct | Each admin action requires its specific permission | all 4 partial-role tests below |
| §19: `/settings/users` → `users.user.read` | List/detail require `users.user.read` OR a write user-admin permission (A-015 fallback) | `test_read_only_user_admin_can_list_but_cannot_write` |
| §12.1 `users.user.update` = update users | Role assignment + team add/remove require `users.user.update` | `test_update_only_role_can_assign_but_cannot_suspend`, `test_disable_only_role_can_suspend_but_cannot_assign` |
| §12.1 `users.user.disable` = disable users | Suspending a user requires `users.user.disable`; restore-to-active requires `users.user.update` | `test_create_only_role_...`, `test_update_only_role_...`, `test_disable_only_role_...` |
| §15.12: System Administrator keeps create/update/disable | Seeded `system_admin` still does everything (no regression) | existing 002G tests still pass |

## Behavior guarantees verified by tests
- A create-only role: cannot assign roles, add/remove teams, or suspend (all `403`); can
  still read (holds a user-admin permission).
- An update-only role: can assign roles, add teams, restore users to active; CANNOT
  suspend (`403`).
- A disable-only role: can suspend (session revoked, audit written); CANNOT assign roles
  or teams (`403`).
- A read-only user-admin role: can list/detail; CANNOT write (`403`).
- Every forbidden write produces NO `AuditLog` row and does NOT revoke the target's
  session (permission is enforced before mutation).
- Check order preserved: `401` (auth) → `403` (permission) → `400`/`404`.
- 002G behavior unchanged: last-active-`system_admin` lock-out, suspend session
  revocation, envelope/pagination, and role/team serialization shape.

## Files changed
See `changed-files.txt`.

## Evidence
- `evidence/terminal-logs/backend-red.log` — 4 new tests failing before implementation.
- `evidence/terminal-logs/backend-green.log` — same 9 admin tests passing after.
- `evidence/terminal-logs/backend-full-coverage.log` — 79 tests pass, coverage 95%.
- `evidence/terminal-logs/frontend-gates.log` — typecheck/lint/test/build green.
- `evidence/api-responses/admin-user-action-permission-examples.md` — partial-permission
  `403` examples and the full per-action permission table.

## Assumptions
- A-015 (new): read gate accepts write user-admin permissions because seeded
  `system_admin` lacks `users.user.read`. See `docs/working/ASSUMPTIONS.md`.

## Recommended Next Action
Proceed to `002I-object-level-permission-test-harness`, then
`002J-api-contract-test-harness`.
