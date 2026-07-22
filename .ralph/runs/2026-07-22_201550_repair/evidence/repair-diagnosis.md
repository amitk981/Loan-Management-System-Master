# Repair Diagnosis Evidence

## Demonstrated failure

Ralph's complete backend coverage validator failed only at
`sfpcl_credit.tests.test_dpd_monitoring_api.DpdMonitoringApiTests.test_bounded_active_portfolio_reports_each_outcome`.
The endpoint remained functionally correct, but the request executed 23 queries against an established ceiling
of 20.

The exact test was reproduced unchanged before the repair. It failed deterministically with
`AssertionError: 23 not less than or equal to 20`; see
`terminal-logs/01-dpd-query-budget-red.log`.

## Root cause

Slice 011G added a generic `LoanAccountQuerySet.update()` guard that locks and reads target account state before
allowing an update, so direct mutations of closed accounts fail closed. The DPD calculation owner already locks
the account, re-authorises its scope, and confirms a serviceable status inside `_calculate_locked()`. Its final
current-DPD pointer update nevertheless passed through the generic guard a second time.

The targeted query trace proved that this redundant guard contributed exactly three over-budget statements:
a nested savepoint, a second `loan_account_status`/`closed_at` query, and the savepoint release. The pointer
`UPDATE` itself was already part of the original bounded path. See
`terminal-logs/03-dpd-query-instrumented.log`.

## Minimal repair

- Added `LoanAccountQuerySet.update_current_dpd_status_if_open()`, a narrow pointer-only update that embeds
  `closed_at IS NULL` and non-`closed` predicates in the single SQL update.
- Changed the locked DPD owner to use that seam and require exactly one updated row. A zero-row result raises
  `DpdConflict`, so a closed/ineligible account cannot retain the newly created snapshot; the surrounding atomic
  transaction rolls the calculation back.
- The generic closed-account guard remains unchanged for every ordinary queryset update/delete and instance save.
- Temporary `[DEBUG-dpd-q23]` instrumentation was removed; no debug marker remains in product or test code.

## Feedback loop

| Phase | Exact scope | Result | Evidence |
| --- | --- | --- | --- |
| RED | Named failing DPD query-budget test | Reproduced 23 queries against the `<= 20` contract | `terminal-logs/01-dpd-query-budget-red.log` |
| Probe | Same named test with targeted query summaries | Identified the redundant savepoint/state-read/release at queries 18, 19, and 21 | `terminal-logs/03-dpd-query-instrumented.log` |
| GREEN | Named failing DPD query-budget test | 1/1 passed | `terminal-logs/04-dpd-query-budget-green.log` |
| Regression | Entire DPD monitoring API module | 9/9 passed | `terminal-logs/05-dpd-monitoring-focused-green.log` |
| Reverse consumers | Closure API and direct repayment API modules | 15/15 passed | `terminal-logs/06-closure-repayment-reverse-consumers-green.log` |
| Static | Django check and migration consistency | Passed; no model changes detected | `terminal-logs/07-backend-static-checks-green.log` |

The complete backend suite and coverage floor are intentionally left to Ralph's independent validator, as the
repair prompt forbids the agent from running that authoritative lane itself.
