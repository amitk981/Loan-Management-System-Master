# Review Packet: 2026-07-21_070957_repair

## Result
Ready for independent validation

## Slice
010K3-servicing-as-of-owner-boundary-closure

## Demonstrated failure and correction

Independent coverage failed the bounded active-portfolio DPD API test at 21 queries against a
20-query ceiling. Captured SQL showed the 010K3 capitalisation-owner prefetch was one fixed,
necessary query and not an N+1. The remaining excess was a duplicate calculate-permission lookup
inside `_calculate_locked`: both public callers had already checked the exact calculate permission,
and the locked loan-owner resolver rechecked canonical loan scope.

The repair removes only that duplicate private lookup. It does not relax the query assertion or
remove the capitalisation evidence required by AC-SAO-2.

## Traceability

The source contract says DPD uses schedule and immutable posted ledger truth as of the requested date
(`functional-spec.md` M11-FR-002 and `data-model.md` §35.4). The code retains the dated
capitalisation-evidence prefetch and eliminates only redundant authorization work. This is verified
by `test_bounded_active_portfolio_reports_each_outcome`, the five public servicing owner-boundary
tests, and the DPD payment-timing matrix.

## Evidence reviewed

- Exact failure reproduced: `evidence/terminal-logs/dpd-monitoring-query-red.log`.
- SQL hypothesis probe: `evidence/terminal-logs/dpd-monitoring-query-probe.log`.
- Exact regression green: `evidence/terminal-logs/dpd-monitoring-query-green.log`.
- Five servicing owner-boundary tests green: `evidence/terminal-logs/servicing-asof-focused.log`.
- Eight impacted DPD tests, Django check, and migration sync green:
  `evidence/terminal-logs/repair-focused-gates.log`.
- Semantic closure validator: PASS for three findings and five acceptance IDs.

## Independent validation focus

- Confirm the complete backend coverage suite retains the 20-query result under its worker setup.
- Re-run the declared PostgreSQL five-test class twice and verify no authorization/race regression.
- Confirm no private helper caller exists outside the two public calculate entry points; repository
  search found only those two call sites.
