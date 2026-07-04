# Risk Assessment — 003A Audit Log Foundation (repair)

Risk level: **Medium** (per slice; standing approval covers autonomous execution).

## Why Medium
- Read-only endpoint over an existing model; no schema change, no migration, no writes.
- Exposes audit data, which is compliance-sensitive, so access must be permission-gated
  and the read must not mutate or fabricate audit rows.

## What changed
- NEW `sfpcl_credit/identity/modules/audit_log.py` — audit-query service boundary
  (permission check, §42.1 serializer, filter validation, newest-first pagination).
- NEW `sfpcl_credit/identity/audit_views.py` — thin `require_GET` view.
- EDIT `sfpcl_credit/config/urls.py` — registered `api/v1/audit-logs/`.
- NEW `sfpcl_credit/tests/test_audit_logs_api.py` — 12 tests (TDD).
- Docs: `docs/working/API_CONTRACTS.md`, `docs/working/ASSUMPTIONS.md` (A-017),
  slice status, HANDOFF, progress, state.

## Risk controls in place
- **Access control**: gated by the existing canonical `audit.audit_log.read` permission
  (002C catalogue). No new permission invented; `reports.audit.read` not used. Tested:
  401 (no token), 401 (malformed bearer), 403 (authenticated without the permission),
  200 (auditor with the permission).
- **Append-only / no read-auditing**: the endpoint is read-only; a dedicated test asserts
  a GET creates zero new `AuditLog` rows. No update/delete route added.
- **No data fabrication**: system/no-actor rows (`actor_user=None`) serialize as
  `actor: null`; test-verified.
- **Input validation**: invalid UUID filters and unknown query parameters return
  `400 VALIDATION_ERROR` with `field_errors`; test-verified.
- **002K2 protected role untouched**: no change to `local_demo_tracer_user`; the test
  fixture creates a fresh `internal_auditor` role and does not reuse the demo tracer role.
- **Protected paths**: no protected/forbidden file touched (only `sfpcl_credit/**`,
  `docs/working/**`, `docs/slices/**`, `.ralph/runs|state|progress`).

## Regression surface
- `config/urls.py` gained one route; existing routes unchanged. Full backend suite
  (120 tests) and frontend suite (26 tests) both green; coverage 96% (floor 85).

## What fixed the previous failure
The prior claude attempt (`2026-07-04_202151_normal_run`) wrote the module + tests but
never wired a view or URL (every endpoint test hit 404) and left this file as the
template. This run completes the view + URL wiring, makes all 12 tests pass, and fills
every required artifact.

## Residual risk
Low. Follow-up A-017 records boring defaults (ordering tiebreak, page-size bounds,
unknown-param strictness) for source-doc confirmation. A future architecture-review or
data-model slice may add a composite `(entity_type, entity_id, -created_at)` index if
audit volume warrants it; not required now (existing single-column indexes on
`entity_type`, `entity_id`, `actor_user`, `created_at` already exist).

Manual review required: no (gates + tests cover the behavior).
