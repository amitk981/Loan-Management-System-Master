# Execution Plan

Selected slice: 010A-loan-account-schedule-and-ledger

## Boundary

Implement only backend-owned, read-only repayment-schedule and loan-ledger truth for an existing
loan account. Add no repayment capture/allocation, interest/DPD calculation, schedule generator,
mutation endpoint, or frontend wiring.

## Public interfaces

- `GET /api/v1/loan-accounts/{loan_account_id}/repayment-schedule/?page=&page_size=`
- `GET /api/v1/loan-accounts/{loan_account_id}/ledger/?page=&page_size=`

Both interfaces reuse the existing `finance.loan_account.read` plus canonical object-scope seam,
return the standard list envelope, reject unknown/invalid pagination, and disclose inaccessible
accounts as `404 NOT_FOUND` only after authentication and role/permission authority succeeds.

## TDD tracer bullets

1. RED: an authorised, scoped reader requests an active account schedule and receives ordered,
   decimal source rows. GREEN: add the exact §18.3 schedule model, database constraints/migration,
   and the schedule projection/read endpoint.
2. RED: the same reader requests the ledger and receives exactly one canonical successful
   disbursement row with debit/opening running balances, owner reference, transfer actor, and SAP
   status. GREEN: add the deep read projection over the canonical Epic 009 transfer evidence; do
   not duplicate it into a mutable ledger row.
3. RED→GREEN incrementally cover empty collections, stable page boundaries and ordering, strict
   query validation, unauthenticated/forbidden/cross-scope/missing access, query bounds, immutable
   source behavior, and schedule uniqueness/non-negative database rejection.

## Expected changes

- `sfpcl_credit/loans/models.py` and one `loans` migration for repayment schedules.
- A process-level coordinator over loans, SAP, and disbursement owner interfaces,
  `sfpcl_credit/loans/views.py`, and `sfpcl_credit/config/urls.py` for the reads.
- Focused public API/model tests plus focused Epic 009 reverse-consumer runs.
- `docs/working/API_CONTRACTS.md` with exact request, response, pagination, permission, ordering,
  immutability, and error contracts.
- Current-run RED/GREEN, migration, query-count, response-example, reverse-consumer, check, lint,
  and review evidence; no frontend evidence because the slice explicitly excludes UI wiring.

## Verification

- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every Django command.
- Run each focused test selector once while RED and again after its minimal GREEN implementation,
  retaining explicit exit codes in `evidence/terminal-logs/`.
- Run the completed focused schedule/ledger file, impacted loan/disbursement reverse-consumer files,
  `manage.py check`, and `makemigrations --check`; do not run the complete backend suite/coverage.
- Inspect diff stats/targeted hunks, then perform the required independent-style standards/spec
  review and record risk, review packet, and final summary.
