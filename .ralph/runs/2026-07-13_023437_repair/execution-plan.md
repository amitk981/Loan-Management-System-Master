# Execution Plan

Selected slice: 006Z8-portal-limit-provenance-module-and-interaction-closure

Mode: repair

1. Preserve the quarantined implementation and use the two saved trusted-browser logs as the
   authoritative red signal: portal entry intermittently lacks the dashboard control or fails to
   reach the routed MP05 heading after that control is activated.
2. Inspect only the declared Playwright spec and the existing portal auth/dashboard/router seams;
   rank and falsify post-login remount, event-dispatch, incomplete fixture, and leaked-request causes.
3. Add or tighten the smallest non-browser regression seam that catches the demonstrated portal
   entry failure, save red evidence, then make the smallest e2e-fixture-only repair.
4. Run the focused regression green, Playwright collection, and the declared spec locally when the
   sandbox permits Chromium. Do not fabricate screenshots; the independent two-run browser gate is
   authoritative.
5. Run configured frontend/backend gates in proportion to the repair, verify protected paths and
   diff limits, and save self-contained evidence, changed-files, risk, review, and final summary.
6. Refresh state, progress, handoff, selected-slice status, and the already-sharpened next slice
   without changing protected files or invoking git mutation commands.
