# Impact Analysis

## Affected modules

- `monitoring`: DPD snapshot/policy integrity, reminder coordination, quarterly MIS snapshots and
  transition replay authorization.
- `loans`: immutable DPD schedule source decisions, including repayment/reversal and interest
  capitalisation reclassification evidence.
- `communications`: final delivery preflight seam used by reminder jobs before provider invocation.
- Database: one migration for snapshot-side DPD and operational-policy protections plus any retained
  cutoff metadata required by the owner boundary.

## Blast radius

- Existing DPD calculate/read and bulk-calculate responses must remain compatible.
- Existing communication jobs not owned by reminders must dispatch unchanged.
- Existing MIS generation/list/detail/export and draft/submitted/reviewed transitions retain response
  shape and exact replay semantics, but replay is no longer authorization.
- Repayment, reversal, invoice, accrual, capitalisation, and disbursement owners remain authoritative;
  this slice consumes their immutable evidence without changing their write contracts.

## Regression tests

- DPD: instance/queryset/bulk/direct-SQL/reparent/delete integrity, policy amendment immutability,
  capitalisation classification, and repayment/reversal date matrix.
- Reminders/communications: provider-boundary adverse races, exact retry once-only behavior, and
  1/100/101 batch identity plus continuation outcomes.
- MIS: current-scope replay checks for generate/submit/review, exact submitted-CFO authority,
  late-created row exclusion, retained response stability, and exact/changed-key concurrency.
- PostgreSQL: one declared five-test class covering the cross-owner race and database-only contracts.
