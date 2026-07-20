# Execution Plan

Selected slice: `010G-monthly-interest-accrual`

## Boundary and interface

- Extend the existing `interest.modules.interest_engine` module with monthly-accrual behavior; do
  not create a general servicing or capitalisation engine.
- Expose the selected API contracts for one loan/month, bounded bulk generation with explicit dry
  run, and authorised SAP posting evidence capture.
- Accept identity/month/status evidence only. Principal, effective rate, period, day-count method,
  calculation version, and amount remain server-owned.
- Preserve immutable calculation snapshots and one database row per loan/month. Keep external SAP
  delivery out of scope and represent the retained obligation/status honestly.

## TDD tracer bullets

1. RED/GREEN: one authorised, in-scope active loan creates a calendar-month accrual from the
   retained principal, effective-rate history, and one approved calculation configuration; it also
   creates one audit row and one pending SAP posting obligation without changing loan balances,
   ledger entries, repayment allocation, or annual invoice snapshots.
2. RED/GREEN: request validation, missing/ambiguous calculation configuration or rate, ineligible
   pre-disbursement/post-closure periods, permission denial, and cross-scope access all fail with no
   calculation/rate-consumption/audit/SAP writes.
3. RED/GREEN: exact replay returns the retained response with zero writes; a changed replay or a
   second request for the same loan/month cannot overwrite the snapshot.
4. RED/GREEN: bounded selected/all-active bulk generation returns per-loan
   `created`/`existing`/`skipped`/`failed` results; dry run calculates outcomes without database,
   audit, rate-consumption, or SAP-obligation writes, and one bad loan does not hide good outcomes.
5. RED/GREEN: authorised SAP reference/status capture retains actor/time/audit truth, supports exact
   replay, rejects changed/fabricated transitions, and never claims provider delivery.
6. RED/GREEN: month/FY/leap boundaries and effective-rate changes use the correct period-end rate
   snapshot while earlier accrual and 010F invoice snapshots remain immutable.
7. RED/GREEN: PostgreSQL same-loan/month contention retains exactly one accrual chain.

## Implementation and contracts

- Add the minimum interest-owned configuration, accrual, and SAP-obligation persistence plus one
  migration with uniqueness/check/index constraints and immutable calculation fields.
- Add routes/views that preserve the repository's standard success/error envelopes and object-scope
  nondisclosure behavior; update `docs/working/API_CONTRACTS.md` for the server-owned request shape,
  bulk bounds/results, and SAP status contract.
- Record only genuinely missing policy as an assumption; do not invent benchmark, spread, reset,
  day-count, tax, penal-rate, or provider rules.

## Verification and evidence

- Save every focused RED and GREEN command under
  `.ralph/runs/2026-07-20_082615_normal_run/evidence/terminal-logs/` with the required Ralph Python
  interpreter and explicit exit status.
- Run focused interest/rate/servicing reverse-consumer tests, the declared PostgreSQL label when the
  local database capability is available, `manage.py check`, and `makemigrations --check`.
- Do not run the complete backend suite or coverage locally; the orchestrator owns that gate.
- Inspect targeted diffs and migration SQL/state, then complete `risk-assessment.md`,
  `review-packet.md` (result exactly `Ready for independent validation`), and `final-summary.md`.
