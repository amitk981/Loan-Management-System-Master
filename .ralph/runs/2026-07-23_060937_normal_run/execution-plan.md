# Execution Plan

Selected slice: `011M-kyc-re-kyc-compliance-tracker`

## Boundary

Implement the backend-only KYC/re-KYC compliance tracker described by slice 011M. Reuse the
compliance task engine, scheduler job, notification, member/KYC verification, member object-scope,
audit, and restricted-document owners. Do not add frontend wiring, mutate KYC facts from the
tracker, define an external CKYC integration, or change generic task/communication policy.

## TDD behaviours (one red/green cycle at a time)

1. Generate one cycle-unique review and linked compliance task exactly two calendar years after a
   canonical verified KYC result, deriving due/warning/overdue state and projecting Individual/FPC
   completeness from governed member, KYC document, CKYC, nominee, beneficial-owner, and risk facts.
2. Make scheduler replay and concurrent PostgreSQL execution converge on one review/task/reminder
   identity; reject changed replay facts.
3. Expose permissioned, member-scoped list/detail queries with due-within-30-days, overdue, member
   type/status, and assignment filters; keep sensitive document facts masked/restricted.
4. Allow assignment and due/overdue reminder requests only to authorised KYC/Credit owners, using
   retained notification delivery state and append-only safe audit evidence.
5. Complete a review only when a newer, canonical governed KYC verification exists; reject stale,
   same-cycle, caller-supplied, foreign, premature, and direct-mutation attempts while retaining
   before/after status, reviewer, completion time, evidence links, task closure, and audit.
6. Verify API envelopes, role/scope denials, invalid filters/dates/statuses, restricted document
   download delegation, and reverse-consumer KYC/task/notification behaviour.

## Planned files

- Add the KYC review model and one compliance migration.
- Add a deep `compliance.modules.kyc_review_tracker` service/query interface.
- Add thin compliance HTTP views and URL routes.
- Add focused service/API/PostgreSQL acceptance tests and update the working API contract.
- Save red/green logs, focused validation output, risk assessment, review packet, and final summary
  under this run directory.

## Validation

- For every behaviour: run the single new failing Django test with
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python`, save RED output, implement minimally, rerun and
  save GREEN output.
- Run the focused compliance, member KYC, document download, communication, and scheduler tests.
- Run `manage.py check` and `makemigrations --check`; do not run the complete backend suite locally.
- Run the declared PostgreSQL acceptance label when the configured database is available; preserve
  the exact expected test count of one for `RekycSchedulerPostgreSQLAcceptanceTests`.
