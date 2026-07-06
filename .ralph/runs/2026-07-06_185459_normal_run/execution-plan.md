# Execution Plan

Selected slice: 003IA2-notification-mark-read-stale-write-hardening

## Scope
- Harden `POST /api/v1/notifications/{notification_id}/mark-read/` only.
- Preserve current notification list/mark-read API shape, recipient scoping, permission behavior, and audit action names.
- No frontend changes expected and no schema change expected.

## Source and Contract Trace
- `docs/source/screen-spec.md` S04 requires notification read/unread state and mark-as-read actions.
- `docs/working/API_CONTRACTS.md` says mark-read requires `read_state_version`, returns `409 STALE_WRITE` on persisted version mismatch, and writes one `communications.notification.marked_read` audit row only for a successful transition.
- `docs/working/REVIEW_FINDINGS.md` identifies the defect: the service checks the submitted version on an unlocked model instance before the transactional save/audit block.

## Implementation Steps
1. Add a failing-first backend regression in `sfpcl_credit/tests/test_notifications_api.py` that simulates a same-version retry racing against an already-persisted successful mark-read, proving the stale attempt returns `409`, leaves version/read metadata unchanged, and creates no second audit row.
2. Move the scoped notification lookup, version comparison, read-state mutation, and audit write into one `transaction.atomic()` block in `sfpcl_credit/communications/services.py`, using `select_for_update()` on the existing current-user recipient queryset.
3. Re-run the targeted notification tests to capture green evidence, then run full Ralph gates and save logs under `.ralph/runs/2026-07-06_185459_normal_run/evidence/terminal-logs/`.
4. Update run artifacts, state/progress/handoff, slice status, changed-files, risk assessment, review packet, and final summary.
5. Sharpen the next 1-2 `Not Started` slice files using only already-opened source/digest context.
