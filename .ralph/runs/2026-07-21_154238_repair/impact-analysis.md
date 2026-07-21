# Impact Analysis

## Demonstrated Failure

The independent complete backend gate failed
`sfpcl_credit.tests.test_dpd_monitoring_api.DpdMonitoringApiTests.test_bounded_active_portfolio_reports_each_outcome`
because the include-all-active bulk DPD request executed 21 queries against a bound of 20.

## Affected Backend Pieces

- `sfpcl_credit/monitoring/modules/dpd_monitoring.py`: bulk portfolio selection and per-account outcome classification.
- `sfpcl_credit/loans/modules/dpd_source_decision.py`: inspected but intentionally preserved; CR-015's separate account lock and post-lock scope authorization is binding owner-boundary behavior.
- `sfpcl_credit/tests/test_dpd_monitoring_api.py`: existing permanent query-budget and outcome regression provides the exact repair signal; no test weakening is permitted.

## Frontend Impact

None. The public bulk-DPD response and frontend contracts do not change.

## Blast Radius

The edit is limited to the include-all-active branch. Explicit account-ID requests retain their existing inaccessible/closed-account outcome classification. Locked calculation, DPD amounts, snapshot persistence, audit output, permissions, and API envelopes remain unchanged.

## Regression Tests

- Exact RED/GREEN: `sfpcl_credit.tests.test_dpd_monitoring_api.DpdMonitoringApiTests.test_bounded_active_portfolio_reports_each_outcome`.
- Affected module: `sfpcl_credit.tests.test_dpd_monitoring_api`.
- The orchestrator reruns the authoritative complete backend suite and coverage after the bounded repair.
