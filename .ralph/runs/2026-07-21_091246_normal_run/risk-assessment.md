# Risk Assessment

Risk level: High

- Selected slice: 010L-member-portal-repayment-view
- Mode: normal_run
- Manual review required: independent Ralph validation and trusted browser acceptance.

## Material risks and controls

- Cross-member financial disclosure: every projection resolves the member from one active portal
  account, scopes the account before nested reads, rejects caller member identity, and uses a common
  nondisclosing `404` for guessed and actual foreign accounts. The permanent backend matrix covers
  detail, schedule, repayment, invoice, and instruction routes plus staff and suspended principals.
- False repayment confirmation: history is sourced only from canonical SAP-posted allocations in
  terminal allocated states. Pending internal receipts and reversed receipts are excluded; the UI
  has no `Under verification` state because proof submission is not approved.
- Bank-detail leakage or false authority: account numbers expose last four only. Instructions fail
  closed unless a complete runtime value is explicitly marked approved; the unverified statement
  label and outgoing disbursement source-bank registry are not reused.
- Client financial drift: MP15-MP18 format backend decimal strings but do not calculate balances,
  allocation, status, next due, invoice amounts, or permissions. Account selection is explicit and
  retained by the borrower portal parent.
- Frontend regression/visual drift: the implementation reuses existing portal alerts, cards, tables,
  badges, spacing, colours, and typography. Full frontend tests, typecheck, lint, and build passed.
- Browser evidence: Playwright collection passed for all four declared cases. A local execution
  reached both servers but Chromium aborted under sandbox macOS process restrictions; the retained
  log is honest and no screenshot was fabricated. The independent trusted browser gate runs twice
  outside the sandbox and remains authoritative.

## Residual decisions

- Production direct repayment instructions remain unavailable until governance provisions and marks
  a complete `PORTAL_REPAYMENT_INSTRUCTIONS` value approved. This is recorded as A-151.
- Borrower UTR/proof submission remains disabled, matching the unresolved source policy.

## Gate summary

- New portal backend tests: 3 passed.
- Focused backend and reverse-consumer regressions: 62 passed.
- Django check and migration sync: passed; no migration required.
- Frontend focused tests: 14 passed; complete suite: 362 passed.
- Frontend typecheck, lint, and build: passed.
- Browser contract collection: 4 tests collected; local launch blocked as described above.
