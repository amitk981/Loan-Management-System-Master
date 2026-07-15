# Execution Plan

Selected slice: architecture-review

1. Pin the review window at prior architecture-review commit `b32559c` and inventory the commits,
   changed files, slice specifications, source references, tests, and retained evidence for the four
   completed slices: 007E2, 007F, 007G, and 007H.
2. Run independent Standards and Spec review passes over the completed-product diff
   `git diff b32559c...78d912f`, then inspect test quality, edge cases, requirement-ID coverage,
   duplication, deep-module boundaries, and context/queue truth as the Ralph architecture-review
   runbook requires. The later docs-only CR-004 intake commit is outside the product-review window.
3. Record newest-first findings in `docs/working/REVIEW_FINDINGS.md`; create or sharpen only the
   corrective/run-ahead slices justified by significant findings, and update the Epic 007 digest,
   assumptions/ADRs, context, blocked statuses, progress, state, and handoff only where the evidence
   requires it. Production code remains untouched.
4. Run documentation/queue validation and proportionate existing quality gates, save terminal
   evidence, changed-files, risk assessment, review packet, and final summary, and verify no protected
   or production path changed.
