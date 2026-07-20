# Review Packet: 2026-07-20_124034_normal_run

## Result
Ready for independent validation

## Slice
010E4-rate-effective-date-and-write-boundary-closure

## Recommended Next Action
Run the orchestrator's independent protected-path, migration, complete backend coverage, and exact
PostgreSQL capability gates; commit and merge only if all remain green.

## Scope Reviewed

- Added coherent approval-evidence database admission and complete standard ORM write guards.
- Kept future-effective activation out of the mutable loan current-rate projection.
- Added an explicit-date, audited, idempotent convergence facade and date-bounded loan read selectors.
- Removed changed loan/interest consumers' private configuration-model imports.
- Replaced cross-`TestCase` rate fixtures with public builders and added the exact four-test trusted
  PostgreSQL acceptance class.

## Traceability

The source says floating rates must retain versions/effective dates and borrower communication
(`functional-spec.md` M10-FR-001–002, BR-064–065), configuration-dependent calculations must retain
the selected version (`codebase-design.md` §38.2), and financial modules require idempotency and
concurrency tests (§26.3). The code now admits an active row only with coherent canonical approval
evidence, resolves rates for an explicit date, leaves a future rate unpublished until due, and lets
interest/loan consumers cross one public configuration facade. This is verified by
`RateEffectiveDatePostgreSQLAcceptanceTests` (four tests, twice on PostgreSQL), the focused API/consumer
suite, and the static migration gates.

## Evidence

- TDD RED/GREEN: `evidence/terminal-logs/ac-rate-*-red.log` and
  `evidence/terminal-logs/ac-rate-*-green.log`
- Exact PostgreSQL acceptance twice: `evidence/terminal-logs/postgresql-acceptance-run-1.log` and
  `evidence/terminal-logs/postgresql-acceptance-run-2.log`
- Prior PostgreSQL owner regressions: `evidence/terminal-logs/postgresql-reverse-owner-tests.log`
- Focused API/loan/invoice/accrual tests: `evidence/terminal-logs/reverse-consumers-focused-green.log`
- Public-builder regression: `evidence/terminal-logs/rate-api-public-builders-green.log`
- Check/migration/compile: `evidence/terminal-logs/backend-static-gates.log` and
  `evidence/terminal-logs/backend-compile.log`

## Independent Review Notes

- Confirm the migration constraint accepts every retained canonical active row in the independent
  migrated database.
- Confirm the runtime capability discovers exactly four tests and executes the class twice.
- Full backend suite and coverage were intentionally not run by the agent; Ralph owns that gate.
