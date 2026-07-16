# 009C Evidence Summary

## Red/green

- `terminal-logs/01-loan-account-success-red.log`: missing public `loans` owner.
- `terminal-logs/03-loan-account-success-green.log`: public success tuple green.
- `terminal-logs/04-loan-account-replay-red.log` and `05-loan-account-replay-green.log`: exact
  replay and changed retry.
- `terminal-logs/06-loan-account-json-contract-red.log` and
  `07-loan-account-json-contract-green.log`: malformed JSON envelope.
- `terminal-logs/08-loan-account-contract-matrix-red.log` and
  `09-loan-account-contract-matrix-green.log`: canonical duplicate conflict.
- `terminal-logs/14-review-findings-red.log` and `15-review-findings-green.log`: frozen dispute
  source, newest legal evidence, locked SAP decision, nullable links, complete history, and
  immutability findings from independent review.
- `terminal-logs/16-migration-harness-repro.log` and `17-migration-harness-green.log`: downstream
  loans migration-leaf interaction reproduced and fixed in historical migration tests.

## Local gates

- `terminal-logs/11-django-check-migrations.log`: Django check and migration drift.
- `terminal-logs/12-frontend-gates.log`: build, typecheck, lint, and 322 frontend tests.
- `terminal-logs/18-backend-full-coverage-final.log`: authoritative final SQLite backend suite and
  coverage threshold: 994 tests pass, 52 expected skips, 91% total coverage.
- `terminal-logs/19-django-check-migrations-final.log`: final Django system check and migration
  drift check pass.
- `terminal-logs/20-final-integrity.log`: state JSON, diff whitespace, queue/capability lint,
  Ralph workflow regressions, protected-file scan, and diff-limit accounting pass.

## PostgreSQL capability

`terminal-logs/10-loan-account-postgresql-race-1.log` honestly records that the coding sandbox was
denied access to `/tmp/.s.PGSQL.5432`. The collected `LoanAccountCreationRaceTests` is declared by
the slice's `postgresql-five-race-acceptance` capability. Ralph's orchestrator must run that exact
five-caller class twice outside the sandbox; no local pass or screenshot is claimed.

## Sanitization

`api-contract-example.json` uses synthetic UUIDs and values. Focused tests recursively scan the
response, audit, workflow, and status-history surfaces for protected borrower/nominee values,
document checksums, storage facts, and SAP plaintext.
