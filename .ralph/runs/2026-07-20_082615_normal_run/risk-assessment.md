# Risk Assessment

Risk level: High

- Selected slice: `010G-monthly-interest-accrual`
- Mode: `normal_run`
- Standing approval: applicable; no matching revocation was found.
- Independent validation required: yes.

## Financial and data-integrity controls

- The client supplies only loan/month identity. Principal, period, effective rate, calculation
  version/day count, and amount are server-owned decimal snapshots.
- Principal is resolved through a loan-owned as-of seam: original disbursement before the first
  repayment, otherwise the latest immutable repayment/reversal ledger balance on or before month
  end. A later repayment therefore cannot reduce an earlier month retroactively.
- One approved effective-rate version and one approved calculation version are required. Missing or
  ambiguous policy fails before rate-consumption, accrual, audit, or SAP-obligation writes.
- Database uniqueness on `(loan_account, accrual_month)`, transaction locks, immutable calculation
  fields, and idempotency digests defend against duplicate/changed replay and concurrent creation.
- SAP starts honestly pending. Terminal posted/failed evidence requires permission and object scope,
  is atomic with its local obligation/audit, and does not claim external delivery. Free-text remarks
  and the SAP reference are hashed in audit JSON.
- Bulk generation is capped at 100, isolates per-loan outcomes, and has an explicit dry run that
  performs no persistence or audit writes.

## Policy decision and residual risk

- A-147 records the unresolved partial-month policy. Until governance approves proration, a loan
  must be funded by the first day and remain open through month end; otherwise the month fails
  closed. The approved 010F `simple_daily` version supplies method/day-count only; invoice owner,
  tax, fee, document, and communication fields do not affect accrual.
- The as-of seam currently includes disbursement plus the implemented repayment/reversal ledger.
  Future 010H capitalisation must extend this loan-owned seam with its immutable movement rather
  than adding another interest-owned principal source.
- The production migration adds financial rows and constraints, and the same-month race is
  PostgreSQL-sensitive. Local SQLite collected the exact one-test class but skipped it. Ralph must
  run it twice on PostgreSQL before commit.
- Focused/reverse tests, Django check, migration sync, and diff whitespace are green. The complete
  backend coverage suite and repository frontend gates remain the orchestrator's authoritative
  acceptance; they were intentionally not duplicated by the agent.
- No protected/source files, dependencies, frontend files, external services, or real personal or
  financial data were changed or used.
