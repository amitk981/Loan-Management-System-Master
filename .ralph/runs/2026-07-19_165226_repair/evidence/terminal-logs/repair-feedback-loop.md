# Repair Feedback Loop

## Authoritative red signal

The retained independent command was:

`RALPH_EVIDENCE_DIR=<run-1> E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npm run e2e -- e2e/epic-009-staff-disbursement-closure.e2e.spec.ts`

Run `2026-07-19_164219_repair` reached the real CFC authorisation endpoint, received HTTP 200, then
received an empty real CFC workspace and timed out waiting for `Action recorded successfully.`.
This is the exact CR-012 red-capable browser symptom.

## Minimized cause

`PaymentAuthorisationHub` renders action messages inside the selected-row branch. The real CFC
workspace is pending-only; once authorisation succeeds, the row correctly leaves CFC scope and the
truthful visible state is `No payment authorisations in your scope`. The nested success alert cannot
render after that terminal refresh.

The same pending-only selector proved the approved row could not supply the next transfer form to
the CFC actor. A focused guarded-fixture regression was made red by requiring the existing Senior
Finance transfer permission and synthetic evidence ownership. The red output is retained in
`backend-transfer-actor-red.log`.

## Repair and green signal

- The browser awaits the genuine authorisation POST, asserts `approved / pending / record_bank_transfer`,
  and then asserts the visible empty CFC queue.
- Credit Manager, Senior Finance, and CFC each authenticate through the real staff login form.
- The guarded fixture gives its initiating Senior Finance actor the existing transfer-success
  permission and synthetic evidence; no production permission catalogue changes.
- The browser awaits the genuine transfer POST and asserts `successful / active` before the final
  transfer/advice state capture.
- `backend-transfer-actor-green.log` retains the one-test green result, and
  `frontend-focused-final.log` retains the five-test component green result.

## Local browser limitation

The exact local Playwright attempt started real Django/Vite setup but the coding sandbox closed
Chrome during `browserType.launch`, before the test body. This is retained in
`local-red-browser.log`; no screenshots were fabricated. Playwright collection and static boundary
checks pass. Ralph's two trusted outside-sandbox executions remain the authoritative original-flow
green signal.
