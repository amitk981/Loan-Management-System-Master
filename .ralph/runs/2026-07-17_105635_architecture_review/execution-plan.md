# Execution Plan

Selected slice: `architecture-review`

1. Pin the review range at prior architecture-review commit `24bfc4f4` through current `HEAD`,
   covering completed slices 008M7, 009D4, 009E2, and 009F only.
2. Read the four completed slice specifications, their Epic 008/009 digests, the repository's
   documented architecture/API/data-model standards, and the relevant cited source sections.
3. Run independent Standards and Spec review passes over `git diff 24bfc4f4...HEAD`; separately
   inspect test assertions, edge cases, duplication, dependency direction, requirement-ID
   traceability, blocked-slice prerequisites, and CONTEXT accuracy.
4. Reproduce significant suspected defects with read-only inspection or review-only focused probes.
   Do not modify production code and do not run the full backend suite.
5. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`; create fully executable
   corrective slices for significant issues, sharpen the next 1-2 Not Started slices using only
   already-opened source material, and update the epic digests/CONTEXT only where repository truth
   has materially moved.
6. Save self-contained review evidence, changed-files, risk assessment, review packet, final
   summary, and update Ralph state/progress/handoff plus the architecture-review descriptor.
7. Run docs/queue/protected-path validation and focused retained tests or checks proportionate to
   any findings. Leave independent full validation to the orchestrator.

No production source file will be edited in this run.
