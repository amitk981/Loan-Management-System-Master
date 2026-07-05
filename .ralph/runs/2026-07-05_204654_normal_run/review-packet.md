# Review Packet: 2026-07-05_204654_normal_run

## Result
PASS — all gates green.

## Slice
003G2-dashboard-internal-auditor-access-regression (Medium risk, backend/API only).

## Plain-English summary (for a non-developer)
An internal auditor is supposed to see a read-only "compliance" dashboard. The backend had a mismatch:
the dashboard code listed the internal auditor as a compliance-dashboard user, but the permission
catalogue never gave that role the key it needs to open the dashboard. So once the dashboard screen is
connected to the backend, an internal auditor would have been shown a "permission denied" error instead
of their dashboard. This fix gives the internal auditor exactly that one read-only dashboard key —
nothing more — and adds a self-checking test so this specific gap can never come back unnoticed.

## Traceability ("source says X, code does X, test proves it")
- **Source says X:** `docs/source/auth-permissions.md` §19.1 defines `management_readonly` as the
  dashboard/summary access scope, and assumption A-023 records the mapping
  "Compliance Team Member / Company Secretary / **Internal Auditor** -> compliance".
- **Code does X:** `sfpcl_credit/identity/catalogue.py` now grants `management_readonly` to
  `internal_auditor`; `dashboard.services._ROLE_CONTEXTS` (unchanged) maps it to `compliance` and
  `user_can_read_dashboard` gates on `management_readonly`.
- **Test Y proves it:**
  - `test_dashboard_api.py::test_seeded_internal_auditor_receives_compliance_shell` — seeds the real
    catalogue, logs in a real internal auditor, asserts `200` and `role_context == "compliance"`
    (red before the fix: `403 != 200`; green after).
  - `test_catalogue_seed.py::test_every_dashboard_context_role_can_read_dashboard` — asserts every
    role in `_ROLE_CONTEXTS` holds `management_readonly` after `seed_catalogue()` (the invariant 003G
    missed).
  - `test_catalogue_seed.py::test_management_readonly_dashboard_scope_is_seeded_for_dashboard_roles` —
    `internal_auditor` added to the explicit dashboard-role set.

## Contract impact
None. `GET /api/v1/dashboard/` response contract (`role_context`, `cards[]`, `tasks[]`) is unchanged;
the fix is a seed grant, so `docs/working/API_CONTRACTS.md` needs no update (slice §API Contracts).

## Gate results
- Backend `manage.py check`: no issues.
- Backend tests: 172 passed.
- `makemigrations --check`: no changes (no schema/migration).
- Backend coverage: 96% (floor 85%).
- Frontend typecheck / lint / vitest (26) / build: all pass.
- Protected-path scan: clean. Diff: 5 files, no new deps.

## Red/green evidence
`evidence/terminal-logs/backend-tests-red.log` (3 failing), `backend-tests-green.log` (3 passing).

## Recommended Next Action
Proceed to `003H-dashboard-task-ui-wiring` (its dependency 003G2 is now satisfied).
