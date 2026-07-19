# Review Packet: 2026-07-19_230254_normal_run

## Result
Ready for independent validation

## Slice
010C-principal-first-allocation

## Outcome

Principal-first repayment allocation is implemented as a deep backend module with one public
interface. One transaction owns locking, coherent capture validation, waterfall calculation,
schedule/account updates, immutable allocation/audit/ledger writes, and exact replay. The TDD and
codebase-design skills directly shaped this public-interface test surface and concentrated the
financial rules behind the allocator seam.

## Source Traceability

- Product requirements §11.23 and functional spec BR-056/§11.9 say partial repayment reduces
  principal before interest. `RepaymentAllocator` applies those exact minima; verified by
  `test_partial_receipt_reduces_principal_and_appends_immutable_evidence` and
  `test_crossing_receipt_updates_schedule_then_retains_charges_and_excess`.
- Data model §§19.6/35.2 require explicit allocations and no unconfigured charge allocation. The
  migration stores before/after principal, interest, charges, total, rule/version, actor, timestamp,
  exception remainder, and one linked ledger row; verified by the crossing and database tests.
- API §32.4 defines the allocation endpoint and codebase design §17.2 defines the allocator seam.
  The route and response are documented in `docs/working/API_CONTRACTS.md`; verified through the
  HTTP interface by all six allocation tests.
- Security §22.2 requires positive captured receipts, duplicate prevention, principal-first, SAP
  preservation, and audit. 010B's positive constraint remains, capture evidence is reconciled,
  exact replay creates no second effect, SAP truth is unchanged, and one safe audit is retained.
- Test plan MOD-REP-006–008, FIN-REP-001–005, and E2E-011 are covered by the calculation matrix,
  payoff/replay, zero-write denial, database, ledger, and Epic 009/010A/010B regression tests.

## Evidence

- RED/GREEN tracer: `evidence/terminal-logs/010C-red-tracer.log` and
  `evidence/terminal-logs/010C-green-tracer.log`.
- RED/GREEN crossing, capture integrity, and database constraints: matching `010C-red-*` and
  `010C-green-*` terminal logs.
- Final focused allocation run: `evidence/terminal-logs/010C-allocation-green.log` (6 passed).
- Reverse consumers: `010C-reverse-010A-010B.log` (15 passed) and
  `010C-reverse-009-and-checks.log` (2 passed, checks clean, one PostgreSQL test collected/skipped).
- Before/after examples: `evidence/allocation-matrix.md`.

## Review Focus

- Confirm A-139's oldest-installment-first default is acceptable pending source governance.
- Run the declared five-way race twice on PostgreSQL and verify one allocation, balance transition,
  ledger entry, and audit.
- Confirm independent migration/coverage gates and inspect that append-only evidence constraints
  behave identically on PostgreSQL.

## Substantive Risks and Decisions

- High financial-integrity risk is controlled but still requires the independent PostgreSQL gate.
- No approved charge waterfall exists; any charge-facing or excess amount stays explicit and never
  becomes a charge allocation or ledger credit.
- Exact replay returns the retained allocation projection with no replay wrapper because source
  §32.4 defines no idempotency header/response wrapper for this action; the singular retained result
  and financial effect are invariant.

## Recommended Next Action

Run Ralph's independent complete backend coverage, migration, protected-path, diff-limit, and twice-
run PostgreSQL contention validation. The orchestrator may commit only if all gates pass.
