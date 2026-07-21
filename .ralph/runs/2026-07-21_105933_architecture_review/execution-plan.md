# Execution Plan

Selected slice: architecture-review

## Scope

Perform only the bounded oversized-slice queue rewrite requested for failed slice `010M`. Do not
modify production code, protected paths, source documents, orchestrator-owned state/progress, or
unrelated slice contracts.

## Retained Input

- Original slice: `docs/slices/010M-servicing-and-monitoring-frontend-wiring.md`.
- Failed run: `.ralph/runs/2026-07-21_102540_normal_run/` in the integration checkout.
- Measured candidate: 21 files and 2,093 changed lines against a 2,000-line limit.
- Retained contract: staff S43-S52 wiring, four mock-removal owners, four browser screenshots,
  frontend/backend red-green evidence, idempotency/permission/error-state proof, and High risk.

## Rewrite Plan

1. Mark `010M` `Superseded`, identify both successors, and retain the failed-run measurement and
   allocation rationale in the original slice.
2. Create `010MA` for account schedule/ledger plus direct repayment, statement exception, and
   subsidiary-reconciliation wiring. It inherits `010M`'s prerequisite `010L` and owns the three
   repayment/account mock removals and the ledger/posting browser outputs.
3. Create `010MB` for interest operations plus DPD/reminder monitoring. It depends on `010MA`, owns
   the monitoring mock removal, and owns the interest/monitoring browser outputs.
4. Preserve every original source reference, requirement, test behavior, evidence class, and risk
   either in the relevant successor or as a shared invariant explicitly consumed by both.
5. Retarget every downstream dependency on `010M` to terminal successor `010MB`; update the bounded
   Epic 010 digest only where its ownership/dependency wording would otherwise become stale.

## Validation Plan

- Confirm only queue metadata, the bounded digest, and this run's artifacts changed.
- Confirm both successor files contain `Origin` with exact marker ``Oversized slice: `010M` ``,
  recognized statuses, real acyclic dependencies, runtime capabilities, independent acceptance,
  retained evidence allocations, and predicted budgets comfortably below 2,000 lines.
- Confirm the original prerequisite is on `010MA`, `010MB` depends only on `010MA`, and all existing
  downstream dependencies previously naming `010M` name `010MB`.
- Run the repository's queue/split validation commands if available, plus targeted metadata searches
  and diff-stat checks. No product test suites are appropriate because production code is unchanged.
