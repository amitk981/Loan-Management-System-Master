# Risk Assessment — 003G2 Dashboard Internal Auditor Access Regression

Risk level: **Medium** (matches slice). Backend RBAC seed data change; no schema, no migration, no
financial logic, no frontend.

## What changed
Added one permission grant: `management_readonly` to the `internal_auditor` role in the canonical
catalogue seed (`sfpcl_credit/identity/catalogue.ROLE_PERMISSIONS`). Two regression tests added.

## Why it is safe
- **Blast radius is one role.** Only `internal_auditor` gains a permission; no other role, endpoint,
  or model is altered. The permission granted (`management_readonly`) is a read-only dashboard/summary
  scope that writes no audit rows and exposes only zero-count shell cards.
- **Source-backed, not invented.** A-023 and `auth-permissions.md` §19.1 already document
  `internal_auditor -> compliance` and `management_readonly` as the dashboard scope. This grant
  realises the documented mapping; it does not create a new business rule.
- **No privilege escalation of concern.** The internal auditor is a read-only audit/compliance role;
  granting read access to a zero-count dashboard shell is strictly narrower than the audit-log,
  report, and compliance-read permissions it already holds.
- **Idempotent seed.** `seed_catalogue()` uses `get_or_create`; rerunning does not duplicate links.
- **Guardrails.** No protected/forbidden files touched (scan clean). Diff is 5 files / well under the
  30-file, 2000-line limits. No new dependencies. No migrations (`makemigrations --check` = no changes).

## Regression coverage added
- `test_dashboard_api::test_seeded_internal_auditor_receives_compliance_shell` — end-to-end proof a
  seeded internal auditor now gets `200` + `role_context: "compliance"` (was `403`).
- `test_catalogue_seed::test_every_dashboard_context_role_can_read_dashboard` — invariant tying the
  seed to `dashboard.services._ROLE_CONTEXTS` so any future role added to the mapping without the
  permission fails the build.

## Residual risk
None material. If source docs later define a narrower dashboard permission code, A-023's revisit note
already owns replacing `management_readonly`.
