# Execution Plan

Selected slice: `architecture-review`

## Review boundary

- Fixed point: previous successful architecture-review commit `1f1d500`.
- Review range: `git diff 1f1d500...HEAD` and `git log 1f1d500..HEAD`.
- Completed product slices in scope: `002J2`, `004E2`, `006G3`, `CR-001`, and `006H4`.
- Production code is read-only for this run.

## Work plan

1. Read each in-scope slice, its run packet, relevant epic/digest requirements, and the changed implementation/tests.
2. Run independent Standards and Spec review axes, then inspect test assertions, edge cases, duplication, module direction, and architecture drift directly.
3. Trace completed-epic functional requirement IDs and explicit deferrals; verify `CONTEXT.md` remains accurate and re-check every Blocked slice prerequisite.
4. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`; create or sharpen corrective slices only for significant issues, without changing production code.
5. Sharpen the next two eligible Not Started slices using requirements already opened, and update their digest if new distilled requirements are needed.
6. Run the required frontend/backend quality gates and documentation/integrity checks using the mandated backend interpreter.
7. Save self-contained evidence, `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; update Ralph state, progress, handoff, and the architecture-review descriptor status.

## Expected evidence

- Review-boundary commit/diff inventory and two-axis review reports.
- Functional-ID, blocked-slice, context-truth, and production-code-unchanged checks.
- Frontend build/typecheck/lint/test and backend check/migration/coverage logs.
- Final protected-path, changed-file, and diff-limit verification.
