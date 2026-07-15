# Execution Plan

Selected slice: 007T-register-null-contract-and-action-order-closure

1. Verify the exact S23 backend legacy payload and the existing S21 request-generation seam against
   the slice, Epic 007 digest, cited source sections, and architecture-review finding.
2. RED/GREEN the S23 public UI behavior: replace reconstructed legacy fixtures with top-level null
   `purpose`/`risk`, make the DTO honest, and render the retained unavailable-value treatment without
   changing the register table/detail composition.
3. RED/GREEN the S21 public UI behavior one ordering case at a time: delay action detail/decision
   refreshes, begin newer success/denied/malformed/empty filter generations, and prove stale action
   results cannot replace current collection, totals, selection, detail, decision, or error state.
4. Normalize all touched S21 component and browser pagination fixtures so every mocked response is
   accepted by the production pagination contract; update the two declared browser scenarios and
   screenshot names without changing approved styling.
5. Run focused frontend tests, typecheck, lint, build, the full frontend suite, and collection-only
   Playwright checks. Save terminal logs and exact fixture trace; do not fabricate browser screenshots
   if Chromium cannot launch in the sandbox.
6. Review the diff against Standards and Spec, sharpen the next queued slice files using already-opened
   source/review facts, then update the slice status, state, progress, handoff, digest, changed-files,
   risk assessment, review packet, and final summary.

Public test seam: render `SanctionWorkbench`/`RegistersHub` with mocked authenticated feature-client
responses and assert visible state through user interactions. The existing queue/detail generation
refs remain the single ordering interface; no parallel request-state module or new visual pattern is
introduced.
