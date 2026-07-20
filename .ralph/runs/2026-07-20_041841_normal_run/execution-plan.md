# Execution Plan

Selected slice: 010E2-effective-rate-versioning-and-borrower-notices

## Scope

Implement only the backend section-41.4 interest-rate configuration contract. Keep the public
module interface small: create/list through HTTP, activate through HTTP, and deterministic
historical resolution for later invoice/accrual callers. Reuse the existing communications
dispatcher for email/SMS snapshots, queued jobs, provider receipts, retry state, and honest
delivery status.

## Planned changes

1. Add configuration-owned models for immutable effective-dated floating-rate versions,
   per-loan historical rate evidence, and durable borrower-notice obligations, in one
   non-destructive migration.
2. Add an `interest_rate_configuration` module owning validation, maker-checker activation,
   locking/idempotency, contiguous effective periods, historical resolution, activation audit,
   and atomic notice fan-out to active loans.
3. Expose the source §41.4 list/create/activate routes using standard envelopes, exact
   `config.interest_rate.manage` authority for mutations, and read-only configuration authority
   for list access.
4. Add the permission to the seeded catalogue and document the concrete contract, conflict modes,
   boundary resolution, and notice status in `docs/working/API_CONTRACTS.md`.
5. Keep benchmark, spread, reset cadence, and penal-interest policy optional/configurable; do not
   derive an effective rate or invent a reset rule.

## TDD tracer bullets

1. RED→GREEN: authorised proposal creation/listing, exact fields, validation, sanitised audit, and
   mutation/read permission separation.
2. RED→GREEN: maker-checker activation, exact and changed idempotency replay, contiguous successor
   periods, immutable activated versions, and before/at/after historical resolution that fails
   closed on zero/multiple matches.
3. RED→GREEN: activation atomically creates exactly one loan-level notice obligation linked to one
   email and one SMS communication per affected active loan, queues through the existing dispatcher,
   exposes pending/failed/sent truth, and never treats queueing as delivery.
4. RED→GREEN: PostgreSQL concurrent activation has one winner, consistent periods, and no duplicate
   per-loan notice obligations; retain the declared three-test acceptance class and run it twice.
5. Add reverse-consumer tests showing later invoice/accrual code can retain a historical rate
   snapshot while newer versions activate without rewriting old evidence.

## Local verification and evidence

- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command.
- Save each focused failing and passing command with explicit exit status under
  `evidence/terminal-logs/`.
- Run focused configuration and communication regressions, `manage.py check`, and
  `makemigrations --check`; do not run the complete backend suite or coverage.
- Save a boundary matrix and contract examples, then complete `risk-assessment.md`,
  `review-packet.md`, and `final-summary.md` with paths that remain inside this run folder.
