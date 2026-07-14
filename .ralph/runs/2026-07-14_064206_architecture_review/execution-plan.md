# Execution Plan

Selected slice: architecture-review

1. Pin the previous successful architecture-review commit and enumerate the four subsequently
   completed slices (007O, 007P, 007Q, 008A), their commits, slice specs, epic digests, and cited
   source sections.
2. Review the complete diff independently along two axes: repository/Ralph architecture standards,
   and fidelity to the selected slice/source requirements. Inspect test assertions and edge cases,
   duplication, module boundaries, API/data contracts, and production-code drift; do not edit
   production code.
3. Verify completed-epic functional requirement coverage, `CONTEXT.md` truthfulness, and every
   blocked slice against `.ralph/state.json`. Record significant findings newest-first and create or
   sharpen executable corrective slices when evidence warrants them.
4. Run documentation/queue validation and proportionate project gates, save self-contained terminal
   evidence, and produce `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and
   `final-summary.md`.
5. Update the architecture-review descriptor, Ralph state/progress/handoff, and sharpen the next one
   or two Not Started slices using only the source material already opened during this review.

Production code is read-only for this run. `docs/source/` and all protected paths remain unchanged.
