# Execution Plan

Selected slice: 008M5-documentation-durable-actions-and-blocker-closure
Mode: repair

1. Read the quarantined run's trusted-browser failure log and establish one deterministic command
   that reproduces the exact first-run failure without altering the existing 008M5 implementation.
2. Rank and test narrowly scoped hypotheses against the real-Django Playwright spec, preserving all
   five declared screenshot names and the source-required upload/re-upload, correction, blocker,
   restricted-state, final-approval, and narrow-screen behavior.
3. Change only the demonstrated E2E contract defect. Do not change backend/business behavior unless
   the failure proves that behavior is the cause; if business behavior must change, add a failing
   regression first and retain red/green evidence.
4. Re-run the focused Playwright contract/reproduction, frontend documentation tests, typecheck,
   lint, and build as proportionate repair gates. Do not run the full backend or coverage suite.
5. Save self-contained repair evidence, changed-files.txt, risk assessment, review packet, and final
   summary. Keep the selected slice Complete, retain current state/progress/handoff truth, and leave
   commit/merge/push to independent orchestration.
