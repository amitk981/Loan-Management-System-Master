# Risk Assessment

Slice: `004K-borrower-360-kyc-panel-and-masking-ui-wiring`

Risk level: Medium

## Risk Drivers
- Frontend now composes several Epic 004 APIs on one screen, so regressions could affect staff
  visibility of member, KYC, land/crop, nominee, shareholding, and bank metadata.
- The slice touches sensitive reveal UI behavior for PAN/Aadhaar and masked bank metadata display.
- Borrower 360 previously contained broad prototype mock data for loans, repayments,
  communications, risk, security, nominee, and audit surfaces.

## Controls Applied
- TDD evidence saved: `borrower360-red.log` then `borrower360-green.log`.
- Added tests that verify 004J bank/cancelled-cheque endpoints are called and normalized as
  masked-only metadata.
- Added view tests that verify Borrower 360 renders API-backed Epic 004 facts, hides unauthorized
  reveal controls, contains no full fake PAN/Aadhaar/bank values, and does not show out-of-scope
  duplicate-bank/payment/disbursement controls.
- Removed `mockData` imports from `Borrower360.tsx` and replaced unimplemented modules with
  explicit empty states.
- Full frontend/backend gates passed, including backend coverage at 96%.

## Residual Risk
- Browser PNG screenshot capture was blocked by sandbox restrictions: first root `npx` attempted
  network and failed, then the installed Playwright Chromium failed to launch due macOS Mach port
  permission denial. Logs are saved in `visual-screenshot-desktop.log`; the self-contained visual
  HTML evidence remains reviewable.
- Borrower 360 loads optional subresources independently. If a subresource fails, the page renders
  the member profile and a warning rather than failing the entire screen. This is a UI resilience
  choice, not a new business rule.
- Real loan/application/repayment/communication/risk/audit records remain deferred until their
  backend APIs exist.

## Protected Paths
No protected files or `docs/source/**` files were modified.
