# Review Packet: 2026-07-20_194456_architecture_review

## Result
Ready for independent validation

## Slice
architecture-review

## Scope

- Fixed point: successful architecture-review commit
  `016a3a893fbbda1a3d32ca5daa4b36e4da40e212`.
- Product commits: `28f8e19d` (010E4), `600e9742` (010H2), `c6175bf3` (010I), and
  `b7e802ff` (010J). Intervening/later Ralph-orchestration commits were excluded from the product
  critique.
- Active inherited roots: `ROOT-010-RATE-VERSION-OWNER` at generation 2 via 010E4 and
  `ROOT-010-INTEREST-CALCULATION-OWNER` at generation 1 via 010H2.
- Review-only candidate: no production code, migrations, frontend, source, protected, state,
  progress, or mechanical handoff changes.

## Standards Review

- High: 010E4's current-rate convergence facade accepts a future caller-controlled date and has no
  production due-date caller. The projection can therefore publish early or remain stale after the
  effective date, with collection/scalar disagreement.
- High: the interest owner applies a hard-coded per-segment `ROUND_HALF_UP` without an approved
  rounding policy or boundary.
- High: `LoanAccount.current_dpd_status_id` remains an unconstrained UUID rather than the binding
  foreign key required by the data model.
- High: reminder send exposes a communications changed-key exception beyond the reminder API's
  conflict handler.
- Medium: DPD/reminder owners directly consume private loan and communication models rather than
  public owner decisions.
- Low: changed PostgreSQL/long-lived tests still construct other `TestCase` fixtures and call
  private setup helpers.

The independent Standards report is retained at
`.ralph/runs/2026-07-20_194456_architecture_review/evidence/review-probes/standards-axis.md`.

## Spec Review

- High: approved `InterestInvoiceConfiguration` remains mutable/deletable before first consumption,
  contrary to 010H2 AC-INT-6.
- High: capitalisation can add full unpaid invoice interest to principal while subtracting only
  available account/schedule interest, rather than reconciling exactly or failing zero-write under
  AC-INT-4.
- High: 010J uses a fixed 365-day threshold instead of the binding calendar-anniversary decision,
  allowing an early reminder across leap-year spans.
- Medium: a later still-overdue DPD pointer can invalidate retained quarter eligibility.
- Medium: a late portfolio contact/template failure can hide earlier committed reminder rows behind
  one request-level error.

The independent Spec report is retained at
`.ralph/runs/2026-07-20_194456_architecture_review/evidence/review-probes/spec-axis.md`.
The axes remain independently ranked. Their related symptoms are grouped only for corrective
ownership: the standards Low is carried by the existing Medium servicing-seam root, not relabelled
as a new Low finding.

## Owner-Level Disposition

- `AR-010-RATE-001` is Carried High. Generation 2 recurs, so `CR-014` is the root's one permitted
  terminal Architecture Review Finalizer. It owns current-date enforcement, production invocation,
  collection/consumer equivalence, and races. No further terminal or numeric successor is admitted.
- `AR-010-INTEREST-001` is Carried High. `010H3` is its one ordinary successor after generation 1,
  grouping approval-time immutability, approved rounding/fail-closed behavior, and atomic financial
  reconciliation.
- `AR-010-DPD-001` is New High. `010I2` groups the data-model FK contract, validated backfill,
  frozen policy/input evidence, public owner reads, and pointer races.
- `AR-010-REMINDER-001` is New High. `010J2` groups calendar eligibility, execution-time
  serviceability, conflict translation, honest batch results, and public communications ownership.
- `AR-010-SERVICING-SEAM-001` remains Carried Medium. The four High corrections close their changed
  seams; complete older seam removal stays with Epic 010 closure and creates no leaf slice.
- `AR-010-LEDGER-001` remains Carried Medium and was not reproduced or changed by this bounded diff.

## Focused Evidence

Four one-test review probes ran with
`/Users/amitkallapa/LMS/.ralph/venv/bin/python` and failed on their intended assertions:

