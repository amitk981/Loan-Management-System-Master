# Ralph Handoff

## Last Run

2026-07-14_084216_normal_run

## Current Status

008B is complete. The backend now generates PDF or Word loan documents from retained, checksum-
verified approved template bytes and approval-owned frozen borrower/review/sanction facts. It
retains immutable §16.3 metadata, returns exact replay results, and exposes an object-scoped,
metadata-only list. Loan Agreement generation remains guarded until an executed Term Sheet exists.

Generation requires its dedicated permission, canonical application scope, template-file reference
authority, approved/effective/type/variant eligibility, and complete declared placeholders. It
creates one audit and workflow record without rendered content. PostgreSQL application locking plus
a database replay constraint retained one result under five concurrent identical requests.

## Validation

Evidence is in `.ralph/runs/2026-07-14_084216_normal_run/evidence/`. Frontend build, typecheck,
lint, and all 287 tests pass. Django check/migration sync and all 722 backend tests pass with 22
expected PostgreSQL-only skips at 93% coverage. Focused generation/frozen-snapshot regressions and
the authoritative PostgreSQL five-request replay race pass.

## Next Run

Run the due architecture review before further normal slices. After review, run sharpened 008C;
008D is also sharpened from the same Epic 008 digest for the subsequent queue position.
