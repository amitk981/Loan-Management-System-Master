# Execution Plan

Run: `2026-07-17_075837_architecture_review`
Selected slice: `architecture-review`
Mode: `architecture_review`
Review range: `41df4f51...6d79db01`

1. Confirm the four merged slices since the previous review and inspect their slice files, run
   packets, commit diffs, and cited Epic 008/009 digests.
2. Run two independent review passes over the fixed range: documented standards/architecture and
   source/spec fidelity, including functional requirement traceability.
3. Independently inspect test assertions and edge cases, duplication/dependency direction, object
   scope, immutable evidence, concurrency/idempotency, API contracts, and migration safety; run only
   focused read-only probes or tests needed to substantiate findings.
4. Reconcile the two passes, append newest-first findings to `docs/working/REVIEW_FINDINGS.md`, and
   create or sharpen dependency-valid corrective slices for every significant issue.
5. Verify `CONTEXT.md` against repository truth, re-check all blocked slice prerequisites, sharpen
   the next one or two Not Started slices using already-opened source extracts, and update the Epic
   digests where the review adds durable facts.
6. Save self-contained evidence, `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and
   `final-summary.md`; update Ralph state, progress, handoff, and the architecture-review descriptor.
7. Verify no production or protected file changed and run documentation/queue/state validation
   appropriate to an architecture-review-only run. Do not commit, add, push, or run the full suite.
