# Review Packet: 2026-07-04_202830_repair

## Result
Success (repair of 003A-audit-log-foundation)

## Slice
003A-audit-log-foundation — expose the existing append-only `identity.AuditLog` through a
protected, paginated, read-only `GET /api/v1/audit-logs/` endpoint.

## Diagnosis of the previous failure (repair mode)
- `2026-07-04_202030_normal_run` (codex): usage-limit exhausted before any code.
- `2026-07-04_202151_normal_run` (claude): wrote `identity/modules/audit_log.py` and the
  test file but **never wired a view or URL** — every endpoint test returned 404
  (`FAILED (failures=12, errors=1)`) — and left `risk-assessment.md` as the template, so
  the artifact-quality gate also failed. This run implements the missing view + URL and
  fills all artifacts.

## Traceability (for a non-developer)
- **The source doc says**: `docs/source/api-contracts.md` §42.1 defines
  `GET /api/v1/audit-logs/?entity_type=…&entity_id=…` returning items with
  `audit_log_id`, `actor{user_id, full_name}`, `actor_type`, `action`, `entity_type`,
  `entity_id`, `old_value`, `new_value`, `ip_address`, `created_at`.
- **The code does that**: `identity/modules/audit_log.py::serialize_audit_log` produces
  exactly those fields (mapping the stored `old_value_json`/`new_value_json` to
  `old_value`/`new_value`, and `actor: null` for system rows), served newest-first with the
  standard top-level `pagination` envelope by `audit_views.py::audit_log_list`.
- **Verified by tests**: `tests/test_audit_logs_api.py` —
  `test_authorized_list_returns_item_shape_and_pagination_newest_first` (exact field set +
  ordering), `test_system_row_without_actor_serializes_actor_null` (actor null path),
  filter tests, and the validation/permission tests below. Evidence:
  `evidence/audit-logs-api-response.txt` shows a real 200 and a real 400.
- **Permission rule**: slice requires the existing `audit.audit_log.read` (002C catalogue).
  Code checks it via `auth_service.effective_permission_codes`; no new permission invented.
  Verified by `test_user_without_audit_permission_is_forbidden` (403) and the positive
  auditor path.
- **Append-only**: no write/update/delete route; `test_reading_audit_logs_creates_no_new_audit_row`
  asserts a GET adds zero `AuditLog` rows.

## Gate results
- Backend `manage.py check`: no issues.
- Backend `makemigrations --check --dry-run`: No changes detected (no schema change).
- Backend tests: 120/120 passed; coverage 96% (floor 85); new module 98%, new view 93%.
- Frontend `npm run typecheck`, `npm run lint`, `npm test` (26/26), `npm run build`: all green.
- Protected-paths: none touched.
- Diff limits: 7 files, well within limits; 0 new dependencies; 0 migrations.

## Files changed
- NEW `sfpcl_credit/identity/modules/audit_log.py`
- NEW `sfpcl_credit/identity/audit_views.py`
- EDIT `sfpcl_credit/config/urls.py`
- NEW `sfpcl_credit/tests/test_audit_logs_api.py`
- EDIT `docs/working/API_CONTRACTS.md`, `docs/working/ASSUMPTIONS.md` (A-017),
  `docs/slices/003A-audit-log-foundation.md`, `docs/working/HANDOFF.md`, `.ralph/progress.md`,
  `.ralph/state.json`

## Reviewer note (duplication)
The thin bearer-session auth helper `_authenticate_session` now appears in three view
modules (`views.py` `_bearer_access_token`, `admin_views.py`, `audit_views.py`). Kept local
here to minimize repair blast radius; a future small refactor slice could extract one shared
HTTP auth helper. Flagged for architecture review, not blocking.

## Recommended Next Action
Merge; then run `003B-workflow-event-foundation` (mirror this module/view pattern; heed the
digest warning about the existing tracer `workflow_events` table).
