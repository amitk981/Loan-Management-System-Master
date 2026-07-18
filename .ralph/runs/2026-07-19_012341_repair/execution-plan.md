# Execution Plan

## Repair boundary

Repair only the trusted-browser failure recorded in
`.ralph/runs/2026-07-19_011304_repair/failure-summary.md`. Preserve the existing uncommitted 009I2
implementation and do not revisit passing backend, frontend, or documentation work.

## Diagnosis and feedback loop

- Red-capable command: run the declared Playwright spec with real Django and the run evidence
  directory. The prior independent run deterministically timed out in all three tests while looking
  for a borrower navigation button named `Disbursement Status`.
- Minimal cause: the approved borrower sidebar exposes that destination as `Disbursement`; the MP14
  page heading is `Disbursement Status`. The spec confused the page title with the navigation label.
- Prediction: changing only the three sidebar locators to the existing accessible name
  `Disbursement` lets each test reach its exact status-route seam and its MP14 assertions.

## Implementation

1. Update only the stale navigation accessible name in
   `sfpcl-lms/e2e/portal-disbursement-status.spec.ts`.
2. Run Playwright collection and the focused spec when Chromium is available. If the coding
   sandbox blocks Chromium launch, retain the exact launch output and rely on Ralph's external
   twice-run browser gate as required by the slice contract.
3. Run focused frontend tests plus typecheck, lint, and build because the repair touches only the
   browser contract.
4. Save diagnosis, verification, risk assessment, review packet, and final summary in this run
   folder. Do not fabricate screenshots; the independent browser validator owns them.
