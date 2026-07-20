# Risk Assessment

Risk level: High

- Selected slice: 010J2-reminder-eligibility-and-delivery-integrity-closure
- Mode: normal_run
- Manual review required: independent Ralph validation is required before merge.

## Material risks and controls

- Early borrower contact across leap-year spans: eligibility now comes from the DPD owner's retained
  calendar-anniversary decision, with day-before/on/after PostgreSQL coverage.
- Stale automation after repayment, resolution, revoked scope/contact, or template expiry: both the
  send seam and worker execution recheck current owner truth; cancellation exhausts the job before
  the provider adapter and retains a safe audit reason.
- Duplicate or cross-owned delivery: communications conflicts are translated to the reminder 409
  contract; exact replay and competing PostgreSQL sends retain one communication job.
- Hidden partial batch effects: every scoped quarter snapshot returns a created/retained/skipped/
  failed row, and per-loan transactions isolate late contact/template failures.
- Schema evolution: one additive JSON field and one migration retain eligibility evidence; migration
  synchronization and Django system checks pass.

## Residual risk

- The orchestrator still owns the complete backend coverage suite and all repository-wide gates.
- Historical reminders receive the migration default `{}`; no historical eligibility is fabricated.
- No real provider was invoked and no real personal or financial fixture data was used.
