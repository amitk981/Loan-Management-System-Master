# Review Packet

## Summary
Implemented draft loan-application create/read/update through backend APIs:
- New app: `sfpcl_credit.applications`
- New table: `loan_applications`
- New endpoints:
  - `POST /api/v1/loan-applications/`
  - `GET /api/v1/loan-applications/{loan_application_id}/`
  - `PATCH /api/v1/loan-applications/{loan_application_id}/`

## Source Traceability
- Source says loan application APIs include create, retrieve, and update draft endpoints
  (`docs/source/api-contracts.md` §19.2-§19.4). Code implements those routes in
  `sfpcl_credit/applications/views.py` and `sfpcl_credit/config/urls.py`, verified by
  `test_create_and_read_draft_returns_metadata_only_response_and_audit` and
  `test_patch_updates_allowed_draft_fields_and_rejects_cross_member_references`.
- Source says loan applications reference members and store requested amount, purpose, status/stage,
  and actor fields (`docs/source/data-model.md` §13.1). Code stores those facts in
  `LoanApplication`, verified by create/read/patch API tests.
- Source says application endpoints require loan-application read/create/update permissions
  (`docs/source/auth-permissions.md` §12.4 and endpoint map). Code gates endpoints with those
  permission codes, verified by `test_draft_endpoints_enforce_permissions_and_validation`.
- Source and prior slices require sensitive values to remain masked. Code serializes only member
  summaries and masked bank/cancelled-cheque metadata, verified by assertions that responses and
  audit metadata omit PAN, Aadhaar, full account numbers, token values, hashes, and `holder_name`.

## Deliberate Deferrals
- Submit/status transition: 005B.
- Formal `LO...` reference generation and loan request register: 005C.
- Completeness, documents, deficiencies, eligibility, loan limits, appraisal, sanction,
  disbursement, member portal, and frontend wiring: later Epic 005+ slices.

## Evidence
- Red create/read: `evidence/terminal-logs/005A-red-01-create-read.log`
- Green create/read: `evidence/terminal-logs/005A-green-01-create-read.log`
- Red patch: `evidence/terminal-logs/005A-red-02-patch.log`
- Green patch: `evidence/terminal-logs/005A-green-02-patch.log`
- Focused tests: `evidence/terminal-logs/005A-loan-application-tests.log`
- Full backend tests: `evidence/terminal-logs/backend-tests.log`
- Coverage: `evidence/terminal-logs/backend-coverage.log`
- Frontend gates: `evidence/terminal-logs/frontend-*.log`
- API examples: `api-response-examples.md`

## Gate Results
- Backend check: passed.
- Backend tests: 241 passed.
- Migration check: passed, no changes detected.
- Backend coverage: 95%, floor 85%.
- Frontend lint: passed.
- Frontend typecheck: passed.
- Frontend tests: 80 passed.
- Frontend build: passed.
- `git diff --check`: passed.
