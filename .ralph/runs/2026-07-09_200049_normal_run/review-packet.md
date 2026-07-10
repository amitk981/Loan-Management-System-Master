# Review Packet: 2026-07-09_200049_normal_run

## Result
Success

## Slice
`005D-application-document-checklist`

## What Changed
- Added `ApplicationDocument` in `sfpcl_credit/applications/models.py` with one migration.
- Added service functions for:
  - listing application document metadata;
  - attaching document metadata to submitted applications;
  - verifying submitted document metadata;
  - deriving the source-required checklist from latest metadata rows.
- Added routes/views for application-document list/upload, document verify, checklist read, and
  checklist refresh.
- Extended loan application API tests for checklist item codes, upload/verify audit, sensitive-data
  exclusion, permission denial, object-scope denial, draft upload rejection, unknown IDs, and
  duplicate version history.
- Updated `docs/working/API_CONTRACTS.md`, `ASSUMPTIONS.md`, Epic 005 digest, handoff, progress,
  state, and slice status.

## Traceability
- Source/digest says application document endpoints are:
  `GET/POST /loan-applications/{id}/application-documents/`,
  `POST /application-documents/{id}/verify/`,
  `GET /loan-applications/{id}/document-checklist/`, and refresh.
  Code implements those routes in `sfpcl_credit/config/urls.py` and views in
  `sfpcl_credit/applications/views.py`; verified by
  `test_application_document_checklist_upload_and_verify_are_metadata_only`.
- Source/digest says application documents store metadata only and link to `documents.DocumentFile`.
  Code stores `document_file` FK, no bytes, in `ApplicationDocument`; verified by upload tests and
  sensitive-value assertions.
- Source/digest says required application-stage documents are loan application form, borrower PAN,
  borrower Aadhaar/OVD, nominee PAN, nominee Aadhaar/OVD, share certificate copy, land document /
  7/12 extract, crop plan, and six-month bank statement.
  Code defines `REQUIRED_APPLICATION_DOCUMENT_TYPES` and checklist output uses exactly those codes;
  verified by checklist test equality.
- Source/digest says cancelled cheque may be collected but is required before disbursement, not
  application checklist completion. Code allows `cancelled_cheque` as an upload document type but
  excludes it from `REQUIRED_APPLICATION_DOCUMENT_TYPES`; recorded in API contracts and digest.
- Slice says endpoints must reuse 005C2 object access. Views call
  `applications.services.evaluate_application_object_access(...)` for list/checklist/upload/verify;
  verified by same-permission out-of-scope denial tests.
- Slice says successful upload and verification require metadata-only audit. Code writes
  `applications.application_document.attached` and
  `applications.application_document.verified`; verified by audit assertions and sensitive-value
  exclusions.
- Slice says duplicates must preserve history. Code assigns `version_number = max + 1`; verified by
  two uploads producing versions 1 and 2 plus two audit rows.

## Validation Evidence
- RED: `evidence/terminal-logs/red-loan-application-documents.txt`
- GREEN: `evidence/terminal-logs/green-loan-application-documents.txt`
- Backend check: `evidence/terminal-logs/backend-check.txt`
- Migration check: `evidence/terminal-logs/backend-makemigrations-check.txt`
- Full backend tests: `evidence/terminal-logs/backend-tests-coverage-run.txt`
- Coverage: `evidence/terminal-logs/backend-coverage-report.txt`
- Frontend gates: `frontend-typecheck.txt`, `frontend-lint.txt`, `frontend-tests.txt`,
  `frontend-build.txt`
- API examples: `api-response-examples.md`

## Reviewer Notes
- No frontend code was changed because the slice declared no direct screens.
- Checklist refresh is intentionally read-derived under A-039; future 005E should not treat it as a
  persisted completeness decision.
- `black` is unavailable in the venv, but all required gates passed.

## Recommended Next Action
Run `005E-completeness-workbench`.
