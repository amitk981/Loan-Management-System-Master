# Execution Plan

Selected slice: 006Y13-member-mutation-success-interaction-closure

1. Use the two trusted-browser logs from `2026-07-12_230715_repair` as the failing-first signal and
   confirm the exact server request sequence around the failed canonical-read count.
2. Repair only the demonstrated Playwright synchronization defect by awaiting each post-mutation
   canonical member-detail response before asserting ledger cardinality; preserve all exact mutation
   URL, method, body, masking, authority, and screenshot assertions.
3. Run the declared Playwright spec twice with the required Ralph evidence directory, preserving both
   green logs, the request ledger, and all five declared screenshots.
4. Run the focused mounted frontend tests plus configured frontend gates, then update this run's
   evidence, changed-files list, risk assessment, review packet, final summary, progress, state,
   handoff, and selected slice status without modifying protected files.
5. Re-check the already-sharpened next slices 006Z5 and 006Z2; change them only if the source-backed
   requirements needed for execution remain incomplete.
