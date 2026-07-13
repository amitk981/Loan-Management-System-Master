# Execution Plan

Selected slice: `architecture-review`

## Scope and constraints

- Review the non-empty three-dot diff `git diff 46442fe...HEAD` covering completed slices
  `006E3`, `006F3`, `006G`, and `006H` since the prior architecture-review commit.
- Do not modify production code or protected/source files. Permitted edits are limited to Ralph run
  evidence, review/state/handoff/progress documentation, ADRs if a durable decision is needed, and
  corrective or next-slice files when review findings justify them.
- Treat the four slice files, Epic 006 file/digest, and their cited source sections as the spec; use
  repository architecture/API/frontend rules as the standards axis.

## Review plan

1. Save the pinned commit list, production-only diffs, and prior-review closure map in this run's
   evidence folder.
2. Read each reviewed slice and its run packet; inspect implementation and tests for meaningful
   assertions, edge cases, source fidelity, duplication, module boundaries, transaction/lock order,
   frontend state and authority checks, and evidence accuracy.
3. Run independent Standards and Spec review agents over the same pinned range, then reconcile their
   reports without collapsing the two axes.
4. Spot-check Epic 006 functional requirement IDs against implementation or explicit deferrals.
5. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`; create or sharpen corrective
   slices only for significant issues, and sharpen the next one or two Not Started slices using only
   source material already opened.
6. Run all configured backend/frontend quality gates with the mandated interpreter, plus diff,
   protected-path, artifact, and permission checks. Save complete logs in the run folder.
7. Write `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; update
   `.ralph/state.json`, `.ralph/progress.md`, and `docs/working/HANDOFF.md` to close the review run.
