# Review Packet: 2026-07-21_054048_architecture_review

## Result
Ready for independent validation

## Slice
architecture-review

## Scope

- Fixed point: validated terminal-finalizer commit
  `b7dbc27b622bee6a159b164d9e0b75aa5517ff47`.
- Product commits: `af2ece48` (010H3), `575bb535` (010I2), `72594e89` (010J2),
  and `77bbe9c0` (010K). Ralph run evidence and mechanical bookkeeping were excluded from the
  product critique.
- Trusted inherited roots: `ROOT-010-INTEREST-CALCULATION-OWNER` generation 2 via 010H3,
  `ROOT-010-DPD-SNAPSHOT-OWNER` generation 1 via 010I2, and
  `ROOT-010-REMINDER-DELIVERY-OWNER` generation 1 via 010J2.
- Candidate scope is documentation, one corrective slice, its downstream dependency edge, and this
  review's retained evidence only. No production, migration, frontend, source, protected, state,
  progress, or mechanical handoff file changed.

## Standards Review

- High: MIS generation and transition replay return retained data before canonical report scope and
  exact submitted-CFO authority. A same-key generation probe returns 200 after read scope is removed.
- High: MIS reconstructs a historical portfolio from private live owners in separate queries. Late
  reminder evidence enters an older cutoff and no source-mutation race establishes one consistent
  as-of snapshot.
- High carried: reminder serviceability commits before the provider claim/invocation boundary; a
  repayment-winning adapter probe still observes an actual provider call.
- High carried: DPD ignores successful capitalisation schedule evidence and reports reclassified
  interest overdue again; snapshot reparenting and approved policy mutation remain possible.
- Medium carried: changed tests still compose other `TestCase.setUp()` implementations and 010K
  widens private-model reconstruction.

The independent report is retained at
`.ralph/runs/2026-07-21_054048_architecture_review/evidence/review-probes/standards-axis.md`.

## Spec Review

- 010H3 closes its approval-time policy, whole-decision rounding, and exact zero-write
  reclassification contract. Seven focused policy/mismatch tests pass.
- 010I2 is partial against AC-DPD2-1/2/3: the same-loan relation is guarded only from pointer writes,
  approved operational policy can mutate in place, and the source decision omits capitalisation.
- 010J2 is partial against AC-REM2-2/4/5: final provider authority is not one protected decision,
  101+ candidates have no continuation truth, and private communication models remain imported.
- 010K is partial against its cutoff, immutable-owner, and permission-scoped replay requirements:
  current authority is skipped on replay and post-cutoff owner rows can enter historical totals.

The independent report is retained at
`.ralph/runs/2026-07-21_054048_architecture_review/evidence/review-probes/spec-axis.md`.

## Owner-Level Disposition

- `AR-010-INTEREST-001` is Closed High. 010H3 passes the current seven-test closure matrix; the
  distinct downstream DPD consumption defect does not reopen calculation/reclassification writes.
- `AR-010-DPD-001` is Carried High. Mapping from generation 1 (`010I2`) to grouped `010K3` consumes
  this root's one ordinary successor (generation 2).
- `AR-010-REMINDER-001` is Carried High. Mapping from generation 1 (`010J2`) to grouped `010K3`
  consumes this root's one ordinary successor (generation 2).
- `AR-010-MIS-001` is New High at generation 1 through `010K3`.
- `AR-010-SERVICING-SEAM-001` remains Carried Medium. Correctness-bearing changed seams are absorbed
  by `010K3`; older test/ledger debt remains Epic 010 closure work without another leaf.
- `AR-010-LEDGER-001` remains Carried Medium and was neither changed nor reproduced in this bounded
  range.

## Root-Cause Boundary Correction

