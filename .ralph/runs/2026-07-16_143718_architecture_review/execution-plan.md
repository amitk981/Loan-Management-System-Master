# Execution Plan

Selected slice: architecture-review

1. Pin the review range to `1601a903...HEAD`, the successful architecture-review commit immediately
   before the five merged slices 008M3, 008M4, 009B2, 009C, and 009D; inventory the commits and
   production/test/docs diffs without changing production code.
2. Read those five completed slice specifications, their Epic 008/009 digests, and only their cited
   source sections. Identify repository standards from Ralph policy, the source architecture/API/data
   contracts, and existing architecture regression tests.
3. Run independent Standards and Spec review passes, then locally reproduce the highest-risk concerns
   with focused read-only inspection or tests. Evaluate assertion quality, edge cases, requirement-ID
   coverage, duplication, dependency direction, context truth, and blocked-slice freshness.
4. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`. Create dependency-valid numeric
   corrective slices for significant reproducible issues, and sharpen the next one or two Not Started
   slices using only requirements already opened. Update the Epic 009 digest when distilled source
   requirements are added.
5. Run documentation/queue/protected-path and proportionate code quality gates, save self-contained
   evidence and required Ralph artifacts, then update state, progress, handoff, and the architecture
   review descriptor. Do not modify production code or protected/source files.

Permissions checked before edits: `.ralph/permissions.json` allows `.ralph/runs/**`,
`docs/working/**`, `docs/slices/**`, `.ralph/progress.md`, and `.ralph/state.json`; this plan excludes
all protected and forbidden paths.
