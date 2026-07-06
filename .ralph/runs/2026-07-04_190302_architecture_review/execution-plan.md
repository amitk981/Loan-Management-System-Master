# Execution Plan

Selected slice: architecture-review

Mode: architecture_review

## Scope
- Review the four product slices merged since the previous architecture-review commit `7908071`: `002G2`, `002I`, `002J`, and `002K`.
- Do not modify production code, migrations, source documents, scripts, protected Ralph config, or frontend styling.
- Use the slice files and existing epic digest as the spec surface; open source docs only for narrow source-reference spot checks if the slice/digest requires it.

## Steps
1. Capture the review window with `git log 7908071..HEAD --oneline`, changed-file summaries, and targeted diffs.
2. Read the reviewed slice files and relevant run artifacts for test evidence, API examples, and review packets.
3. Critique test quality, source-doc fidelity, duplication, and architecture drift.
4. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`.
5. Create or sharpen corrective/follow-up slices only for significant issues.
6. Sharpen the next one to two `Not Started` slices from already-opened digest/source extracts.
7. Save review evidence, changed-files.txt, risk-assessment.md, review-packet.md, final-summary.md, and update Ralph state, progress, handoff, and slice status.
8. Run applicable quality/artifact checks for a docs-only review and save logs.
