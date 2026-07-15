# Execution Plan

Selected slice: architecture-review

Production code will not be modified.

1. Pin the review window at the previous successful architecture-review commit `c843ea8` and
   inventory the four merged slices through `HEAD`: 007F2, CR-004, 007G2, and 007H2.
2. Read each reviewed slice, its retained run evidence, the Epic 007 digest and cited source
   sections, then inspect every production and test hunk in `git diff c843ea8...HEAD`.
3. Run independent Standards and Spec reviews, while the primary review checks assertion quality,
   edge cases, duplication, deep-module ownership, functional-requirement traceability, context
   truth, and stale Blocked slices.
4. Append the newest-first result to `docs/working/REVIEW_FINDINGS.md`; create or sharpen corrective
   slices for significant findings, record an ADR only if a durable undecided architecture choice
   is discovered, and sharpen the next one or two Not Started slices from already-opened sources.
5. Run the configured frontend/backend gates plus queue/state/path checks. Preserve self-contained
   review and terminal evidence in this run folder.
6. Finish `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, `final-summary.md`, state,
   progress, handoff, and the architecture-review descriptor without committing, adding, or
   pushing git changes.
