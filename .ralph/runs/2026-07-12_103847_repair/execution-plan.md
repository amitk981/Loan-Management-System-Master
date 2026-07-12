# Execution Plan

Selected slice: 006Y3-member-registry-and-identity-change-approval-closure

Mode: repair

1. Read the prior repair's trusted-browser logs and artifacts, then establish a fast,
   deterministic Playwright feedback command that asserts the exact missing screenshot/failing
   browser step.
2. Rank and test hypotheses against the existing uncommitted 006Y3 implementation without
   changing unrelated production behavior.
3. Add or tighten the narrow browser-contract regression first, capture its failing output, and
   make only the smallest E2E/fixture/product correction demonstrated by that failure.
4. Capture green output from the narrow loop, collect the declared spec, and run all configured
   frontend/backend quality gates with the mandated backend interpreter.
5. Save self-contained evidence, changed-files/risk/review/final artifacts, and update Ralph
   progress/state/handoff/slice status consistently. Preserve the already-sharpened next slices.
