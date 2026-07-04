# Risk Assessment — 002G2 Admin User Action Permission Granularity

Risk level: **High** (slice-declared). This slice changes the authorization boundary
of the admin user-management API — a security-sensitive control.

## What changed
- Backend only. `sfpcl_credit/identity/admin_views.py` and
  `sfpcl_credit/identity/modules/admin_users.py`. No schema change (migration check
  clean), no new dependency, no frontend change.
- Replaced the single "any user-admin permission = full authority" gate with
  per-action canonical permission checks (read / assignment / suspend / restore).

## Why the change is safe
- **No regression to seeded `system_admin`.** `system_admin` holds
  create/update/disable, so it still passes read (fallback), assignment (update),
  suspend (disable), and restore (update). Existing 002G behavior tests
  (list/detail/assignment/status/last-admin lock-out) still pass unchanged.
- **Fail-closed for partial roles.** New regression tests prove create-only,
  update-only, disable-only, and read-only roles are each restricted to exactly the
  actions their permission authorises; every denied write returns
  `403 PERMISSION_DENIED` and produces no `AuditLog` row and no session revocation
  (permission is checked before any mutation).
- **Ordering preserved:** `401` (auth) → `403` (permission) → `400`/`404`
  (body/validation). The last-active-`system_admin` lock-out guard and suspend session
  revocation are unchanged.

## Assumptions / judgement calls
- **A-015 (new):** read gate accepts `users.user.read` OR any write user-admin
  permission, because the seeded `system_admin` role lacks `users.user.read`
  (`catalogue.py`); a strict read-only gate would lock the only seeded user-admin out.
  Not a business-rule invention — write actions remain gated by their §12.1 permission,
  and no new seed grant was fabricated. Tighten to `{users.user.read}` if source docs
  later add that grant.

## Frontend
No frontend change (slice req 6 permits nav/route visibility to keep using prototype
`manage_users`). The default seeded `system_admin` holds all three write permissions,
so no visible action button implies authority the backend now rejects. Partial
user-admin roles do not yet exist (role management is a later slice); when they do, the
frontend action-visibility follow-up should reuse existing UI patterns only.

## Gates
- Backend: `manage.py check` clean; `makemigrations --check` "No changes detected";
  79 tests pass; coverage 95% (floor 85%).
- Frontend (unchanged, confirmed green): typecheck, lint, 26 vitest tests, build.
- Protected files: none modified.

Standing approval applies (`docs/working/HIGH_RISK_APPROVALS.md`); no `[revoked]` entry
for this slice.
