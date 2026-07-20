# Execution Plan

Selected slice: 010J-reminder-queue

## Scope and interface

- Add a monitoring-owned reminder record and one deep reminder-queue module interface for bounded
  quarter-end creation, SMS/email queueing, and authorised phone-call logging.
- Reuse canonical 010I DPD snapshots, 010A loan balances/account scope, the existing governed
  communications dispatcher/job seam, central permission resolution, and immutable audit records.
- Expose only the source-backed 010J monitoring endpoints. Do not add frontend work, DPD
  recalculation, default transitions, provider implementations, or policy below one year.

## TDD tracer cycles

1. RED then GREEN: an authorised quarter-end run creates exactly the eligible beyond-one-year
   reminder and excludes current, under-threshold, and resolved accounts; replay stays zero-write.
2. RED then GREEN: database uniqueness and PostgreSQL concurrent runs retain one reminder per
   loan/quarter/reason/channel and concurrent sends retain one communications job.
3. RED then GREEN: SMS/email use an approved effective template, retained contact, immutable message
   snapshot, and communications job; stale or missing-contact work is skipped/cancelled honestly.
4. RED then GREEN: phone logs retain authorised actor, borrower-safe outcome and follow-up date with
   no communication/provider row.
5. RED then GREEN: wrong permission, cross-scope account, malformed quarter/date/channel, and
   unapproved/missing templates fail without reminder or false delivery evidence.

Each focused test is added and observed failing before its minimal implementation. RED/GREEN output
is retained under `evidence/terminal-logs/` with the required backend interpreter.

## Product changes

- Extend the monitoring model/migration and module/view/URL seams only as required by 010J.
- Seed the exact `monitoring.reminder.create` permission into the existing role catalogue following
  established monitoring permission patterns.
- Update `docs/working/API_CONTRACTS.md`; record only genuinely source-silent defaults in
  `docs/working/ASSUMPTIONS.md`.

## Verification and evidence

- Run focused monitoring tests after every tracer cycle, then the declared PostgreSQL acceptance
  class twice when the configured database is available.
- Run focused reverse-consumer tests for DPD, loan reads/allocation, and communications delivery/job
  behavior; run backend `manage.py check` and `makemigrations --check` but not the complete suite.
- Save test logs, model/API/race evidence, risk assessment, review packet, and final summary. Inspect
  targeted diff/statistics and ensure protected files and orchestrator-owned mechanical facts remain
  untouched. Set the review result exactly to `Ready for independent validation` only after focused
  gates are green.
