# Execution Plan

Selected slice: `architecture-review`

1. Pin the review range to the previous successful architecture-review commit and inventory the
   four subsequently merged slice commits, their changed files, run evidence, slice specifications,
   epic digests, and cited source sections.
2. Review the range independently along two axes: documented standards/architecture conformance and
   source/slice-spec fidelity. Explicitly inspect assertion quality, negative/edge coverage,
   duplication, module boundaries, functional requirement traceability, and evidence truthfulness.
3. Reconcile findings against current repository state, existing review findings, assumptions,
   blocked slices, the next `Not Started` queue entries, and `CONTEXT.md`; avoid duplicate corrective
   work and create or sharpen executable corrective slices only for significant unresolved defects.
4. Append the newest review entry to `docs/working/REVIEW_FINDINGS.md`, update the matching digests,
   and record an ADR only if this review establishes a new durable architectural decision.
5. Run focused review checks and all configured quality gates, then save self-contained evidence,
   `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.
6. Update Ralph state, progress, handoff, architecture-review descriptor/status, and the next one or
   two `Not Started` slices without modifying production code or protected/source files.
