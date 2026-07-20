# Execution Plan

Selected slice: 010E3-servicing-financial-owner-and-replay-convergence

## Boundary and impact map

- Allocation owner: freeze the original public allocation response at the idempotency seam and
  reject changed/cross-receipt key reuse before writes.
- Statement owner: make subsidiary borrower/application ambiguity checks symmetric without changing
  direct-receipt matching rules.
- Rate configuration owner: enforce append-only active/consumed versions, predecessor consumption
  coverage, canonical effective-date resolution, coherent loan/history fan-out, frozen activation
  replay, and domain-level concurrent consumption conflicts.
- Ledger read owner: replace Python full-history materialisation with database count/window reads
  while preserving the existing response and deterministic mixed-movement ordering.
- Test seam: introduce/reuse public servicing builders so acceptance and PostgreSQL tests do not
  invoke another TestCase's setup or private helpers.
- Database impact: at most one migration for frozen response evidence or strengthened immutable
  state; preserve historical values and use explicit legacy-safe defaults where required.
- API impact: preserve existing endpoints and wrappers; document only response/error semantics that
  materially change.

## TDD sequence

1. Inspect the public owner interfaces, migrations, existing focused tests, and cited source
   contracts; map each AC-FIN selector to one permanent test.
2. Add one public failing replay test for allocation, retain RED output, implement the smallest
   frozen-response owner change, and retain GREEN output.
3. Add the subsidiary ambiguity matrix through the public match endpoint, capture RED, implement
   symmetric borrower/application rejection, and capture GREEN.
4. Add focused public/model/queryset/service rate immutability, predecessor-consumption,
   projection/history, activation-replay, and concurrent-consumption tests as vertical red/green
   cycles; add a migration only if persistence is necessary.
5. Add ledger cardinality/order tests at 1/21/101 mixed rows, capture RED, move count/window work to
   database queries, and capture GREEN.
6. Replace cross-TestCase/private fixture construction in the changed acceptance/PostgreSQL suites
   with public builders/facades and run the exact five-test PostgreSQL label twice when available.
7. Run reverse-consumer focused suites, Django check, migration sync, and applicable lint/format
   checks. Do not run the complete backend suite or coverage locally; the orchestrator owns it.
8. Save review-closure-evidence.md, risk-assessment.md, review-packet.md, and final-summary.md with
   exact AC/finding traceability and evidence paths; finish with the required validation-ready result.

## Risk controls

- Financial and rate-history changes are append-only and transactional; no historical amount or
  consumed snapshot is rewritten.
- PostgreSQL races are authoritative for locking/uniqueness promises; SQLite feedback is not cited
  as concurrency proof.
- Existing public wrappers, permissions, object scope, direct-receipt matching, and communication
  provider semantics remain unchanged outside the selected closure criteria.
- Stop if implementation cannot fit the configured 30-file/2,000-line/one-migration limits rather
  than silently broadening the slice.
