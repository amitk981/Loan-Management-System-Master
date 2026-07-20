# Risk Assessment

Risk level: Medium

- Selected slice: 010I-dpd-calculation-and-monitoring-buckets
- Mode: normal_run
- Manual review required: independent Ralph validation only.

## Material risks and controls

- Financial/as-of correctness: DPD uses immutable schedule dues plus allocation and reversal ledger
  transaction dates, not mutable current paid totals. The payment-timing test proves a later posted
  receipt cannot reduce an earlier snapshot.
- Historical integrity: `(loan_account, as_of_date)` is database-unique, snapshots are append-only,
  exact replay is zero-write, and an older replay cannot regress the current pointer.
- Contention: account row locking plus the unique constraint retained one snapshot and one audit in
  two independent real-PostgreSQL same-date race runs.
- Policy ambiguity: calendar anniversary inclusivity and leap-day handling are isolated in A-148 and
  covered at the day before/on/after each threshold. Optional standard buckets require one effective
  30/60/90 scheme; no scheme is silently seeded.
- Authorization: writes require `monitoring.dpd.calculate`, reads require
  `monitoring.dpd.read`, and both reuse canonical account scope. Portfolio input is capped at 100.
- Workflow blast radius: calculation writes snapshots, account pointer, and audit evidence only. The
  focused test proves no workflow event or loan-status transition is introduced; reminders/defaults
  remain outside this slice.

## Residual risk

Governance still needs to confirm A-148 and provision an effective operational scheme if standard
management buckets are wanted. The orchestrator remains responsible for the complete backend
coverage gate and two declared PostgreSQL acceptance executions during independent validation.
