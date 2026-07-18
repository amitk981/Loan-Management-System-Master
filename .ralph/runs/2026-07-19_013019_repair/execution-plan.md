# Execution Plan

## Repair boundary

Repair only the trusted-browser safe-error failure recorded in
`.ralph/runs/2026-07-19_012341_repair/failure-summary.md` and its retained browser log. Preserve the
current uncommitted 009I2 implementation, including the two passing browser scenarios, and do not
revisit passing backend, frontend, documentation, or migration work.

## Tight feedback loop

- Minimal red-capable command: run only `MP14 renders a safe unavailable state for an exact status
  failure` from `e2e/portal-disbursement-status.spec.ts` with the required real-Django interpreter
  and a run-local screenshot directory.
- Exact retained symptom: the real-login/selection flow reaches MP14, but the expected borrower-safe
  text `Disbursement status could not be loaded. Please try again.` is absent after the exact status
  endpoint returns HTTP 503. The first two cases pass; only `mp14-safe-error.png` is missing.
- Ranked probes: compare expected and rendered error copy; prove the exact route handler receives the
  selected application GET; prove selected application state survives navigation; inspect shared API
  error classification only if those earlier probes do not explain the failure.

## Implementation and verification

1. Reproduce the isolated third case and retain its output. If Chromium is unavailable inside the
   coding sandbox, use the retained independent run as the red proof and add the narrowest
   non-browser regression seam that catches the same mismatch.
2. Change only the demonstrated browser-contract defect. Do not change production copy or behavior
   unless the existing frontend contract itself contradicts the slice requirement.
3. Re-run the isolated case, then the full declared Playwright spec when Chromium is available. Run
   the focused MP14/frontend tests, typecheck, lint, and build in proportion to the changed surface.
4. Save diagnosis and red/green evidence under this run's `evidence/terminal-logs/`, then complete
   `risk-assessment.md`, `review-packet.md`, and `final-summary.md`. Do not fabricate screenshots;
   Ralph's independent gate must still execute the declared browser contract twice.
