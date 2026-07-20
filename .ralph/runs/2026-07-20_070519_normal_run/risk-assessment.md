# Risk Assessment

Risk level: High

- Selected slice: `010F-interest-invoice-generation`
- Mode: `normal_run`
- Standing approval: applicable; no `[revoked]` entry was found for this slice.

## Material risks and controls

- Financial calculation integrity: callers cannot submit principal, rate, period, paid interest,
  tax, fee, or amount. One effective approved configuration and rate snapshot are mandatory; database
  constraints and immutable snapshots protect retained truth.
- Duplicate/concurrency: idempotency-key and loan/period uniqueness are both enforced. The declared
  PostgreSQL race test expects one `200`, one `409`, one invoice, one rate consumption, and one audit.
- Unresolved accounting/ownership: no production default is seeded. Missing benchmark, spread,
  reset, day count, tax/fee, owner roles, or communication template fails closed. A-146 records the
  explicit versioned mechanism.
- Object authority and privacy: generation/issuance require exact permissions, configured owner
  role, and canonical loan scope. Responses/audits omit recipient addresses and borrower contact data.
- Issuance side effects: only drafts issue; one confidential PDF, approved-template communication,
  queued job, actor/time, and audit evidence are bound before status becomes `issued`. No paid-state
  field or transition exists in this slice.
- Residual validation: local SQLite collected but skipped the PostgreSQL-only race as designed. The
  orchestrator must execute the declared test twice on PostgreSQL and run full coverage/migrations.

## Scope assessment

One new backend app and one migration implement only annual invoice generation/list/issue. No
monthly accrual, capitalisation, repayment allocation, frontend, source document, protected file,
dependency, or external delivery behavior changed.
