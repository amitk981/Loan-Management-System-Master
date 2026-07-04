# Execution Plan

Selected slice: architecture-review

Mode: architecture_review. This run will not modify production code.

1. Establish the review window from the previous architecture-review commit and Ralph run history.
2. Read only the relevant completed slice files, run packets, digests, and touched source files needed to critique the merged work.
3. Review the merged diffs for test quality, doc/source fidelity, duplication, architecture drift, and requirement-ID tracking.
4. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`.
5. Create or sharpen corrective slice files for significant findings, and sharpen the next 1-2 `Not Started` slices using already-opened source/digest material.
6. Save run artifacts: evidence logs, `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, `final-summary.md`.
7. Update Ralph state/progress/handoff and mark the architecture review complete without running git add/commit/push.
