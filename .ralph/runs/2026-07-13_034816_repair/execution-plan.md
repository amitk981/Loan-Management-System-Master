# Execution Plan

Selected slice: `006Z10-portal-limit-interaction-and-boundary-proof`

1. Preserve the quarantined implementation and reproduce the trusted-browser failure with the
   focused Playwright scenario recorded in the prior run.
2. Rank and test only hypotheses that explain the demonstrated strict-mode locator collision; do
   not alter production behavior or broaden the slice.
3. Add the narrowest accessible-name selector correction in the existing E2E contract, rerun the
   focused scenario twice, and confirm all four required screenshots are non-empty.
4. Run the configured frontend and backend gates, then refresh repair-run evidence, changed-files,
   risk assessment, review packet, final summary, state, progress, handoff, and slice status without
   modifying protected files or committing.
