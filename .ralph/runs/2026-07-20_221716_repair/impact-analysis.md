# Impact Analysis

## Demonstrated Failure

Both independent PostgreSQL acceptance runs execute all five declared tests and fail only
`test_competing_portfolio_runs_keep_stale_account_visible_and_singular`: after concurrent bounded
portfolio convergence, the Loan Account collection reports one visible account instead of two.

## Affected Pieces

- Backend current-date rate publication/convergence in
  `configurations.modules.interest_rate_configuration`.
- Loan-owned current-rate projection facade and Loan Account 360 collection assembly, only if the
  minimized repro shows the missing row is caused at either boundary.
- The existing PostgreSQL acceptance class and focused public-seam tests in
  `test_servicing_financial_owner_closure.py`.

## Blast Radius

- Financial integrity: a due current-rate publication must remain singular and replay-safe under
  concurrent owner runs.
- Read integrity: an account with stale scalar projection must remain present in collection count,
  rows, and detail while convergence occurs.
- Reverse consumers: invoice, accrual, and capitalisation rate selection must remain unchanged.
- No frontend, API schema, interest arithmetic, schedule cadence, or historical-consumption rewrite
  is in scope.

## Regression Coverage

- Retain the exact five-test trusted PostgreSQL class as the primary RED/GREEN signal.
- Keep the competing portfolio assertion on both account visibility and singular decision effects.
- Rerun focused current-date matrix, replay/permission, collection, and reverse-interest consumer
  tests after the repair.
