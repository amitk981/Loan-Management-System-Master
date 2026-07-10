# Execution Plan

Selected slice: `architecture-review`

## Boundaries

- Review the four product slices merged after architecture-review commit `1e2d873`:
  `005I2`, `006B`, `006C`, and `006D`.
- Use `git diff 1e2d873...HEAD` as the pinned comparison range while excluding the unrelated
  Ralph agent-configuration commit from product findings.
- Do not modify production code or `docs/source/`.

## Review Steps

1. Run independent Standards and Spec reviews against the pinned diff, slice files, epic files,
   working contracts, and relevant digests.
2. Inspect the product diff and tests directly for meaningful assertions, boundary cases,
   permission/object-scope behavior, failed-write preservation, duplication, and architecture drift.
3. Spot-check the reviewed requirements against the cited source sections; use existing digests
   first and record any newly distilled source facts in the matching digest.
4. Check whether an epic completed in the review window and, if so, trace every applicable
   `M##-FR-###` requirement to implementation or an explicit deferral in `ASSUMPTIONS.md`.
5. Prepend findings to `docs/working/REVIEW_FINDINGS.md`; create or sharpen a corrective slice for
   each significant issue, and record an ADR only if the review uncovers a durable design decision.
6. Sharpen the next one or two `Not Started` slices (`006E`/`006F`) only with requirements already
   opened during this review.
7. Run the full Ralph quality gates and save self-contained terminal evidence.
8. Complete `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, `final-summary.md`, state,
   progress, handoff, and architecture-review status without committing, adding, or pushing.

## Expected Evidence

- Pinned comparison range and reviewed commit list.
- Separate Standards and Spec reports.
- Focused test-quality/architecture/source-fidelity notes.
- Full backend check/tests/coverage/migration-sync and frontend lint/typecheck/tests/build logs.
- Protected-path, diff-limit, artifact-integrity, and whitespace checks.
