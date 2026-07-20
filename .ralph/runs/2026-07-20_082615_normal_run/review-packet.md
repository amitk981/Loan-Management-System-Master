# Review Packet: 2026-07-20_082615_normal_run

## Result
Ready for independent validation

## Slice
010G-monthly-interest-accrual

## Recommended Next Action
Run Ralph's complete independent validation, especially the declared PostgreSQL race twice, migration
application/sync, and the complete six-worker backend coverage suite.

## Implementation Review

- Added immutable `accrual_entries` and one-to-one local SAP posting obligations with database
  uniqueness, monetary/status/evidence checks, protected references, and one migration.
- Extended the existing deep `interest.modules.interest_engine` interface for single creation,
  bounded selected/all-serviceable bulk generation with dry run, and terminal SAP evidence capture.
- Added a loan-owned `principal_balance_as_of` read seam so interest does not import or reconstruct
  repayment policy and later repayments cannot rewrite earlier principal snapshots.
- Reused the approved effective-rate consumption seam and the 010F versioned method/day-count
  configuration. No benchmark, spread, reset, penal-rate, tax, fee, or proration rule was invented.
- Updated the working API contract and recorded the full-month fail-closed policy as A-147.

## Traceability

- Product §11.24 and functional M10-FR-003 say monthly accrual is server-calculated and duplicate
  protected; the code derives principal/rate/configuration/amount and the database enforces one
  loan/month, verified by
  `MonthlyInterestAccrualApiTests.test_single_month_uses_server_owned_snapshots_and_creates_pending_sap_obligation`
  and the replay/duplicate test.
- Functional M10-FR-004 and user flow §29.4 say each month creates SAP posting work; the code creates
  one honest pending obligation and permits only audited local evidence transitions, verified by
  `test_authorised_sap_reference_capture_is_audited_and_exactly_replayable`.
- Data model §19.8 requires retained loan/month, principal, rate, amount, SAP reference/status, actor,
  and time truth; the migration/model preserve those fields and reject incoherent terminal status.
- The slice requires exact historical principal/rate truth and 010A/010C/010F consistency; the code
  resolves principal as of month end and consumes the effective rate as of month end, verified by
  `test_principal_snapshot_is_resolved_as_of_month_end_not_from_later_repayment`,
  `test_financial_year_rate_change_and_leap_month_use_historical_versions`, and the 48-test reverse
  consumer log.
- The slice requires real contention evidence; the exact declared PostgreSQL class contains one
  race test asserting `[200, 409]` and exactly one accrual, obligation, rate snapshot, and audit.

## Verification Evidence

- TDD RED/GREEN and final selectors are indexed in `evidence/test-evidence.md`.
- Final focused/reverse consumers: 48 passed, 8 expected PostgreSQL-only skips, exit 0.
- Django check and migration sync: exit 0.
- Exact PostgreSQL class: one test collected; local SQLite skip is honest and independent PostgreSQL
  execution remains mandatory.
- `git diff --check`: passed.

## Independent Review Focus

- Confirm PostgreSQL locking plus uniqueness yields exactly one complete accrual/audit/rate/SAP chain
  in both independent runs.
- Confirm migration constraints accept pending/posted/failed valid states and reject partial terminal
  evidence.
- Confirm the full suite finds no historical migration-projection leaf issue from `interest.0002`.
- Confirm A-147's full-month fail-closed policy is acceptable until governed proration exists.
- When 010H introduces capitalisation principal movements, it must extend the loan-owned
  `principal_balance_as_of` seam with its immutable ledger truth; it must not make 010G read a second
  current-balance source or rewrite retained accrual snapshots.
