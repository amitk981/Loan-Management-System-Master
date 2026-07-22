# Review Packet: 2026-07-22_201550_repair

## Result
Ready for independent validation

## Slice
011G-closure-readiness

## Demonstrated failure and repair

- Ralph's complete backend coverage lane found one failure: a bounded DPD bulk calculation executed 23 queries
  where its regression contract permits no more than 20.
- The exact failing test reproduced the same `23 not less than or equal to 20` symptom before any repair.
- Query tracing showed that 011G's generic closed-account update guard redundantly opened a savepoint and reread
  state during the DPD pointer update, even though the DPD owner had already locked and re-authorised that account.
- A narrow, conditional pointer-update method now performs the same update in one statement and refuses closed
  rows in SQL. The DPD transaction also requires one updated row or fails and rolls back.

## Traceability

- `product-requirements.md` §11.28 and `test-plan.md` `MOD-CLOSURE-010` say closed loan records are read-only.
  The code keeps the generic closed mutation guard intact and gives the locked DPD owner only a pointer-specific,
  closed-conditional update seam.
- The DPD query-budget regression exercises the real bulk-calculation call path. It was RED before the repair and
  GREEN after it; see `evidence/terminal-logs/01-dpd-query-budget-red.log` and
  `evidence/terminal-logs/04-dpd-query-budget-green.log`.
- The code does not invent a new closure rule: it preserves the source rule while removing only redundant query
  mechanics from an already-authorised servicing update.

## Validation status

- Exact failed test: 1/1 passed after repair.
- Entire DPD monitoring API module: 9/9 passed.
- Closure API and direct repayment reverse consumers: 15/15 passed.
- Django system check: passed.
- Migration consistency: passed, no changes detected.
- Whitespace check and debug-instrumentation cleanup: passed.
- Authoritative complete backend coverage and declared PostgreSQL acceptance: pending Ralph's independent
  validator, as required by the repair prompt.

## Recommended Next Action

Run Ralph's full independent revalidation of the preserved candidate, including complete backend coverage and
the declared PostgreSQL closure-race acceptance.
