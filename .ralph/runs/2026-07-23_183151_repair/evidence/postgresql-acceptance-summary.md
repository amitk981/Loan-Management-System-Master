# PostgreSQL Acceptance Evidence

## Contract

- Label:
  `sfpcl_credit.tests.test_compliance_postgresql_acceptance.GrievanceWorkflowPostgreSQLAcceptanceTests`
- Expected tests: 2
- Required independent runs: 2

## Result

- Independent run 1:
  database `test_sfpcl_credit_repair_green_1_2026_07_23_183151`; exactly 2 tests found; 2 passed.
- Independent run 2:
  database `test_sfpcl_credit_repair_green_2_2026_07_23_183151`; exactly 2 tests found; 2 passed.
- Environment:
  Django database vendor `postgresql`; PostgreSQL server 14.20 (Homebrew).

## Logs

- RED reproduction: `terminal-logs/01-postgresql-acceptance-red.log`
- GREEN run 1: `terminal-logs/04-postgresql-acceptance-green-1.log`
- GREEN run 2: `terminal-logs/05-postgresql-acceptance-green-2.log`
- Environment: `terminal-logs/08-postgresql-environment.log`
