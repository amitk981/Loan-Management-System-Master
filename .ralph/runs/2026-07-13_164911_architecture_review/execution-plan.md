# Execution Plan

Selected slice: `architecture-review`

## Review Window

- Fixed point: prior successful architecture-review commit `48ef331`
- Comparison: `git diff 48ef331...HEAD`
- Product slices: `007C3`, `007D2`, `007D3`, and `007E`
- Production code policy: read-only; this run changes only permitted Ralph artifacts and review,
  queue, digest, context, assumption, ADR, progress, handoff, and state documentation when needed.

## Steps

1. Read the four completed slice specifications, Epic 007 digest/epic, their cited source sections,
   prior review findings, and retained run evidence.
2. Run independent Standards and Spec reviews over the pinned diff, covering real test assertions,
   edge cases, source fidelity, scope creep, duplication, module seams, and architecture drift.
3. Trace Epic 007 functional requirements touched by the window and verify every relevant item is
   implemented or explicitly deferred.
4. Verify `CONTEXT.md` against current repository structure and re-check all `Blocked` slice
   prerequisites against `.ralph/state.json`.
5. Append newest-first findings to `REVIEW_FINDINGS.md`; create or sharpen corrective slices for
   significant gaps, following numeric queue/dependency rules. Record an ADR only if a durable,
   previously undecided architectural choice is required.
6. Sharpen the next one or two Not Started slices from source material already opened.
7. Run documentation/queue checks and proportionate backend tests for any reviewed behavior that
   needs direct confirmation; save terminal evidence.
8. Finish `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, `final-summary.md`, and
   update state, progress, handoff, and architecture-review status without modifying production
   code or protected/source files.
