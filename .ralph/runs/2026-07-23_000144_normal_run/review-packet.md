# Review Packet: 2026-07-23_000144_normal_run

## Result
Ready for independent validation

## Slice
011J-archive-record-and-retention

## Delivered

- Added immutable `ArchiveRecord` persistence and migration with one record per loan/closure,
  physical and/or digital location, retained actor/time, closure-derived start, server-enforced
  minimum retention, replay digests, audit, and terminal workflow evidence.
- Added `LoanClosureModule.archive`, POST/GET archive detail, and paginated searchable archive
  manifest endpoints. Exact replay is zero-write; duplicate/change replay conflicts.
- Enforced completed NOC plus completed/not-applicable security return before archive. Archive
  completes only its checklist requirement and does not rewrite financial close or loan history.
- Added Compliance/CS create+read grants and Internal Auditor read-only grant. Borrowers and wrong
  roles remain denied; access and denials are audited without paths/search terms.
- Added read-only/destruction constraints and no archive mutation/destruction action.

## Source-to-code-to-test traceability

- The source says an archive must contain physical/digital location and retain at least eight years
  after closure (`product-requirements.md` §11.28; `data-model.md` §22.4). The model and archive
  module derive start from `LoanClosure.closed_at`, calculate the calendar minimum, and reject a
  shorter date. Verified by
  `test_eligible_closure_archives_once_with_server_calculated_retention`,
  `test_short_or_forged_retention_is_rejected_then_exact_replay_is_read_only`, and
  `test_leap_day_closure_keeps_the_eight_year_calendar_anniversary`.
- The source says closure, NOC, SH-4/cheque/PoA release and CDSL unpledge must precede archive
  (`security-privacy.md` §26.2). The locked module consumes the NOC and security-return owners'
  retained requirement states. Verified by
  `test_archive_waits_for_noc_and_every_applicable_security_return`.
- The source says archived records stay searchable to authorised users, sensitive documents retain
  access control, and destruction needs future approval/certificate (`component-spec.md` §18.5;
  `security-privacy.md` §§26, 34). The detail/search interfaces enforce Compliance/Auditor scope,
  audit access without paths, deny Borrowers, and expose no mutation/destruction action. Verified by
  the detail/search, authority, and model-immutability tests in `test_archive_api.py`.
- The slice requires one PostgreSQL manifest and one terminal history chain under five racers. The
  exact declared `ArchiveRecordPostgreSQLAcceptanceTests` contains one five-race test asserting one
  archive, one completed requirement, one success audit, one terminal workflow event, and unchanged
  loan status history. SQLite discovered and skipped it as designed; trusted validation owns the
  PostgreSQL execution.

## TDD evidence

- Happy path RED: `evidence/terminal-logs/archive-happy-path-red.txt`; GREEN:
  `archive-happy-path-green.txt`.
- Detail read RED/GREEN: `archive-detail-read-red.txt` / `archive-detail-read-green.txt`.
- Search RED/GREEN: `archive-search-red.txt` / `archive-search-green.txt`.
- Permission catalogue RED/GREEN: `archive-permissions-red.txt` /
  `archive-permissions-green.txt`.
- Final archive behavior matrix: 9/9 green in `archive-final-focused.txt`.
- Reverse-consumer pack: 62/62 green in `impacted-regressions.txt`; catalogue: 18/18 green.
- Django check and migration sync: green in `backend-check-final.txt` and
  `migrations-check-final.txt`. Representative response: `evidence/archive-manifest-example.json`.

## Review focus

- Confirm trusted PostgreSQL five-race acceptance executes exactly one test and converges.
- Confirm the independently selected backend lane and migration/protected-path gates pass.
- Confirm no orchestrator-owned bookkeeping or protected/source file appears in the candidate.

## Recommended Next Action
Run Ralph's independent validation and commit only if every selected gate is green.
