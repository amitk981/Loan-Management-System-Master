# Review Packet: 2026-07-15_151653_normal_run

## Result
Complete pending independent browser validation and commit

## Slice
008L3-portal-action-and-resubmission-contract-closure

## Recommended Next Action
Run the declared browser contract twice, then independently validate and commit the passing slice.

## Traceability

- `screen-spec-member-portal.md` MP07/MP13 says borrowers may upload own pending documents and
  download published documents but cannot accept them. The backend now returns and enforces the
  same locked flags; `test_stale_status_only_completion_cannot_be_reopened_by_portal_upload` proves
  a crafted POST writes no file or success audit.
- MP11 and §8.2 say corrections return the application to SFPCL completeness review.
  `loan_application_lifecycle.resubmit` invokes the 002H guard and canonical audit/workflow writer;
  the public deficiency test proves one success, repeated denial, an open staff deficiency, and
  truthful response-aggregate events.
- API §26 and auth §§19.4/21-23 require scoped, audited, short-lived protected downloads. The
  documentation and deficiency tests prove signed token issue/read, tamper, expiry, current-file
  replacement, cross-action denial, checksum content, full central audit metadata, and no-store.
- Frontend action contract §44 says the UI consumes backend actions while the backend still
  enforces them. Vitest proves exactly one canonical refetch, independent Complete plus Download,
  absent denied uploads, distinct 401/403 states, approved modal composition, validation, and safe
  blob navigation. The two declared Playwright specs own all four exact screenshots.

## Validation

- Frontend: lint, typecheck, build, 304/304 tests.
- Backend: Django check, migration drift, 887/887 tests, 92% coverage (floor 85%).
- Browser: both specs collect; local launch unavailable because Chromium is not installed.
- Diff: within 30-file/2,000-line limits; no protected file, dependency, or migration change.
