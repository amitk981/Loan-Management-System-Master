# Execution Plan

Selected slice: architecture-review

## Scope
- Do not modify production code.
- Review changes merged after the previous architecture review commit (`0120482`) through current `HEAD`.
- Focus product-slice critique on `002D-current-user-api-with-permissions-and-teams` and `002D2-backend-dev-infrastructure`; note Ralph workflow changes separately only if they affect run safety.

## Steps
1. Read required Ralph context, selected completed slice files, Epic 002 digest, and relevant prior run packets.
2. Inspect git diff and changed-file lists for the review window.
3. Critique test quality, source-doc fidelity, duplication, architecture drift, and run evidence.
4. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`.
5. Create or sharpen corrective slices for significant defects, and sharpen the next 1-2 `Not Started` slices using only already-opened source/digest context.
6. Run configured quality gates where possible and save outputs in this run folder.
7. Save `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, `final-summary.md`, and update Ralph state/progress/handoff.
