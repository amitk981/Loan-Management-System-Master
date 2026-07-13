# Execution Plan

Selected slice: architecture-review

1. Pin the review range at the previous successful architecture-review commit (`1ff6cb8...HEAD`),
   inventory the four completed product slices (005E4, 006H7, 006H3, and 006X), and separate the
   intervening Ralph-orchestrator commit from product findings.
2. Read the four slice contracts, Epic 005/006 digests, applicable source references, prior review
   findings, and changed files/tests; map the Epic 005/006 functional-requirement dispositions.
3. Run the review skill's independent Standards and Spec axes in parallel, while the primary review
   checks real assertions, negative/edge cases, duplication, deep-module boundaries, dependency
   direction, browser-evidence fidelity, and architecture drift.
4. Verify the wider architecture-review duties: `CONTEXT.md` truthfulness, every Blocked slice's
   prerequisites, queue integrity, corrective-slice closure, and the next two Not Started slices.
5. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`; create or sharpen corrective
   slices only for significant gaps. Do not modify production code or protected/source files.
6. Run proportionate backend/frontend and docs/queue gates, save self-contained review evidence,
   `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`, then update
   Ralph state, progress, handoff, and any digest/run-ahead notes required by the findings.
