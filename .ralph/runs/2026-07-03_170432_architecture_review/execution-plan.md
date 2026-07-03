# Execution Plan

Selected slice: architecture-review

Mode: architecture-review. Production code must not be modified.

1. Confirm the review window from Ralph state, previous architecture-review artifacts, run folders, and git history.
2. Read only the completed slice files, parent epic/digest material, review packets, and source references needed to judge the merged changes.
3. Review diffs for the slices completed since the last architecture review:
   - test quality and meaningful assertions;
   - source-document and digest fidelity;
   - API envelope/auth service boundary consistency;
   - duplication, layering, and architecture drift;
   - explicit deferrals and assumptions for requirement IDs.
4. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`.
5. Create or sharpen corrective slice files only for significant issues found.
6. Run the applicable validation gates for a docs-only architecture-review run and save terminal output under `.ralph/runs/2026-07-03_170432_architecture_review/evidence/terminal-logs/`.
7. Save `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; update Ralph state, progress, handoff, and virtual slice completion status.
