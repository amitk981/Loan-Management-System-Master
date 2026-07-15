# Execution Plan

Selected slice: CR-005-mp07-completed-download-status-visible

1. Confirm the MP07 public rendering contract and document the CR blast radius before product edits.
2. Add one rendered-interface regression proving that a `complete` Term Sheet shows both the
   canonical Complete badge and its authorised Download control, with no Upload or Re-upload.
3. Run the focused test and save the expected RED output under `evidence/terminal-logs/`.
4. Make the smallest MP07 visibility change using the existing `StatusBadge` and current layout;
   do not change API types, server policy, styling, or MP13.
5. Rerun the focused test and save GREEN output, then run frontend lint, typecheck, tests, and build.
6. Run the configured backend check, migration-drift check, and full coverage suite with the
   orchestrator-managed Python interpreter, even though no backend code changes.
7. Save self-contained evidence and Ralph review artifacts, sharpen the next eligible slice from
   already-read requirements, and update slice/state/progress/handoff only after all gates pass.
