# Ralph Handoff

## Last Run
2026-07-06_164949_normal_run

## Current Status
Slice `003IA-notifications-center-ui-wiring` completed successfully. Architecture review is now due
by cadence (`slices_completed_since_architecture_review: 4`).

## What Completed
- Added `sfpcl_credit.communications.Notification` with migration `0003_notification`.
- Added protected current-user inbox APIs:
  - `GET /api/v1/notifications/`
  - `POST /api/v1/notifications/{notification_id}/mark-read/`
- List scope covers direct user, active primary role, and active team recipients. Other users' rows
  are excluded; inaccessible mark-read returns `404`.
- Mark-read requires `read_state_version`, returns `409 STALE_WRITE`, persists read state, and
  audits `communications.notification.marked_read`.
- `POST /api/v1/communications/send/` now creates a staff notification when addressed to a backend
  user recipient (`user`, `staff_user`, or `internal_user`).
- Added narrow permission `communications.notification.read`; seeded it to active internal roles
  with existing source-backed permission sets while preserving deliberately permission-neutral
  `it_head` and `sales_team_user`.
- Staff `NotificationsCenter` now uses the backend notification API and no longer derives rows from
  mock applications/loans.
- Staff `MyProfile` is read-only and displays identity, role/team codes, status, mobile, email,
  permissions, and available actions from the current backend user loaded via `/api/v1/auth/me/`.
- Updated contracts/assumptions (A-026), Epic 003 digest, prototype inventory/gap report, and
  sharpened `003J`/`003K`.

## Evidence
See `.ralph/runs/2026-07-06_164949_normal_run/` for plan, changed files, risk/review/final summary,
red/green logs, gate logs, API example, and visual evidence notes. Browser screenshots were blocked
by sandbox localhost/browser/renderer restrictions; exact failures are logged.

## Current Blocker
None for the implemented slice. The next loop should run architecture review before more normal
slices because cadence is due.

## Notes For Next Slice
- `003J` and `003K` were sharpened. `003J` must not merge scheduler jobs with dashboard tasks, S04
  notifications, or communication history.
- Dashboard remains role cards plus `tasks: []`; notifications are under `/api/v1/notifications/`.
- Borrower/member-portal notifications remain out of scope for Epic 003; later member-portal slices
  own that path.
