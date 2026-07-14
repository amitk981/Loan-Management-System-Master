# Ralph Handoff

## Last Run

2026-07-14_225031_normal_run

## Current Status

008I is complete. `security_instruments` owns one CDSL pledge per retained package and the exact
§28.5 POST/GET/PATCH routes. The pledge is available only for canonical frozen `demat` packages;
`physical`, `mixed`, and missing applicability remain fail-closed. Ordinary reads expose masked BO
accounts, while an explicit Company Secretary reveal permission records a separate audit event.

Compliance owns preparation and real pending changes. A distinct Company Secretary records the
terminal accepted/rejected result only with retained PSN, SFPCL pledgee identity, active sanctioned
borrower demat holding, source-required future-shares obligation, and genuine current-renderer
same-application evidence. Acceptance freezes its evidence and returns one durable action. Exact
replays are zero-write. Invocation, unpledge, balance changes, checklist completion, package
readiness, file authority, and loan-account creation remain excluded.

Checklist/package reads project pledge milestones without changing earlier PoA/tri-party/SH-4 or
completion-owned facts. 008K was sharpened from source material without implementation; 008J was
already concrete. Four slices have completed since the last architecture review, so review is due.

## Validation

Evidence is in `.ralph/runs/2026-07-14_225031_normal_run/evidence/`: four retained TDD red/green
cycles, focused and impacted suites, two successful executions of both PostgreSQL five-worker race
contracts, Django check/migration sync, 826 backend tests with 36 expected SQLite skips at 92%
coverage, and frontend build/typecheck/lint plus 293 tests.

## Next Run

Run the due architecture review. If it produces no corrective priority, run 008J blank-cheque
custody. Preserve the security-package lock, current renderer/evidence selectors, package/checklist
truth, and strict exclusion of invocation/disbursement authority. A-101 still blocks a complete real
Term-Sheet path.
