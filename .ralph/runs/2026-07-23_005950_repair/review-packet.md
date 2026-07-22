# Review Packet: 2026-07-23_005950_repair

## Result
Ready for independent validation

## Slice
011J-archive-record-and-retention

## Repair outcome

- Preserved the existing archive candidate and changed only its declared PostgreSQL acceptance
  test.
- Diagnosed deterministic `AssertionError: 2 != 1` at the unscoped total
  `LoanStatusHistory` assertion.
- The fixture correctly retains an account-creation history plus the financial-close history before
  archive. Archive is required to preserve both and prove its terminal transition through the
  canonical workflow event.
- Replaced the invalid total-count assertion with a pre/post identity assertion proving that all
  retained append-only loan histories are unchanged by five concurrent exact archive requests.

## Source-to-code-to-test traceability

- The slice requires the earlier financial-close record to be preserved and requires 011G-I
  histories to stay immutable. The archive module does not mutate `LoanStatusHistory`; the repaired
  PostgreSQL test now snapshots the exact retained history IDs before the race and proves the same
  identities remain afterward.
- The source requires archive creation only after closure/NOC/security completion and a single
  controlled terminal archive record (`product-requirements.md` §11.28; `security-privacy.md`
  §26.2; `data-model.md` §22.4). The unchanged five-race assertions still require five 200
  replays to converge on one manifest, one completed archive requirement, one
  `fully_closed_and_archived` workflow event, and one `closure.archive.created` audit.

## Red/green and checks

- RED: `evidence/terminal-logs/postgresql-acceptance-red.txt` ran exactly the declared class on
  PostgreSQL and reproduced `AssertionError: 2 != 1` (1 test, 1 failure).
- GREEN 1: `evidence/terminal-logs/postgresql-acceptance-green-1.txt` (1 test, OK).
- GREEN 2: `evidence/terminal-logs/postgresql-acceptance-green-2.txt` (1 test, OK).
- PostgreSQL facts: `evidence/postgresql-environment-validation.md` records the PostgreSQL Django
  backend and live PostgreSQL 14.20 server without credentials.
- Django check: `evidence/terminal-logs/backend-check.txt` is green.
- Migration sync: `evidence/terminal-logs/migrations-check.txt` reports no changes.

## Review focus

- Confirm the assertion proves loan-history immutability rather than assuming a fixture-wide total.
- Reproduce both trusted PostgreSQL runs with exact count 1 and confirm environment evidence.
- Run Ralph's authoritative backend lane and protected-path/diff checks on the preserved candidate.

## Recommended Next Action
Run Ralph's independent validation and commit only if every selected gate is green.
