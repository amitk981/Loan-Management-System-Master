# Execution Plan

Selected slice: 003IA-notifications-center-ui-wiring

## Scope
- Implement a notification-specific backend inbox boundary instead of overloading `communications` history.
- Wire the staff Notifications Center to the new backend API and remove mock notification rows.
- Keep My Profile read-only and backed by the current backend user loaded from `/api/v1/auth/me/`.
- Preserve dashboard task separation.

## Source Trace
- `docs/source/screen-spec.md` §5.8 and S04 require in-app notifications with title, linked record, severity, timestamp, sender/recipient, read/unread, and action controls.
- `docs/source/content-spec.md` S04 defines the Notifications page tabs and fields.
- `docs/source/api-contracts.md` §8.1 sets pagination rules; §39 defines communication APIs; §43 keeps dashboard summary separate.
- `docs/source/information-architecture.md` places Notifications under Administration.

## TDD / Implementation Steps
1. Backend RED: add focused API tests for current-user notification listing, object-level recipient filtering, mark-read persistence/audit, 401/403, invalid query parameters, and stale mark-read handling.
2. Backend GREEN: add `Notification` persistence, service functions, URLs/views, permission catalogue seed, and communication-send notification creation for staff user/role/team recipients.
3. Frontend RED: add tests for the notification API client/view states and My Profile rendering backend current-user data without mock/edit-only fields.
4. Frontend GREEN: add a notification API client, update `NotificationsCenter.tsx` to use it with existing visual patterns, and simplify `MyProfile.tsx` to read-only backend-current-user display.
5. Documentation: update `docs/working/API_CONTRACTS.md`, `docs/working/ASSUMPTIONS.md`, digest, handoff/progress/state/slice status, and Ralph review artifacts.
6. Evidence/gates: save red/green logs, run backend check/tests/migration/coverage, frontend tests/typecheck/lint/build, save visual evidence or explain any screenshot limitation, and capture changed files/risk/review packet.

## Risk Controls
- No real email/SMS/provider delivery.
- No dashboard task mutation or frontend-only notification permission.
- No fabricated borrower financial details in notification rows.
- One schema migration only.
