# Risk Assessment

Risk level: High

- Selected slice: `010F-interest-invoice-generation`
- Mode: `repair`
- Standing approval: applicable; this repair does not broaden the approved slice.

## Demonstrated failure and repair risk

- The independent full-suite failure was a migration-test isolation defect, not a failed invoice
  calculation or database migration. The new `interest.0001` leaf legitimately depends on current
  loan/rate truth, but two legacy tests accidentally included that leaf while projecting historical
  application states.
- The repair changes only those tests' historical target filters. It excludes `interest` beside the
  already-excluded downstream owners, preventing current invoice dependencies from outrunning the
  pre-credit/pre-witness schema under test.
- The production migration, invoice engine, permissions, API, document generation, communication
  dispatch, and financial constraints are unchanged by this repair.

## Controls and residual validation

- The exact six errors reproduced together before the repair and the same six-test command passed
  twice afterwards against fresh databases with explicit exit 0.
- The preserved 010F API suite passed, as did Django system check and migration sync.
- No debug instrumentation, protected/source changes, dependency changes, or frontend changes were
  introduced. `git diff --check` passed.
- Residual risk is worker partition/order interaction outside the focused reproducer. Ralph's
  independent complete coverage suite remains the authoritative acceptance gate and must rerun
  before any commit.
