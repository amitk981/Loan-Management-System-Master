# Execution Plan

Selected slice: architecture-review

1. Pin the review window to the four product-slice commits after the previous successful
   architecture review: `f35e0fc7...dbccea9c` (009E3, 009F2, 009G, 009H). Exclude later Ralph
   maintenance commits from product-slice findings while recording the current HEAD for audit.
2. Read the four completed slice specifications, Epic 009 digest/epic, their cited source sections,
   and the repository architecture/API standards needed for independent Standards and Spec passes.
3. Inspect the diff and tests for real assertions, negative/edge/concurrency behavior, source-doc
   fidelity, duplication, dependency direction, authority ownership, replay, and architecture drift.
   Run bounded read-only probes or focused retained tests only where they materially validate a
   suspected finding; do not modify production code.
4. Aggregate the two axes without masking one with the other. Append newest-first findings to
   `docs/working/REVIEW_FINDINGS.md`; create fully executable corrective slices for significant
   findings and sharpen the next 1-2 Not Started slices from already-opened Epic 009 material.
5. Reconcile stale blocked slices, Epic 009 functional-requirement coverage/deferments, and
   `docs/working/CONTEXT.md`. Update the architecture-review descriptor, state, progress, handoff,
   and self-contained run evidence/artifacts.
6. Run documentation-lane checks: queue structure/dependencies, protected/production-path scope,
   changed-file/diff limits, and `git diff --check`. Record skipped product gates honestly because
   this review changes no production files.
