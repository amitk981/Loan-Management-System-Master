# Test Evidence — 010G Monthly Interest Accrual

## TDD RED

- `terminal-logs/accrual-single-red.log`: the public single-month endpoint returned 404 before the
  accrual interface existed; the exact tracer test failed and records `EXIT_STATUS=1`.
- `terminal-logs/accrual-bulk-dry-red.log`: the bulk dry-run endpoint returned 404; zero-write bulk
  behavior had no implementation and the log records `EXIT_STATUS=1`.
- `terminal-logs/accrual-sap-red.log`: the SAP evidence endpoint returned 404 before the terminal
  evidence transition existed; the log records `EXIT_STATUS=1`.
- `terminal-logs/accrual-principal-as-of-red.log`: after an August repayment reduced current
  principal to 300000.00, a July accrual incorrectly used 300000.00 instead of the immutable
  pre-repayment 400000.00 month-end truth; the log records `EXIT_STATUS=1`.

## TDD GREEN

- `terminal-logs/accrual-single-green.log`: one authorised July accrual derives 31 days,
  400000.00 principal, 9.2500 rate, and 3142.47 interest while creating one audit/rate snapshot/SAP
  obligation and no balance or ledger change; `EXIT_STATUS=0`.
- `terminal-logs/accrual-bulk-dry-green.log`: bounded dry run reports the calculated outcome while
  leaving accrual, obligation, rate-consumption, and audit counts at zero; `EXIT_STATUS=0`.
- `terminal-logs/accrual-sap-green.log`: authorised SAP evidence is retained once, exact replay is
  zero-write, and the local obligation transitions without claiming provider delivery;
  `EXIT_STATUS=0`.
- `terminal-logs/accrual-principal-as-of-green.log`: July resolves 400000.00 before the later
  repayment and September resolves the immutable 300000.00 post-repayment ledger balance;
  `EXIT_STATUS=0`.
- `terminal-logs/accrual-month-fy-leap-green.log`: March/April rate-version boundary and February
  2028's 29-day leap month calculate from their retained historical versions; `EXIT_STATUS=0`.

## Final Focused and Reverse-Consumer Proof

- `terminal-logs/accrual-final-reverse-consumers-green-2.log`: 48 tests passed, with 8 expected
  PostgreSQL-only skips. The labels cover 010G, annual invoice/rate history, 010A schedule/ledger,
  010C allocation, and servicing financial-owner reverse consumers; `EXIT_STATUS=0`.
- `terminal-logs/final-backend-static-gates.log`: Django system check and
  `makemigrations --check --dry-run` both passed; `EXIT_STATUS=0`.
- `terminal-logs/final-postgresql-local-collection.log`: the exact declared class
  `sfpcl_credit.tests.test_servicing_postgresql_acceptance.MonthlyInterestAccrualPostgreSQLAcceptanceTests`
  collected exactly one test and skipped only because the local database is SQLite;
  `EXIT_STATUS=0`. Ralph must execute this class twice on PostgreSQL.
- `git diff --check` passed. Per the run contract, the complete backend suite/coverage and frontend
  repository gates were not duplicated locally; the orchestrator owns those authoritative gates.
