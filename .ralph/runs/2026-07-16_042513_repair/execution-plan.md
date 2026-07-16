# Execution Plan

Selected slice: 008M2-documentation-workspace-contract-and-visual-closure

1. Reproduce the independent trusted-browser contract failure with the repository's strict
   acceptance parser and preserve the failing output as repair evidence.
2. Repair only the demonstrated contract-format defect in the selected slice: leave the strict
   `Trusted Browser Acceptance` section with its recognized Spec/Screenshot entries and retain the
   behavioral acceptance prose under `Test Cases`.
3. Re-run the parser regression loop, Playwright collection, and the declared browser spec locally.
   Treat a macOS Chromium-service denial as sandbox evidence, not fabricated browser acceptance;
   the orchestrator remains authoritative for the twice-run browser contract and screenshots.
4. Run proportionate frontend checks plus repository/slice lint checks, save red/green and gate
   evidence, then refresh changed-files, risk assessment, review packet, final summary, progress,
   state, handoff, and slice status without disturbing the preserved 008M2 implementation.
