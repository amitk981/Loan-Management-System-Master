# Trusted Browser Acceptance

- Exact spec: `e2e/portal-kyc-correction.e2e.spec.ts`
- Declared output: `portal-kyc-correction-decision.png`
- Viewport: 390 × 844
- Acceptance behaviors: borrower-safe approved decision; evidence upload followed by own-scope
  submission; no internal review notes or full proposed PAN rendered.

The localhost backend and frontend reached readiness on both agent attempts. Chrome then closed
during `browserType.launch` before a page existed on both attempts. See
`terminal-logs/browser-portal-kyc-run-1.log` and `terminal-logs/browser-portal-kyc-run-2.log`.
The preflight browser probe had passed. No screenshot was created or fabricated; trusted independent
validation must run the exact spec twice and retain the genuine declared PNG.
