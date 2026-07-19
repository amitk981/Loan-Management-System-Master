# Repair Feedback Loop

## Authoritative red signal

The retained independent command was:

`RALPH_EVIDENCE_DIR=<run-1> E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npm run e2e -- e2e/epic-009-staff-disbursement-closure.e2e.spec.ts`

In run `2026-07-19_163229_repair`, the genuine Django initiation POST returned HTTP 400 where run
`2026-07-19_162514_repair` had returned HTTP 200. The later CFC, transfer, active-account, and safe
error states therefore never ran. This is the exact red-capable symptom for CR-012.

## Minimized cause

The two retained server logs show two real workspace GETs around the payment form. React development
Strict Mode can start both loads; the spec continued after the first response. The later response
replaced the action descriptor, which retriggered `DisbursementHub`'s form-default effect and could
erase the final-verification comment after Playwright filled it but before the click. The response
ordering explains the alternating HTTP 200 and HTTP 400 outcomes with otherwise identical fixtures.

A focused Django regression constructed the exact payload from the guarded fixture's projected
action descriptor and posted it through the real endpoint. It passed with HTTP 200 and
`initiated / pending / pending`, falsifying readiness, current-owner evidence, idempotency, and actor
authority as the cause.

## Repair

The declared Playwright spec now waits for workspace traffic to settle before using the projected
form, asserts the exact server-projected amount, fills and reasserts the required final-verification
comment, and includes the safe Django envelope in any non-2xx assertion. The guarded backend fixture
test retains the exact projected-action POST as a regression.

## Local browser limitation

The exact local Playwright attempt started the real Django/Vite servers, but the coding sandbox
closed Chrome during `browserType.launch` before the test body. No screenshots were fabricated. The
spec collects successfully; Ralph's two trusted runs outside the coding sandbox remain the
authoritative original-scenario green signal.
