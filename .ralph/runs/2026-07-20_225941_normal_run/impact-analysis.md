# Impact Analysis

## Affected Backend Pieces

- `interest.models.InterestInvoiceConfiguration`: approval lifecycle, immutable approved policy,
  explicit monetary rounding fields, and database constraints.
- `interest.modules.as_of_accounting`: unrounded segmented calculation and one approved rounding
  boundary shared by invoice and accrual callers.
- `interest.modules.interest_engine`: approved-policy resolution/snapshots and pre-write
  capitalisation reconciliation across invoice, account, schedule, payment, ledger, and principal.
- `interest` migration: additive approved-policy/rounding schema and integrity constraints.

## Affected Consumers and Blast Radius

- Annual invoice generation and monthly accrual generation consume the calculation decision; their
  historical snapshots and idempotent original responses must remain immutable.
- Capitalisation touches loan balances, repayment schedules, interest invoices/payment evidence,
  capitalisation evidence/ledger, communications, document/task, and audit rows in one transaction.
- Existing rate-version ownership remains in `configurations`; no rate semantics or rate approval
  transition changes are in scope.
- No frontend route, API request shape, permission code, or external provider contract changes.

## Regression Tests

- Interest owner closure tests: approved policy rejects instance/queryset/bulk/delete mutation before
  consumption; separate approved amendments remain usable and historical calculations retain version.
- Calculation tests: leap, partial-period, multi-segment, and half-unit cases use configured rounding
  exactly once; missing/unsupported rounding fails before invoice/accrual monetary writes.
- Capitalisation tests: exact reconciled matrices move the same interest into principal everywhere;
  account/schedule/payment mismatches leave all financial and operational owners unchanged.
- Replay/race tests: exact replay returns byte-stable original evidence; changed-key and competing
  requests retain one principal increment and one ledger decision.
- PostgreSQL acceptance: the exact declared five-test class covers mutation/database enforcement,
  rounding/reconciliation behavior, and exact/changed-key race outcomes.
