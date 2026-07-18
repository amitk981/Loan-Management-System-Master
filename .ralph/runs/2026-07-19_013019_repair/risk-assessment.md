# Risk Assessment

Risk level: High (declared by the slice; standing owner approval applies)

- Selected slice: `009I2-portal-disbursement-stage-and-visual-closure`
- Mode: `repair`
- Repair scope: one MP14 error-mapping branch and its focused frontend regression fixture/assertion.
- No backend, database, migration, dependency, API schema, styling, source document, protected path,
  orchestrator-owned state/progress fact, or git metadata was changed by this repair.

## Demonstrated risk and control

- A real HTTP 503 becomes an `AuthSessionError` containing server-provided text. MP14 previously
  displayed that text to the borrower, which both violated the declared safe-error browser contract
  and risked exposing internal/provider detail.
- The repair preserves the tailored 401 expired-session and 403 unauthorised messages, but maps all
  other status/download errors to MP14's existing operation-specific safe fallback.
- The regression now uses the exact shared-client 503 error shape and asserts that `Unavailable.` is
  absent, closing the test seam that allowed the browser failure through.

## Residual risk

- Chrome cannot create a page inside the coding sandbox. Ralph's external validator must run the
  declared browser contract twice and produce `mp14-processing.png`,
  `mp14-disbursed-advice.png`, and `mp14-safe-error.png` before any commit.
- The quarantined slice still contains High-risk financial-stage projection work from the original
  implementation. This repair leaves that passing implementation unchanged, and full independent
  frontend/backend revalidation remains mandatory.
