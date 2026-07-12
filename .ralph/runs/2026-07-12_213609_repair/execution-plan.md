# Execution Plan

Selected slice: `006Y11-member-form-container-and-error-matrix-closure`

1. Preserve the quarantined 006Y11 implementation and use the failed trusted-browser assertion as
   the repair feedback loop: the backend projects the enabled approval action with
   `required_permission: members.member.identity_change.approve`, while the E2E contract incorrectly
   expects `members.member.update`.
2. Confirm the canonical permission at the backend registry/projection seam and in existing focused
   tests, then reproduce the exact mismatch with the smallest agent-runnable test/collection command.
3. Change only the demonstrated stale browser assertion. Do not change production authority,
   styling, data flow, or any other slice behavior.
4. Re-run the focused E2E contract (or Playwright collection if Chromium is unavailable), the
   relevant member frontend tests, and the configured frontend gates. Save repair evidence under
   this run's `evidence/terminal-logs/` directory.
5. Review the full preserved diff for protected-path and scope safety, then write changed-files,
   risk assessment, review packet, final summary, and truthful state/progress/handoff artifacts for
   independent full revalidation. The previously sharpened 006Z4 and 006Z2 slices remain unchanged.
