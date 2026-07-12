# Execution Plan

Run: `2026-07-12_152923_repair`  
Slice: `006Y8-witness-maker-checker-and-browser-closure`  
Mode: repair

1. Reproduce the prior trusted-browser failure with the declared Playwright spec and preserve the
   failing output as repair evidence.
2. Trace the routed Application Detail URL and authenticated reload behavior, then identify the
   smallest demonstrated cause of the canonical witness view disappearing.
3. Add or tighten a regression assertion at the correct routing/browser seam before changing the
   implementation, when the current spec does not already express that assertion.
4. Apply only the minimal repair needed for persisted contact and maker-checker identity correction
   to survive a full routed reload.
5. Re-run the focused browser contract, relevant frontend tests, and configured quality gates; save
   red/green evidence and the required screenshots when Chromium is available.
6. Refresh the run artifacts (`changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and
   `final-summary.md`) and update Ralph state/progress/handoff only to reflect verified results.

Permissions were checked against `.ralph/permissions.json`: the expected E2E/frontend and run
artifact paths are allowed; protected and forbidden paths will not be edited.
