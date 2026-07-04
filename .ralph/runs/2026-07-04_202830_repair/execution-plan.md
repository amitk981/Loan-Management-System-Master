# Execution Plan — 003A Audit Log Foundation (repair)

Selected slice: `003A-audit-log-foundation`
Mode: repair
Risk: Medium (standing approval; read-only API over existing model, no schema change)

## Diagnosis of the previous failure
Two prior attempts on 003A failed:
- `2026-07-04_202030_normal_run` (codex): stopped early — usage/rate limit exhausted
  (`agent-limit-exhausted.md`), no product code written.
- `2026-07-04_202151_normal_run` (claude): wrote the service module
  `sfpcl_credit/identity/modules/audit_log.py` and the test file
  `sfpcl_credit/tests/test_audit_logs_api.py`, but **never wired the endpoint** — no
  view and no URL registration. Every endpoint test hit `404` (`Ran 122 tests …
  FAILED (failures=12, errors=1)`). It also left `risk-assessment.md` as the unfilled
  template, so the artifact-quality gate failed.

My worktree is a clean slate (none of those files are present here). I implement fresh,
completing the full path (module + view + URL + tests + docs) and filling all artifacts.

## Goal
Expose the existing append-only `identity.AuditLog` records through a protected,
paginated, read-only `GET /api/v1/audit-logs/` endpoint following `api-contracts.md`
§42.1 item shape, §6-8 envelope/pagination, and §7 error codes, gated by the existing
`audit.audit_log.read` permission (002C catalogue).

## Constraints honored
- No new audit table; reuse `identity.AuditLog` (models unchanged → no migration).
- No update/delete endpoints; append-only preserved; the read creates no audit row.
- Serialization/filtering behind a small module interface
  (`identity/modules/audit_log.py`), matching the 002C2 service-boundary pattern.
- Do not invent permissions (`reports.audit.read` forbidden). Do not touch the
  002K2 `local_demo_tracer_user` role.
- Reuse envelope helpers (`sfpcl_credit/api.py`) and the 002J contract harness
  (`tests/api_contracts.py`).

## Files
- NEW `sfpcl_credit/identity/modules/audit_log.py` — service boundary:
  `AUDIT_READ_PERMISSION`, `user_can_read_audit_logs`, `serialize_audit_log`
  (maps `old_value_json`/`new_value_json` -> `old_value`/`new_value`; `actor: null`
  when `actor_user` is None), `paginated_audit_logs` (parse+validate query params,
  reject unknown params, invalid-UUID -> `ValidationError`, newest-first, top-level
  pagination), and `validation_field_errors`.
- NEW `sfpcl_credit/identity/audit_views.py` — thin `require_GET` view: bearer session
  auth (401 `AUTH_REQUIRED`/`INVALID_TOKEN`), permission gate (403 `PERMISSION_DENIED`),
  query validation (400 `VALIDATION_ERROR` with `field_errors`), success via
  `list_response`.
- EDIT `sfpcl_credit/config/urls.py` — register `api/v1/audit-logs/`.
- NEW `sfpcl_credit/tests/test_audit_logs_api.py` — TDD, using the 002J harness.
- EDIT `docs/working/API_CONTRACTS.md` — document the endpoint contract.

## TDD order
1. Write `tests/test_audit_logs_api.py`; run -> RED (endpoint 404 / missing).
   Save red log to `evidence/terminal-logs/backend-red.txt`.
2. Implement module + view + URL until GREEN. Save green log + coverage.
3. Full backend suite, `manage.py check`, `makemigrations --check`, coverage floor 85.
4. Frontend gates (unchanged) run to confirm no regression.

## Test cases (from slice)
- Unauthenticated -> 401 `AUTH_REQUIRED` (harness error envelope).
- Malformed bearer -> 401 `INVALID_TOKEN`.
- Authorized (`internal_auditor` w/ `audit.audit_log.read`) list -> §42.1 fields +
  pagination shape, newest-first.
- `actor_user=None` row -> `actor: null` with actor_type/action/entity_type/entity_id/created_at.
- `entity_type`+`entity_id` filter -> only matching rows.
- `actor_user_id` filter -> only that actor's rows.
- Authenticated without permission -> 403 `PERMISSION_DENIED`.
- Invalid UUID filter -> 400 `VALIDATION_ERROR` with `field_errors`.
- Unknown query param -> 400 `VALIDATION_ERROR`; `page`/`page_size` remain allowed.
- Empty result set -> `success: true`, `data: []`, valid pagination metadata.
- Read creates no new audit row (append-only / no read-auditing).
