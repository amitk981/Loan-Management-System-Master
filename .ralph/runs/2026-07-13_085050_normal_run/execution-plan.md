# Execution Plan

Selected slice: 006Z14-member-authority-action-and-calculation-proof-closure

## Scope

- Add independently selectable public member-authority matrix rows covering directory list/detail,
  update, identity approval, supply capture/verification, service evidence create/update,
  active-status calculation, and active-status verification.
- Prove permission and persisted member scope separately: an all-action-permission custom actor with
  no assignment receives the canonical nondisclosure error with an unchanged complete ledger; only
  the row's matching assignment enables that action, while a differently permissioned action stays
  denied. Cover global, created-by, assigned, active team, inactive team, unrelated team/member.
- Replace brittle source-text caller assertions with behavioral tests at the staff eligibility,
  authenticated portal, and borrower-limit boundaries, including cross-member substitution and
  zero-write proof.
- Remove the unused `calculate_for_actor` seam because the documented direct calculate endpoint is
  not implemented as a production public boundary and no production caller owns the seam.
- Preserve all active-member calculations, database constraints, maker history, audit/workflow
  behavior, and M02-FR-004..006 semantics.

## TDD sequence

1. Add one authority matrix row and run it alone to RED; make only the minimum fixture/production
   correction needed for GREEN, then repeat row-by-row.
2. Add scope-kind and unrelated-object rows, running each independently before the grouped matrix.
3. Add behavioral calculation-owner substitution tests for application eligibility, portal status,
   and borrower-limit projection; capture RED then GREEN evidence.
4. Remove the dead calculation seam and brittle caller whitelist, retaining the established AST
   dependency guard only for imports that cannot be proven behaviorally.
5. Run focused member/credit suites with coverage, then all configured backend and frontend gates.

## Evidence and closeout

- Save RED/GREEN and gate logs under `evidence/terminal-logs/`, plus a dependency inventory and
  focused coverage report in this run folder.
- Record changed files, risk assessment, review packet, final summary, state/progress/handoff, and
  mark only 006Z14 Complete after all gates pass.
- Sharpen the next one or two Not Started slices using source material already opened and update the
  Epic 006 digest with the durable closure summary.
