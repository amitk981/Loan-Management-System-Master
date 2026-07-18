# Execution Plan

Selected slice: 009H7-communications-dispatcher-interface-and-idempotency-closure

## Demonstrated failure

Independent complete coverage failed only
`NotificationApiTests.test_send_communication_creates_staff_notification_for_user_recipient`:
the retained test posts to the generic communications send endpoint without the explicit
`Idempotency-Key` required by this slice and therefore receives the expected contract response
HTTP 400 instead of its stale HTTP 200 expectation.

## Repair steps

1. Reproduce the exact failure with the mandated backend interpreter and save the output as RED
   evidence.
2. Confirm the endpoint accepts the same request with a bounded explicit idempotency key and that
   the test's staff-notification assertions still exercise the intended integration behavior.
3. Fix only the demonstrated compatibility gap by updating the retained notification API test to
   send an explicit stable key; do not weaken the production requirement or alter dispatcher code.
4. Re-run the exact failing test, the focused notification API class, and the slice's generic
   communications/idempotency API tests; save GREEN evidence.
5. Run Django check, migration sync, and focused compilation. Do not rerun complete backend
   coverage; the orchestrator performs authoritative full revalidation.
6. Audit the final diff and protected paths, then complete this repair run's changed-files, risk,
   review, evidence, and final-summary artifacts while preserving the already-complete slice state,
   progress, handoff, digest, and next-slice sharpening.
