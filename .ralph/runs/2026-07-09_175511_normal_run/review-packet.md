# Review Packet: 2026-07-09_175511_normal_run

## Result
Success.

## Slice
`005B-application-submit-and-status-transition`

## What Changed
- Added `POST /api/v1/loan-applications/{loan_application_id}/submit/`.
- Added `LoanApplication.STATUS_SUBMITTED` and optional `submitted_by_user` persistence.
- Submit permits only `draft -> submitted`, stamps `submitted_at`/`submitted_by_user`, keeps
  `current_stage = initial_loan_request`, keeps `completeness_status = not_started`, and leaves
  `application_reference_number` nullable.
- Submit responses reuse the 005A serializer, including member summaries and masked bank metadata
  with `account_holder_name`.
- Successful submit writes `applications.loan_application.submitted` audit metadata plus a
  `loan_application` workflow event from `draft` to `submitted`.
- Submitted applications remain readable through `GET` and are rejected by draft-only `PATCH`.
- Updated API contract, Epic 005 digest, and A-035/A-036 assumptions.
- Sharpened `005C` and `005D`.

## Traceability
- Source says loan application status includes `submitted` and the submit endpoint is
  `POST /api/v1/loan-applications/{loan_application_id}/submit/`
  (`docs/source/api-contracts.md` §19.5; `data-model.md` status table). Code implements that route
  and status in `sfpcl_credit/applications/views.py`, `services.py`, and `models.py`.
- Source says submit permission is `applications.loan_application.submit`
  (`auth-permissions.md` §12.4 and endpoint map). Tests deny a user without that permission.
- Source and slice require audit/workflow evidence for submit. Tests assert one metadata-only
  `applications.loan_application.submitted` audit row and one `draft -> submitted` workflow event.
- Source and prior slices require sensitive values remain masked. Tests assert submit response and
  audit metadata exclude PAN/Aadhaar/full bank/token/hash values.
- Portal source says the reference number is received after submitted details/documents are checked.
  Code leaves `application_reference_number` nullable and the docs record 005C as the owner.

## Verification
- RED: `submit-red.log` captured the first failing submit test with `404 != 200`.
- GREEN: focused loan application suite passed, 5/5.
- Full backend suite passed, 243/243.
- Backend coverage passed at 96% against the 85% floor.
- Frontend lint, typecheck, tests, and build passed.

## Files To Review First
- `sfpcl_credit/applications/services.py`
- `sfpcl_credit/applications/views.py`
- `sfpcl_credit/applications/models.py`
- `sfpcl_credit/tests/test_loan_applications_api.py`
- `docs/working/API_CONTRACTS.md`

## Recommended Next Action
Run `005C-reference-number-generation-and-loan-request-register`.
