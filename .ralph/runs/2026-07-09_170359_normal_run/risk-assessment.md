# Risk Assessment

Selected slice: `004K2-borrower-360-bank-holder-contract-hardening`

Risk level: Medium

## Why Medium
- This was a frontend contract-hardening slice on a staff-facing Borrower 360 screen.
- It changed the frontend DTO boundary for bank-account metadata, which is user-visible but narrow.
- No backend behavior, database schema, permissions, audit behavior, or API contract rename changed.

## Sensitive Data Risk
- Bank account numbers remain normalized to masked/last-four metadata only.
- Tests assert that full account numbers are not present in normalized account or cancelled-cheque
  payloads.
- Borrower 360 still has no bank-account reveal affordance.

## Scope Controls
- Preserved the 004J/backend canonical response field `account_holder_name`.
- Removed the frontend dependency on the old `holder_name` alias.
- Did not add duplicate-active-borrower warnings, signature-mismatch workflows, payment initiation,
  disbursement-readiness UI, or bank-account full-number reveal behavior.

## Residual Risk
- Visual PNG capture could not be completed because local Chromium launch is blocked by macOS
  sandbox Mach port permissions, and the in-app browser backend was unavailable. A self-contained
  visual HTML artifact is saved instead.
- The implementation relies on the existing test fixture path for visual/contract rendering; full
  live browser verification should be picked up by orchestrator/browser environments that can launch
  Chromium.

Manual review required: normal Ralph/orchestrator review only.
