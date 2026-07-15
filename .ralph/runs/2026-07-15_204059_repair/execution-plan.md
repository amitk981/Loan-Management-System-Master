# Execution Plan

Selected slice: 008L4-portal-production-boundary-and-browser-proof

Mode: repair

1. Preserve the existing uncommitted 008L4 implementation and use the prior trusted-browser
   command as the red-capable feedback loop. Reproduce only the demonstrated post-login heading
   timeout and retain the output in this repair run's evidence.
2. Inspect the two declared Playwright specs, the portal login/session route, and the guarded E2E
   fixture to distinguish an invalid login-success assertion from a real fixture permission,
   identity, or session-persistence defect.
3. Add the smallest regression assertion at the E2E helper seam, observe it fail against the
   current helper contract, then repair only the demonstrated browser boundary failure. Do not
   change production role authority or the already-green backend/business logic unless the focused
   evidence proves that is the cause.
4. Run Playwright collection and the exact declared trusted-browser command twice. Retain all four
   genuine screenshots and both run logs when Chromium is available; if sandbox launch is denied,
   retain the honest launch failure and rely on orchestrator acceptance as directed.
5. Run proportionate frontend/backend gates, check protected paths and diff limits, then update the
   repair artifacts (`changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and
   `final-summary.md`) plus Ralph state/progress/handoff/slice status only as warranted by the
   verified repair.
