# Execution Plan — 003G2 Dashboard Internal Auditor Access Regression

## Slice
`003G2-dashboard-internal-auditor-access-regression` (Medium risk, backend/API only, no frontend).

## Defect being fixed
`sfpcl_credit/dashboard/services._ROLE_CONTEXTS` maps `internal_auditor -> "compliance"`, promising
the internal auditor a compliance dashboard shell. But `identity/catalogue.ROLE_PERMISSIONS`
grants `internal_auditor` audit/report/compliance-read permissions and **omits**
`management_readonly`. `dashboard_summary` gates on `management_readonly`
(`user_can_read_dashboard`), so a seeded `internal_auditor` hitting `GET /api/v1/dashboard/`
receives `403 PERMISSION_DENIED` instead of the documented `role_context: "compliance"` shell.

## Source-backed decision
A-023 (`docs/working/ASSUMPTIONS.md`) and the epic-003 digest already document the mapping
"Compliance Team Member / Company Secretary / **Internal Auditor** -> compliance" and state that the
catalogue seeds `management_readonly` for the dashboard role contexts. `auth-permissions.md` §19.1
defines `management_readonly` as the dashboard/summary access scope. So the fix is a **seed grant**:
add `management_readonly` to `internal_auditor` in `ROLE_PERMISSIONS`. The 003G role-context mapping
and API contract stay unchanged (slice §3 first option; A-023 needs no revision, only its scope is
now fully realised).

## TDD steps (backend, red first)
1. **Red — dashboard API regression** (`sfpcl_credit/tests/test_dashboard_api.py`):
   add a test that runs the real `seed_catalogue()`, creates a user whose `primary_role` is the
   seeded `internal_auditor` role, logs in, and asserts `GET /api/v1/dashboard/` returns `200` with
   `data.role_context == "compliance"`. Fails today with `403`.
2. **Red — catalogue consistency regression** (`sfpcl_credit/tests/test_catalogue_seed.py`):
   add a test that imports `_ROLE_CONTEXTS` from `dashboard.services` and asserts every role named
   there has `management_readonly` after `seed_catalogue()`. Also add `internal_auditor` to the
   existing explicit dashboard-role set in
   `test_management_readonly_dashboard_scope_is_seeded_for_dashboard_roles`. Fails today for
   `internal_auditor`.
3. Save red output to `evidence/terminal-logs/backend-tests-red.log`.
4. **Green — implement**: add `"management_readonly"` to the `internal_auditor` list in
   `identity/catalogue.ROLE_PERMISSIONS`. Update the module comment noting the dashboard scope now
   covers all `_ROLE_CONTEXTS` roles.
5. Save green output to `evidence/terminal-logs/backend-tests-green.log`.

## Non-goals (per slice §5)
No dashboard calculations, no specialist dashboard endpoints, no task persistence, no frontend
wiring, no new permission codes, no schema change (seed data only, so no migration).

## Gates
Backend: `manage.py check`, full test suite, `makemigrations --check`, coverage (floor 85%).
Frontend: build, typecheck, lint, vitest (unchanged; run to prove no regression). Protected-path
scan. Evidence saved under the run folder.

## Docs to touch
- `docs/working/ASSUMPTIONS.md` A-023: note internal_auditor grant now realised (minor clarification,
  no decision reversal).
- `docs/working/digests/epic-003-audit-documents-config.md`: append 003G2 note.
- `docs/working/HANDOFF.md`, `.ralph/progress.md`, `.ralph/state.json`, slice status.
- `docs/working/API_CONTRACTS.md`: unchanged (contract is stable; fix is a seed grant).