- premature future-rate convergence: 1 test, 1 failure, exit 1;
- approved interest configuration mutation: 1 test, 1 failure, exit 1;
- dangling current DPD UUID: 1 test, 1 failure, exit 1;
- reminder changed-key HTTP contract: 1 test, 1 uncaught error, exit 1.

The self-contained commands, output, Finding IDs, Root IDs, and static owner checks are under
`.ralph/runs/2026-07-20_194456_architecture_review/evidence/review-probes/`. These are review RED
signals, not implementation gates; the corrective slices own conversion to permanent RED/GREEN
regressions. The architecture-review candidate is documentation-only, so no complete backend suite,
coverage, frontend, or browser gate was duplicated.

Ralph's read-only manifest, convergence-transition, corrective-count, finalizer-contract,
architecture-scope, admission, and whitespace preflights all pass. The retained output is
`.ralph/runs/2026-07-20_194456_architecture_review/evidence/terminal-logs/review-validation.log`.

## Source and Coverage Audit

- M10-FR-001–011 have implemented rate, invoice, accrual, payment, capitalisation, SAP/document,
  communication, and evidence owners, but M10 correctness remains conditional on `CR-014` and
  `010H3`; this review does not silently mark the module complete.
- M11-FR-001–004/006/007 have implemented DPD/reminder foundations, but their binding relational,
  calendar, replay, and delivery truth remains conditional on `010I2`/`010J2`.
- M11-FR-005/008 are explicitly queued in `010K`; later default integration and remaining
  reporting/UI/portal capabilities stay in their named Epic 010/011 successors. No source
  requirement was silently dropped.
- `docs/working/CONTEXT.md` now truthfully names the implemented Epic 010 foundations and the four
  active owner closures. No slice is Blocked, so no prerequisite required re-parking.
- No ADR was added because the review rejects implementation drift against existing source/data/
  owner contracts rather than accepting a new durable decision.

## Convergence Metrics

- Findings closed: 0
- New Critical: 0
- New High: 2
- New Medium: 0
- New Low: 0
- Corrective slices added: 4

The prior review closed 2 findings and added 2 correctives. Additions therefore have not exceeded
closures across two consecutive reviews; the root-cause boundary-correction recommendation trigger
is not met. The capped rate root is handled by its single terminal finalizer under the standing
policy.

## Finding Closure Manifest

| Finding ID | Root ID | Severity | Disposition | Reproducer | Corrective Slice | Closure Evidence |
|---|---|---|---|---|---|---|
| AR-010-RATE-001 | ROOT-010-RATE-VERSION-OWNER | High | Carried | .ralph/runs/2026-07-20_194456_architecture_review/evidence/review-probes/rate-current-date.log | CR-014 | - |
| AR-010-INTEREST-001 | ROOT-010-INTEREST-CALCULATION-OWNER | High | Carried | .ralph/runs/2026-07-20_194456_architecture_review/evidence/review-probes/interest-owner.log | 010H3 | - |
| AR-010-DPD-001 | ROOT-010-DPD-SNAPSHOT-OWNER | High | New | .ralph/runs/2026-07-20_194456_architecture_review/evidence/review-probes/dpd-owner.log | 010I2 | - |
| AR-010-REMINDER-001 | ROOT-010-REMINDER-DELIVERY-OWNER | High | New | .ralph/runs/2026-07-20_194456_architecture_review/evidence/review-probes/reminder-owner.log | 010J2 | - |
| AR-010-SERVICING-SEAM-001 | ROOT-010-SERVICING-OWNER-SEAM | Medium | Carried | .ralph/runs/2026-07-20_194456_architecture_review/evidence/review-probes/servicing-seam.log | - | - |

## Recommended Next Action

Run independent architecture-review validation. On acceptance, execute the dependency-ordered
corrective queue beginning with the terminal `CR-014`; do not proceed to 010K until 010J2 is green.
