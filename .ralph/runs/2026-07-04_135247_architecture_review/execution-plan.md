# Execution Plan

Selected slice: architecture-review
Run ID: 2026-07-04_135247_architecture_review

## Scope
- Review the four completed slices since the previous architecture-review commit `0939e01`: `002EYA`, `002F2`, `002G`, and `002H`.
- Do not modify production code.
- Review for test quality, source/doc fidelity, duplication, architecture drift, and whether existing corrective findings were actually closed.

## Steps
1. Read required Ralph context, the epic digest, and the reviewed slice/run artifacts.
2. Inspect `git diff 0939e01..HEAD`, per-slice files, tests, and evidence packets.
3. Spot-check source/doc fidelity using the already-opened epic digest and only targeted source docs if the slice references require it.
4. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`.
5. Create or sharpen corrective `docs/slices/` entries for significant findings; sharpen the next 1-2 `Not Started` slices using only already-opened context.
6. Run required quality gates and save evidence under `.ralph/runs/2026-07-04_135247_architecture_review/evidence/terminal-logs/`.
7. Save `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, `final-summary.md`, and update Ralph state/progress/handoff/slice status.
