# Execution Plan

Selected slice: `architecture-review`

1. Pin the review range to the previous successful architecture-review commit and enumerate the four subsequently merged slice commits.
2. Read only those four slice specifications, their Epic 009 digest/source anchors, the prior review findings, and the changed files in the pinned diff.
3. Review the range independently along two axes: documented standards/architecture and slice/spec fidelity. Inspect test assertions, negative and race coverage, duplication, module seams, and functional-requirement traceability.
4. Reproduce significant suspected defects with read-only inspection or focused review probes; do not modify production code and do not run the full backend suite.
5. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`; create concrete corrective slices for significant defects, then sharpen the next one or two eligible `Not Started` slices only from already-opened sources.
6. Re-check blocked-slice prerequisites and `docs/working/CONTEXT.md` accuracy. Update Ralph state, progress, handoff, the architecture-review descriptor, and this run's evidence, changed-files, risk, review packet, and final summary.
7. Validate documentation-only scope, queue structure, artifact completeness, and the final diff without committing, adding, or pushing.

Constraints: no production-code edits; no protected-file or `docs/source/` edits; all findings must cite reviewable file/test/spec evidence.
