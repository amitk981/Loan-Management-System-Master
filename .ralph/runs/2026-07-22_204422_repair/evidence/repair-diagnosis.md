# Repair Diagnosis Evidence

## Demonstrated failure

Ralph's complete backend coverage validator failed in
`sfpcl_credit.tests.test_credit_model_ownership_migration` because the test's historical applications registry
could not resolve `EligibilityAssessment`. The focused module reproduced the exact failure before repair: both
forward and reverse tests errored in fixture setup with `LookupError`. See
`terminal-logs/01-credit-ownership-migration-red.log`.

## Root cause

The 011G candidate adds `closure.0001_initial` as a new migration-graph leaf. Three older ownership/backfill tests
construct historical registries by starting from every current leaf except explicitly listed downstream owners.
Because `closure` was not yet listed, its dependency path through current loans and application state outran each
database schema that the test had deliberately migrated backwards:

- credit ownership projected the post-move `credit` models instead of the pre-move `applications` models;
- witness backfill projected fields added after applications 0011 against the applications 0011 table;
- SAP ownership projected the SAP-owned state while the database was still at the finance-owned state.

The graph probe proved the causal edge without changing code: `closure.0001` reaches `credit.0001`; the existing
target set lacks the applications model, and removing only the closure leaf restores the applications model while
keeping the credit model absent. See `terminal-logs/02-migration-graph-probe.log`.

## Minimal repair

Added `closure` to the downstream-owner exclusions in the credit, witness, and SAP historical migration-state
constructors. SAP excludes it in both its initial and reversed historical projections. Migration targets,
production migrations, fixtures, and behavioral assertions remain unchanged.

## Feedback loop

| Phase | Scope | Result | Evidence |
| --- | --- | --- | --- |
| RED | Credit ownership migration module | 0/2; exact missing `EligibilityAssessment` failure reproduced | `terminal-logs/01-credit-ownership-migration-red.log` |
| Probe | Migration graph and projected registry | Closure path reached credit move; excluding closure restored the intended old state | `terminal-logs/02-migration-graph-probe.log` |
| GREEN | Credit ownership migration module | 2/2 passed | `terminal-logs/03-credit-ownership-migration-green.log` |
| Subsequent RED | Witness and SAP historical migration modules | 4 setup errors exposed from the same closure-leaf contamination | `terminal-logs/04-related-historical-migrations-red.log` |
| Subsequent GREEN | Witness and SAP historical migration modules | 7/7 passed | `terminal-logs/05-related-historical-migrations-green.log` |
| Static | Django check, migration consistency, whitespace/debug cleanup | Passed; no model changes detected | `terminal-logs/06-static-checks-green.log` |

The authoritative complete backend coverage lane is intentionally left to Ralph's independent validator, as the
repair prompt forbids the agent from running that complete lane itself.
