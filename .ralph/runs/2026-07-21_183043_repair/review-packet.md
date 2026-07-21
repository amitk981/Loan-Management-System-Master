# Review Packet: 2026-07-21_183043_repair

## Result
Ready for independent validation

## Slice
010N-global-search-api-and-ui

## Repair Scope

The preserved 010N candidate failed one independent complete-suite test. The repair changes only the
new `aadhaar_last4` model/migration field metadata and this run's evidence artifacts; frontend,
search-provider, permission, response, and navigation code are unchanged.

## Root Cause

`members.0015` created `aadhaar_last4` as a non-null database column without a database default.
The failing credit migration test intentionally renders a historical cross-app `Member` model that
predates that field while the physical members table remains at 0015. Its insert therefore omitted
the column and violated the database constraint. Matching Python/database empty-string defaults is
the repository's established compatibility pattern for fields added across historical model seams.

## Validation Evidence

- RED: `evidence/terminal-logs/appraisal-history-migration-red.log` — exact independent failure
  selector reproduced the `members.aadhaar_last4` `NOT NULL` error; exit 1.
- GREEN: `evidence/terminal-logs/appraisal-history-migration-green.log` — the exact selector passes;
  1 test, exit 0.
- Adjacent migration coverage: `evidence/terminal-logs/appraisal-history-migration-class-green.log`
  — both forward and reverse historical-migration tests pass; 2 tests, exit 0.
- Downstream migration coverage:
  `evidence/terminal-logs/legacy-appraisal-remediation-migration-green.log` — both downstream
  historical-model remediation tests pass; 2 tests, exit 0.
- Search/member consumers: `evidence/terminal-logs/backend-search-member-consumers-green.log` — 27
  tests pass, including indexed query-plan assertions for Aadhaar suffix search; exit 0.
- Framework checks: `evidence/terminal-logs/backend-check.log` and
  `evidence/terminal-logs/backend-migrations-check.log` — Django check and migration-sync both pass.

## Traceability

The slice and `docs/source/data-model.md` §30 require an indexed, stored Aadhaar suffix used only for
server-side scoped matching. The code keeps `aadhaar_last4` non-null and indexed, gives unavailable
suffixes the non-matching empty-string representation, and continues to populate real suffixes in
the established member services. This is verified by the historical-migration classes and
`GlobalSearchApiTests.test_sensitive_and_suffix_queries_use_measured_indexes` in the 27-test pack.

## Review Notes

- No protected files, source documents, Git metadata, dependencies, or additional migrations were
  changed.
- No debug instrumentation or throwaway harness remains.
- Full backend coverage and the declared trusted-browser contract remain for Ralph's independent
  validator, as required by the repair prompt.

## Recommended Next Action
Run Ralph's full independent validation against the preserved candidate and commit only if every
gate passes.
