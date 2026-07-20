# Risk Assessment

Risk level: Medium

- Selected slice: 010J-reminder-queue
- Mode: normal_run
- Manual review required: independent Ralph validation remains required.

## Material risks and controls

- Duplicate borrower contact: automatic reminders have a conditional database uniqueness rule for
  loan/quarter/reason/channel, account row locking, communications idempotency, and twice-green
  PostgreSQL contention evidence. Manual phone calls remain distinct records by design.
- Stale work: every explicit send locks the reminder, rechecks current exact-quarter DPD, positive
  outstanding and serviceable account state, then cancels with a safe reason before creating a job
  if resolved.
- Fabricated delivery: reminder creation reports queued only. Sent/failed truth is read from the
  communications-owned job; phone logs cannot hold template, communication or provider evidence by
  database constraint.
- Authority/disclosure: mutations require `monitoring.reminder.create` and canonical loan scope.
  Tests cover missing permission and inaccessible-account nondisclosure. API/run summaries omit
  recipient, message body and provider-sensitive evidence.
- Template/contact integrity: SMS/email require existing borrower contact and the communications
  owner's approved/effective template validation. Caller message text cannot replace the governed
  rendered snapshot.
- Migration risk: one additive monitoring migration creates `reminders` with bounded channel,
  origin, status and channel-evidence constraints plus indexes. `makemigrations --check` is green.

## Residual risk

The independent full-suite/coverage gate and its clean-database migration execution remain the
authoritative final checks. The source does not name the quarter-run transport/bound; A-149 records
the bounded conventional interface for later governance or 010M consumption.
