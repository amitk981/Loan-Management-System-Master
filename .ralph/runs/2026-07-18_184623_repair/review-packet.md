# Review Packet: 2026-07-18_184623_repair

## Result
Repair complete pending independent validation

## Slice
009H7-communications-dispatcher-interface-and-idempotency-closure

## Demonstrated Failure and Root Cause

The independent 1,191-test coverage run failed only
`NotificationApiTests.test_send_communication_creates_staff_notification_for_user_recipient`:
HTTP 400 was returned instead of the test's expected 200. The retained test predated H7's explicit
duplicate-identity contract and posted to `/api/v1/communications/send/` without an
`Idempotency-Key`. The endpoint correctly rejected it before writes.

## Repair Review

- Repair delta: one test request now sends the stable key
  `notification-user-recipient-send`.
- Production dispatcher, view, service, model, migration, and adapter code are unchanged by this
  repair.
- The exact test failed before the repair and passed after it with all original notification
  assertions intact.
- All 14 tests in `test_notifications_api` and `test_communications_api` pass, covering the
  repaired integration seam and H7's generic missing/exact/changed/reused-key contract.
- Django check, migration sync, compilation, diff whitespace, protected-path, and debug-marker
  audits pass locally. Complete coverage is intentionally delegated to the orchestrator.

## Traceability

Source integrations §21.1 requires explicit idempotency identity. H7 implements that by rejecting
a missing generic-send key before writes. The repaired retained test now behaves as a valid caller
instead of weakening the endpoint, verified by the RED/GREEN exact-test logs and focused API log in
`evidence/terminal-logs/`.

## Next Slice Readiness

`009H8` and `009I2` were re-read. Both remain concrete, dependency-correct Not Started slices with
fields, runtime/browser contracts, failure cases, and role/current-truth rules; changing them in
this narrow repair would invent no additional useful requirement.

## Recommended Next Action
Run full independent repair validation. If green, let the orchestrator commit and proceed to
`009H8`, then `009I2`.
