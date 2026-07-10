# Ralph Handoff

## Last Run
2026-07-11_030117_architecture_review

## Current Status

The due independent review covered `006E4`, `006F4`, `004E`, `006G2`, and `006H2` from fixed point
`6efe1a8`. Production code was not changed. 006E4's remediation/history behavior and 006F4's twice-
green five-race PostgreSQL execution are substantive. Four corrective slices now precede the visual
restoration and Epic 006 tracer:

- 002J2 aligns authenticated missing-permission errors with source-standard `403 FORBIDDEN` while
  preserving object/sensitive/approval denial codes and all authorization decisions.
- 004E2 envelopes malformed witness bodies, snapshots the exact qualifying shareholding/folio,
  conservatively handles legacy rows, removes redundant indexes, and moves witness list composition
  behind its application-owned seam.
- 006G3 removes the `credit -> approvals -> credit` cycle, moves sanction workflow-event creation
  into the atomic approvals handoff, and reruns the five PostgreSQL races with exact evidence
  assertions.
- 006H4 replaces the Workbench's global-permission union with authoritative resource actions and
  adds real default-container interaction tests for every action/denial/reload path.

006H3 now depends on 006H4 and continues to own prototype visual fidelity and deterministic
Playwright screenshots. 006X remains behind 006H3. M02-FR-009/BR-010 remains open until 004E2;
M04-FR-010/011 UI confidence remains open until 006H4. M04-FR-001/002 stay explicitly deferred to
012EA under A-053; M04-FR-003 retains A-054.

`docs/working/CONTEXT.md` still describes the repository truthfully. `.ralph/state.json` has no
Blocked slices, so no stale prerequisites required reopening.

## Validation

Architecture-review evidence and configured gate logs are under
`.ralph/runs/2026-07-11_030117_architecture_review/`. Review findings are newest-first in
`docs/working/REVIEW_FINDINGS.md`. No source, production, or protected file was edited.

## Next Run

Run `002J2-forbidden-permission-error-contract-alignment`, then 004E2, 006G3, 006H4, 006H3, and
006X in dependency order. Do not treat the current Workbench action UI or witness verification
history as accepted until their corrective slices pass.
