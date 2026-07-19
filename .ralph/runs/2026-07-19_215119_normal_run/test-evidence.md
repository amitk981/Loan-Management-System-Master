# Test Evidence

| Capability | Permanent test | Evidence |
|---|---|---|
| Ordered decimal schedule projection | `LoanScheduleLedgerApiTests.test_authorised_reader_gets_ordered_decimal_schedule_truth` | `evidence/terminal-logs/schedule-tracer-red.log`; `schedule-tracer-green.log` |
| Canonical immutable disbursement ledger | `LoanScheduleLedgerApiTests.test_ledger_projects_one_canonical_disbursement_without_copying_it` | `evidence/terminal-logs/ledger-tracer-red.log`; `ledger-tracer-green.log` |
| Later servicing preserves opening history | `LoanScheduleLedgerApiTests.test_later_servicing_balances_preserve_schedule_and_opening_disbursement` | `evidence/terminal-logs/servicing-safe-read-red.log`; `servicing-safe-read-green.log` |
| Immutable activation drift rejected | `LoanScheduleLedgerApiTests.test_historical_ledger_rejects_drifted_immutable_activation_amount` | `evidence/terminal-logs/historical-activation-drift-red.log`; `historical-activation-drift-green.log` |
| Complete schedule/ledger matrix | `sfpcl_credit.tests.test_loan_schedule_ledger_api` (10 tests) | `evidence/terminal-logs/schedule-ledger-focused-green.log` |
| Epic 009 reverse consumers | Six exact public creation/read/scope/transfer selectors | `evidence/terminal-logs/epic009-reverse-consumers.log` |
| Model/migration integrity | Django check and `makemigrations --check --dry-run` | `evidence/terminal-logs/backend-check-and-migrations.log` |
| Database constraints | `loans.0002_repayment_schedule` SQL and database rejection test | `evidence/terminal-logs/repayment-schedule-migration-sql.log`; focused green log |

The populated-read test asserts schedule and ledger query ceilings of 35 queries for a full
20-line schedule page and the canonical opening ledger row. Pagination tests cover 21 rows across
the exact 20-row boundary. All fixtures use generated identities and synthetic financial values.
