# Execution Plan: Architecture Review

Selected slice: `architecture-review`

## Review Boundary

- Fixed point: previous successful architecture-review commit `220f3038`.
- Review head: starting worktree commit `e1698e87`.
- Three-dot diff: `git diff 220f3038...e1698e87`.
- Completed slices in range: 007R, 007S, 008A2, and 008B.

## Plan

1. Confirm the fixed point, commit list, changed-file inventory, and safe worktree state.
2. Read only the four reviewed slice specs, their cited Epic 007/008 digests and maps, relevant
   standards, and narrowly targeted source sections needed for fidelity checks.
3. Run independent Standards and Spec review passes in parallel as required by the review skill;
   separately inspect test assertions, edge cases, architecture boundaries, duplication, migrations,
   security/permission behavior, and functional-requirement traceability.
4. Reconcile findings against production diffs and focused tests. Append significant findings
   newest-first to `docs/working/REVIEW_FINDINGS.md`; create dependency-valid corrective slices for
   confirmed issues and record any durable architecture decision only if one is actually needed.
5. Verify `CONTEXT.md`, all Blocked-slice prerequisites, queue integrity, and the next 1-2 Not Started
   slice specs. Sharpen 008C/008D only where the already-opened Epic 008 material exposes missing
   execution detail.
6. Run proportional quality gates and save terminal output under this run's `evidence/terminal-logs/`.
   Produce `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`, then
   update Ralph state, progress, handoff, and the architecture-review descriptor without touching
   production code or protected/source files.
