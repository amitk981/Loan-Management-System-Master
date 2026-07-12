# Execution Plan

Selected slice: 006Y3-member-registry-and-identity-change-approval-closure
Mode: repair

1. Preserve the quarantined 006Y3 implementation and diagnose only the independent trusted-browser
   failure recorded by run `2026-07-12_100436_repair`.
2. Use the twice-reproduced trusted Playwright failure as the red signal; inspect the profile/modal
   structure and narrow the approval locator to the intended existing control without changing UI.
3. Re-run the focused Playwright contract where the sandbox permits, collect the spec as a fallback,
   and run proportional frontend gates because the repair changes only an E2E test.
4. Save red/green evidence and required repair artifacts, confirm protected paths and diff limits,
   then update Ralph progress, handoff, state, and the already-complete slice status only as needed.
5. Confirm the next one or two Not Started slices are already concretely sharpened from the Epic 004
   material opened in this run; do not broaden this repair if no sharpening is needed.
