# Execution Plan

Selected slice: 007F2-exception-routing-coherence-and-explicit-projection-closure

## Scope and interfaces

- Exercise the existing sanction submission/enrichment HTTP endpoints, approval-case list/detail/action
  endpoints, Exception Register endpoint, sanction-decision endpoint, and Credit Sanction Register
  endpoint. Do not add frontend scope or a new public endpoint.
- Keep approval coherence and reader-index synchronization behind
  `approvals.modules.approval_case_projection.refresh_approval_case_projection`; invoke it explicitly
  from approval-owned writers only.

## TDD sequence

1. Add one public HTTP tracer proving a reviewed above-limit appraisal with distinct approval and
   exception business reasons can be enriched, listed, retrieved, approved by the CFO and two
   Directors, and observed in both terminal registers. Capture the failing RED output.
2. Correct the coherence invariant minimally so independently authored approval/register reasons
   remain distinct while same-case exception type/reason/risk, frozen limit provenance, exception
   condition, and matrix facts remain coherent. Run the tracer GREEN.
3. Add public HTTP denial cases for contradictory frozen amount/exception-flag snapshots and prove
   stable zero-write behavior; retain forced within-limit waiver coverage through the public route.
   Implement the frozen amount/flag agreement check before any routing writes.
4. Extend public replay/conflict tests across changed reason, risk, type, amount, and provenance so
   exact replay is zero-write and mismatches cannot rewrite or hide the original case.
5. Add persistence tests proving direct appraisal/case saves do not synchronize cross-table
   projection state, remove the appraisal `post_save` receiver, and explicitly refresh from every
   approval-owned writer that can change projection inputs, including returned/new-cycle flows.
6. Update `docs/working/API_CONTRACTS.md` and the Epic 007 digest with the corrected invariant and
   ownership of the two reason fields.

## Verification and evidence

- Store focused RED/GREEN command output under
  `.ralph/runs/2026-07-13_202809_normal_run/evidence/terminal-logs/`.
- Run focused backend tests after each TDD cycle, then Django check, migration sync, full backend
  coverage, and all frontend build/typecheck/lint/test gates with the mandated interpreters/tools.
- Save changed-files, risk assessment, review packet, final summary, progress/handoff/state, and
  complete the selected slice only after all gates pass. Sharpen the next one or two Not Started
  slices using only source material already opened.
