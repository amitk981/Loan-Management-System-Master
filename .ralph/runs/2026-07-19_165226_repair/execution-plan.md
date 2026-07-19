# Execution Plan

Selected slice: CR-012-epic-009-playwright-evidence-is-incomplete

1. Preserve the quarantined CR-012 implementation and use the retained trusted-browser execution as
   the red-capable feedback loop: CFC authorisation returns HTTP 200 but the assertion expects a
   nested alert after the authorised row has left CFC scope.
2. Minimise the failure against the existing `PaymentAuthorisationHub` behavior and its focused test;
   distinguish API failure from successful terminal queue removal using the exact response and the
   visible empty state.
3. Repair only the demonstrated Playwright assertion. Await and verify the genuine Django
   authorisation response, then verify the terminal CFC queue state before advancing the fixture.
4. Run focused backend and frontend regressions, Playwright collection/static contract checks,
   typecheck, lint, and build. Attempt the declared browser spec locally only if Chromium launches;
   never fabricate screenshots or weaken the nine-state/hash contract.
5. Inspect targeted diffs and protected paths, save terminal evidence, and complete the risk
   assessment, review packet, and final summary with the review result exactly
   `Ready for independent validation`.
