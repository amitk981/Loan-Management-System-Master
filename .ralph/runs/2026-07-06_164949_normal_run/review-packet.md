# Review Packet: 2026-07-06_164949_normal_run

## Result
Success

## Slice
003IA-notifications-center-ui-wiring

## Summary
- Added `Notification` persistence and migration `communications.0003_notification`.
- Added `GET /api/v1/notifications/` and
  `POST /api/v1/notifications/{notification_id}/mark-read/`.
- Current-user notification reads are scoped to direct user, active role, and active team recipients.
- Mark-read persists/audits read state and rejects stale writes with `409 STALE_WRITE`.
- `communications/send` now creates staff inbox rows for direct backend-user recipients.
- Staff `NotificationsCenter` uses the backend notification API; no mock notification derivation
  remains on that screen.
- Staff `MyProfile` is read-only from current backend user data loaded by `/api/v1/auth/me/`.

## Traceability
- Source says S04 centralises system alerts, borrower communications, internal notifications, and
  compliance reminders with title, linked record, severity, timestamp, sender/recipient, read/unread,
  and action button fields (`screen-spec.md` S04). Code returns those fields from
  `/api/v1/notifications/`; verified by `test_notifications_api.py`.
- Source says notification channels include in-app notifications (`screen-spec.md` §5.8). Code adds
  a persisted current-user inbox distinct from generic communication history; verified by list and
  send-to-user tests.
- Source API contracts use standard pagination (§8.1). Code returns standard top-level pagination
  on notification list; verified by `assert_pagination_shape`.
- Source §43 dashboard remains role summary/tasks. Code keeps dashboard separate from notifications;
  `003J` was sharpened to preserve that separation.
- Source/current auth contract from 002D exposes `/api/v1/auth/me/`. `MyProfile` renders backend
  current-user identity, role/team codes, status, mobile, email, permissions, and actions; verified by
  `MyProfile.test.tsx`.

## Tests And Gates
- Backend red/green: `notifications-red.log`, `notifications-green.log`.
- Frontend red/green: `frontend-notifications-profile-red.log`,
  `frontend-notifications-profile-green.log`.
- Backend full tests: 183/183 passing.
- Backend coverage: 96%, floor 85.
- Frontend tests: 46/46 passing.
- Typecheck, lint, build, migration check, diff check, and protected-path scan passed.

## Visual Evidence
Live screenshots were blocked by sandbox permissions:
- Django localhost bind failed with `Operation not permitted`.
- Playwright Chromium launch failed with Mach port `Permission denied`.
- Quick Look render failed under sandbox initialization.

A static visual evidence HTML artifact is saved at
`evidence/screenshots/003ia-visual-evidence.html`; logs are in
`evidence/terminal-logs/visual-evidence-render.log`.

## Recommended Next Action
Run architecture review by cadence, then continue to the sharpened `003J` slice if review passes.
