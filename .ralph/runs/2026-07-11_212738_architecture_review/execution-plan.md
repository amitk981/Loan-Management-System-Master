# Execution Plan

Selected slice: architecture-review

1. Pin the review range at the previous architecture-review commit (`7a3d1c9...HEAD`) and identify
   the four completed product slices in that range plus any intervening repository changes.
2. Read each completed slice, its parent epic/digest and cited source sections needed for fidelity;
   map applicable functional requirement IDs and inspect the actual commit diffs and tests.
3. Run independent Standards and Spec reviews in parallel, then independently check test quality,
   edge cases, duplication, module boundaries, dependency direction, and architecture drift.
4. Verify repository-wide architecture-review duties: `CONTEXT.md` truthfulness, stale `Blocked`
   slices, source requirement disposition, and the next one or two `Not Started` slice definitions.
5. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`; create or sharpen corrective
   slices only for significant actionable gaps, without modifying production code.
6. Run documentation/queue validation and proportionate existing quality checks, then save
   self-contained evidence, changed-files, risk assessment, review packet, final summary, and
   update Ralph state, progress, handoff, and the architecture-review descriptor as required.