Across the prior and current reviews, corrective additions (4 + 1) exceed findings closed (0 + 1).
Instead of adding separate DPD, reminder, and MIS leaves, `010K3-servicing-as-of-owner-boundary-closure`
groups the related private/live owner symptoms behind one immutable as-of decision boundary while
preserving each root's independent generation history. Existing `010K2` now depends on `010K3`, so
statements, portal, and frontend work cannot consume the known inconsistent boundary.

The generated slice declares `postgresql-five-race-acceptance`; both the runtime-capability and
trusted PostgreSQL declaration validators pass. The coding sandbox cannot open the local PostgreSQL
Unix socket, so no trusted runtime result is fabricated; the product slice's declared independent
gate owns the twice-run five-test matrix.

## Focused Evidence

- Interest closure: 7 tests passed, Django check clean, exit 0.
- DPD owner: 2 pointer/policy tests failed on intended assertions; the public
  capitalisation-to-DPD probe separately failed `37000.00 != 0.00`.
- Reminder owner: 1 test failed because the provider was invoked after the schedule became paid.
- MIS owner: 2 tests failed—scope-less replay returned 200 and a late reminder was counted.
- Probe source, bound logs, independent axes, and fixed-point evidence are under
  `.ralph/runs/2026-07-21_054048_architecture_review/evidence/review-probes/`.

These are review RED signals, not product implementation gates. No complete backend, coverage,
frontend, or browser suite was duplicated for this documentation-only candidate.

## Source and Coverage Audit

- M10-FR-001–011 retain implemented rate, invoice, accrual, payment, capitalisation,
  communication, and evidence owners; 010H3 closes the active interest-calculation root.
- M11-FR-001–008/010 retain DPD, reminder, portfolio-summary, drill-down, and quarterly-MIS
  foundations, but correctness is explicitly conditional on `010K3` rather than silently marked
  complete. Later default/closure/compliance facts remain honestly unavailable under the 010K
  contract and their queued Epic 011/012 owners.
- `CONTEXT.md` now truthfully records the implemented MIS foundation and the single active as-of
  correction. No slice is `Blocked`, so no stale prerequisite required re-parking.
- No ADR was added because the corrective restores existing owner, cutoff, idempotency, permission,
  and relational-integrity contracts rather than choosing a new business rule.

## Convergence Metrics

- Findings closed: 1
- New Critical: 0
- New High: 1
- New Medium: 0
- New Low: 0
- Corrective slices added: 1

## Finding Closure Manifest

| Finding ID | Root ID | Severity | Disposition | Reproducer | Corrective Slice | Closure Evidence |
|---|---|---|---|---|---|---|
| AR-010-INTEREST-001 | ROOT-010-INTEREST-CALCULATION-OWNER | High | Closed | .ralph/runs/2026-07-21_054048_architecture_review/evidence/review-probes/interest-owner-reproducer.log | - | .ralph/runs/2026-07-21_054048_architecture_review/evidence/review-probes/interest-owner-closure.log |
| AR-010-DPD-001 | ROOT-010-DPD-SNAPSHOT-OWNER | High | Carried | .ralph/runs/2026-07-21_054048_architecture_review/evidence/review-probes/dpd-owner.log | 010K3 | - |
| AR-010-REMINDER-001 | ROOT-010-REMINDER-DELIVERY-OWNER | High | Carried | .ralph/runs/2026-07-21_054048_architecture_review/evidence/review-probes/reminder-owner.log | 010K3 | - |
| AR-010-MIS-001 | ROOT-010-MIS-AS-OF-OWNER | High | New | .ralph/runs/2026-07-21_054048_architecture_review/evidence/review-probes/mis-owner.log | 010K3 | - |
| AR-010-SERVICING-SEAM-001 | ROOT-010-SERVICING-OWNER-SEAM | Medium | Carried | .ralph/runs/2026-07-21_054048_architecture_review/evidence/review-probes/servicing-seam.log | - | - |

## Recommended Next Action
Run independent architecture-review validation. On acceptance, execute `010K3` before the existing
010K2 statement/export slice; do not advance servicing consumers across the open as-of boundary.
