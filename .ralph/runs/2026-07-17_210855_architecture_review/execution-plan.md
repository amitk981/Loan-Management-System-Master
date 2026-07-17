# Execution Plan

Selected slice: architecture-review

1. Pin the independent review range at the previous successful architecture-review commit
   `e6fd78d1...HEAD`; inventory the four completed slices in that range (`CR-009`, `009E4`,
   `009G2`, and `009H2`) and distinguish non-slice Ralph maintenance commits.
2. Read the four completed slice contracts, their Epic 009 digest/source references, the changed
   production/test files, and retained run evidence. Map functional requirements, test claims,
   and declared architectural boundaries to the implementation.
3. Run the review skill's two independent axes in parallel: documented standards/architecture and
   source/spec fidelity. Supplement them with direct probes for test quality, edge cases,
   duplication, dependency direction, requirement-ID coverage, and current-context accuracy.
4. Reproduce significant suspected defects with review-only tests or focused read-only checks.
   Save terminal output under this run's `evidence/terminal-logs/`; do not modify production code.
5. Append a newest-first entry to `docs/working/REVIEW_FINDINGS.md`. Create or sharpen numeric,
   dependency-valid corrective slices for significant issues, and re-sharpen the next one or two
   `Not Started` slices using only source material opened during this review.
6. Re-check blocked-slice prerequisites and `docs/working/CONTEXT.md`, then update the architecture
   descriptor, state, progress, handoff, changed-files list, risk assessment, review packet, and
   final summary. Validate documentation scope, queue structure, JSON syntax, and the final diff.

Production code will not be changed. Product gates are intentionally not rerun because this
architecture-review lane is documentation-only; focused review probes are evidence, not fixes.
