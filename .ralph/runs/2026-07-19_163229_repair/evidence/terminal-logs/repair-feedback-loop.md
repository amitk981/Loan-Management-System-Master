# Repair Feedback Loop

## Authoritative red signal

The previous independent trusted-browser command was:

`RALPH_EVIDENCE_DIR=<run-1> E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npm run e2e -- e2e/epic-009-staff-disbursement-closure.e2e.spec.ts`

It reached the real initiation boundary. Django logged HTTP 200 for the initiation POST and HTTP 200
for the following workspace GET, then Playwright timed out for five seconds waiting for
`Payment initiation recorded successfully.` This is the exact, deterministic red-capable signal.

## Minimized cause

`DisbursementHub.runAction` refreshes owner-backed workspace rows before setting its success message.
The message is rendered only inside `primaryAction`'s card. Successful initiation consumes the
`initiate_disbursement` action, so the refreshed UI can remove that card before its nested message is
visible. The mutation succeeded; the evidence assertion targeted a transient element that cannot
survive the successful state transition.

Ranked alternatives were an idempotent replay message, a later reload clearing the message, or the
row leaving finance scope. The captured 200 POST/GET and the action-card render boundary distinguish
the first hypothesis from these alternatives.

## Repair and green-capable contract

The declared Playwright spec now:

1. waits for the genuine Django initiation POST response;
2. asserts the API envelope contains `success: true`, `initiation_status: initiated`,
   `authorisation_status: pending`, and `bank_transfer_status: pending`;
3. waits for the consumed `Initiate payment` action to disappear; and
4. asserts the refreshed visible `Pending` state before changing actors.

The exact spec collects successfully. A local execution started Django and Vite, but macOS Chrome
closed during `browserType.launch` after 4 ms, before the test body. Per the slice contract this is
an infrastructure limitation, not a browser-contract verdict; the orchestrator's two trusted runs
are the authoritative green execution.
