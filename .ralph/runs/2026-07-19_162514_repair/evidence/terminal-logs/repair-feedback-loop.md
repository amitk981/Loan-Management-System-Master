# Repair Feedback Loop

## Authoritative red signal

Previous repair run command:

`RALPH_EVIDENCE_DIR=<run-1> E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npm run e2e -- e2e/epic-009-staff-disbursement-closure.e2e.spec.ts`

Observed result: Playwright reached the real Django-backed SAP & Disbursement screen after
`--make-ready`, but `Initiate payment` remained disabled for the full 5-second assertion timeout.
The server log showed no workspace GET after the guarded fixture transition.

## Root cause

The guarded fixture command mutates the isolated E2E database outside the browser. The mounted
`DisbursementHub` loads workspace state only when mounted, while clicking the already-selected
navigation item did not remount it. The spec therefore asserted against the earlier blocked row.

## Repair

The spec now reloads the authenticated app after both out-of-browser fixture transitions and
reopens the required screen. This forces a fresh real-Django workspace response without changing
production behavior or intercepting an owned API.

## Local browser attempt

The exact spec was invoked after the repair with the mandated backend interpreter. Django and Vite
started, but macOS Chrome closed during `browserType.launch` before the test body (3 ms). This is the
documented coding-sandbox limitation, not a contract verdict. No screenshots were fabricated; the
orchestrator's two unsandboxed trusted-browser repetitions remain authoritative.
