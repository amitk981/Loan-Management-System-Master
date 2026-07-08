# Risk Assessment

Selected slice: `003IA2-notification-mark-read-stale-write-hardening`

Mode: `normal_run`

Risk level: Medium

## Why
- This slice changes backend concurrency behavior for a staff notification action endpoint.
- It touches audit semantics: successful unread-to-read transitions must write exactly one
  `communications.notification.marked_read` audit row, while stale retries must write none.
- No schema, permission catalogue, frontend styling, or public API response shape changed.

## Controls
- TDD evidence captured:
  - RED: `evidence/terminal-logs/red-notification-mark-read-stale-retry.log`
  - GREEN: `evidence/terminal-logs/green-notification-mark-read-stale-retry-after-cleanup.log`
- The implementation keeps existing current-user recipient scope and uses `select_for_update()`
  inside `transaction.atomic()` for the mark-read lookup/version check/save/audit operation.
- Existing `401`, `403`, wrong-recipient `404`, validation `400`, and stale `409` notification tests
  remain covered by `sfpcl_credit/tests/test_notifications_api.py`.
- Protected-path scan passed; no protected or source-doc paths were modified.

## Residual Risk
- Local tests use SQLite, where row-lock behavior is less representative than production
  PostgreSQL. The code uses Django's portable `select_for_update()` pattern and the regression
  simulates the stale in-flight object identified by the architecture review.
- No frontend behavior changed, so no visual evidence was required.

Manual review required: standard Ralph/orchestrator review only.
