# Critical UAT Interest-Invoice Conflict Diagnosis

## Authoritative Symptom

The orchestrator-owned trusted browser run launched Chromium, completed the disbursement and
repayment steps, and reached `UAT-014/015/016/017`. The public request
`POST /api/v1/loan-accounts/<id>/interest-invoices/` returned HTTP 409 where the E2E spec expected
HTTP 200.

## Tight Reproduction

The focused public-API test
`CriticalUatE2eSeedTests.test_seed_is_idempotent_and_builds_only_public_journey_preconditions`
uses the same declared Epic 009 and critical-UAT seeds, completes the public repayment action, logs
in as the source Accounts actor, and posts the FY2026-27 invoice request.

Before the repair it deterministically returned:

> One approved interest invoice configuration is required.

Evidence: `terminal-logs/critical-interest-precondition-red.log`.

## Ranked Hypotheses and Outcome

1. Missing seeded FY2026-27 invoice configuration/rate coverage — confirmed. The critical seed
   created neither and the service rejected the request before invoice ownership evaluation.
2. Wrong source actor — confirmed in the E2E spec. It remained logged in as Credit Manager even
   though the source UAT role for interest is Accounts.
3. Duplicate invoice or idempotency collision — disproved. Playwright removes the isolated
   database before seeding and no seed created an invoice.
4. Loan-period ineligibility — disproved by the active funded account and positive outstanding
   balance exercised by the focused public test.

## Repair

- The guarded local critical-UAT seed now creates exactly one immutable FY2026-27 invoice
  calculation configuration and one canonically activated, gap-free approved rate.
- A deterministic System Administrator checker activates the proposed rate through the real
  configuration owner and has only the additional communication authority that activation
  requires in the isolated E2E database.
- The Playwright scenario switches to the seeded Accounts actor for invoice generation, then back
  to Credit Manager for DPD/default actions.
- No production endpoint, permission rule, financial algorithm, model, migration, or live provider
  behavior changed.

## Verification

- RED: `terminal-logs/critical-interest-precondition-red.log` — 409 with the exact configuration
  conflict.
- GREEN: `terminal-logs/critical-interest-precondition-green.log` — focused public behavior passes.
- Focused regression: `terminal-logs/backend-focused-green.log` — 6 tests pass.
- Django/migrations: `terminal-logs/backend-check-migrations-green.log`.
- Frontend seed selection: `terminal-logs/frontend-seed-focused-green.log` — 5 tests pass.
- TypeScript, ESLint, build: `terminal-logs/frontend-typecheck-green.log`,
  `frontend-lint-green.log`, and `frontend-build-green.log`.
- Spec collection: `terminal-logs/critical-uat-spec-collection-green.log` — 1 declared test.

## Browser Infrastructure Evidence

Two unchanged post-fix exact browser reruns are retained in
`terminal-logs/trusted-browser-acceptance-green.log` and
`terminal-logs/trusted-browser-acceptance-green-2.log`. Both ended during `browserType.launch`
before a page, request, or application assertion existed. No screenshots were fabricated.
Independent trusted validation must rerun the declared spec and produce both required screenshots.
