# Risk Assessment

Risk level: High

- Selected slice: 010I2-dpd-pointer-and-policy-integrity-closure
- Mode: normal_run
- Manual review required: independent Ralph validation and owner review before promotion to `main`.

## Material risks and controls

- **Schema/data integrity:** the migration changes a UUID projection into a protected relationship
  and adds immediate database owner guards. It validates every non-null legacy pointer first and
  fails closed on dangling/cross-loan data. Coherent values retain the same database column and are
  not recalculated.
- **Historical meaning:** legacy and new snapshots freeze the SOP boundary convention, optional
  operational scheme identity/version/dates/bounds, and source inputs in append-only JSON. The
  backfill adds provenance only; it does not alter amounts, dates, buckets, or DPD.
- **Concurrency:** current-pointer advancement and source decisions execute under the canonical
  loan row lock. Two isolated PostgreSQL runs each passed the exact five-test race matrix.
- **Authorization:** calculation permission is rechecked inside the transaction and the public
  loan-owner decision reapplies canonical object scope as part of the locked query.
- **Consumer compatibility:** the database column and `current_dpd_status_id` attribute remain
  stable; API additions are additive. Focused DPD and reminder-consumer tests passed together.
- **Operational-policy ambiguity:** absence of an operational scheme remains optional under
  M11-FR-004; an effective non-active scheme fails closed. This is recorded as A-150.

## Rollback and recovery

- Migration reversal drops the immediate guards and returns model state/database type to the
  nullable UUID field; frozen JSON additions are intentionally retained because removing audit
  provenance would be destructive.
- A production migration failure leaves the migration unapplied and reports the first incoherent
  loan/snapshot identity. Operators must repair or isolate authoritative legacy data; no automatic
  DPD fabrication is permitted.

## Residual risk

- Governance has not defined a separate operational-scheme approval workflow; `active` is the
  current approval fact. Future governance must version this prospectively without rewriting
  retained snapshot bytes.
