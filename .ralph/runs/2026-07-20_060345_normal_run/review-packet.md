# Review Packet: 2026-07-20_060345_normal_run

## Result
Ready for independent validation

## Slice
010E3-servicing-financial-owner-and-replay-convergence

## Recommended Next Action
Run Ralph's independent complete backend/coverage gates and the declared five-test PostgreSQL
acceptance twice; commit only if every gate passes.

## Implementation Review

- Allocation replay now returns the §45.2 wrapper around allocation-time response evidence even
  after later repayment status changes; changed/cross-owner keys remain conflicts.
- Subsidiary matching now rejects both competing application references and competing borrower
  identities while preserving the direct-receipt rule.
- Active configuration, rate history, and consumption snapshots reject supported mutations.
  Successor activation checks retained consumption dates before closing an open predecessor.
- Activation advances each active floating loan's current-rate projection, appends one old/new
  history, and replays the frozen activation-time response rather than live notice status.
- Concurrent consumption uniqueness is translated into deterministic replay/domain conflict.
- Ledger reads count in the database and fetch bounded movement windows before deterministic merge.
- The slice-owned PostgreSQL acceptance suite uses a public builder and declares exactly five races.

## Source Traceability

- `functional-spec.md` M09-FR-007 says subsidiary matching requires borrower name and application
  number; the matcher now rejects either competing identity, verified by the ambiguity matrix test.
- `api-contracts.md` §45.2 says duplicate financial keys return the original response in a replay
  wrapper; allocation and activation do so, verified by the replay tests.
- `functional-spec.md` M10-FR-001–002 and `data-model.md` §§18.5/25.3 require effective versions,
  loan history, and borrower notice evidence; activation now produces one coherent immutable chain,
  verified by rate history/projection/replay tests.
- `data-model.md` §34.1 requires atomic repayment allocation; existing atomic financial writes are
  preserved and the read path now pages their append-only movements without materialising history.

## Validation Evidence

- Focused RED/GREEN: `evidence/terminal-logs/*-red.log` and
  `evidence/terminal-logs/financial-owner-focused-green.log`.
- Ledger cardinalities: `evidence/terminal-logs/ledger-cardinality-green.log` — mixed repayment
  and reversal windows at 1, 21, and 101 rows, exit 0.
- Slice-owned suite: `evidence/terminal-logs/servicing-owner-suite.log` — 2 portable tests passed;
  the 5 PostgreSQL-only tests collected and truthfully skipped on SQLite, exit 0.
- Reverse consumers: `evidence/terminal-logs/reverse-consumers.log` — 73 tests, exit 0.
- Backend checks: `evidence/terminal-logs/backend-check-migrations.log` — check and migration sync,
  exit 0.
- PostgreSQL: not claimed locally; independent declared capability remains mandatory.

## Reviewer Focus

- Verify PostgreSQL absent-row consumption races return one exact snapshot and domain conflicts.
- Verify competing successor activation serializes correctly and retains contiguous periods.
- Confirm complete-suite consumers accept the §45.2 replay wrapper for both ordinary and manual
  allocation.
