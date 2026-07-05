# Risk Assessment — 003G Dashboard Task Summary API

## Risk Level
Medium.

## Why
- Adds a new authenticated backend API endpoint.
- Adds and seeds the `management_readonly` permission scope for dashboard summary access.
- Changes the local/demo zero-permission account from `management_viewer` to `it_head` because
  `management_viewer` now has source-backed dashboard summary access.

## Controls
- TDD red/green evidence saved for the dashboard API and catalogue seed.
- Endpoint requires session-bound bearer auth and `management_readonly`.
- Tests cover missing bearer token, revoked token, authenticated no-permission user, unknown query
  parameter validation, supported role contexts, no audit write on read, and no sensitive
  borrower/member/loan-account fields.
- No database models or migrations were added.
- No frontend code was changed.
- Protected files and `docs/source/**` were not modified.

## Residual Risk
- Dashboard card counts are intentionally zero until downstream lending/compliance/treasury modules
  exist. This is documented in A-023 and `API_CONTRACTS.md`.
- If source docs later add exact dashboard permission codes or role-specific scopes,
  `management_readonly` should be replaced or narrowed.
