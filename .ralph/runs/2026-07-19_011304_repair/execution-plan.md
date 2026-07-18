# Execution Plan

Selected slice: 009I2-portal-disbursement-stage-and-visual-closure
Mode: repair

1. Preserve the quarantined 009I2 implementation and use the saved trusted-browser failure as
   the authoritative symptom: every scenario times out in the shared application-selection helper
   before MP14 is opened.
2. Reproduce only the first Playwright scenario against real Django to establish a fast,
   deterministic red/green loop, then inspect the selected-application navigation and current
   portal headings at that exact seam.
3. Rank and test the smallest plausible causes (stale heading assertion, failed selection state,
   or unexpected application-detail rendering) one variable at a time. Change only the browser
   contract or the already-scoped portal code proven responsible.
4. Re-run the focused first scenario, then all three declared MP14 scenarios and confirm the three
   required screenshots are non-empty in this repair run's evidence directory.
5. Run impacted frontend unit tests, typecheck, lint, and build. Do not repeat the complete backend
   suite; the normal run's backend implementation already passed and the orchestrator will perform
   full independent revalidation.
6. Save repair logs and complete risk-assessment.md, review-packet.md, and final-summary.md with the
   demonstrated cause, exact verification, and remaining independent-browser-gate expectation.
