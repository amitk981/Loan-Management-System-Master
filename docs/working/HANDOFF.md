# Ralph Handoff

## Last Run
2026-07-09_125944_normal_run

## Current Status
`004G-landholding-and-crop-plan-records` completed successfully.

## What Completed
- Added `LandHolding` persistence in `sfpcl_credit.members` with member FK, document type,
  survey/location fields, positive `area_acres`, required `document_id`, verification fields, and
  created timestamp.
- Added `CropPlan` persistence with member FK, nullable `loan_application_id`, crop type, season,
  positive `planned_area_acres`, optional estimated cost, loan-purpose alignment, optional
  `document_id`, verification fields, and created timestamp.
- Implemented `GET`/`POST /api/v1/members/{member_id}/land-holdings/` and
  `GET`/`POST /api/v1/members/{member_id}/crop-plans/` with standard envelopes and pagination.
- Recorded A-032 because source permissions have no land/crop-specific codes: list uses
  `members.member.read`, create uses `members.member.update`, and no new permission codes were
  seeded.
- Successful creates write `members.land_holding.created` or `members.crop_plan.created` audit
  metadata only; read access writes no audit/workflow rows.
- Replaced Member Profile's Land & Crop tab with API-backed loading/empty/error/list/validation/
  success/create states using existing UI patterns and no mock land/crop rows.
- Updated `docs/working/API_CONTRACTS.md`, `docs/working/ASSUMPTIONS.md`, and the Epic 004 digest.
- Sharpened `004H-kyc-upload-and-verification` and `004I-sensitive-masking-and-reveal-audit`.

## Explicit Deferrals
- Land/crop detail and update endpoints are not implemented.
- Verification actions for land holdings and crop plans are not implemented.
- Loan-limit calculations, per-acre scale-of-finance, land-based eligible amount, purpose
  eligibility, application blockers, and task scheduling remain deferred.
- Exact land/crop permission codes remain deferred until source docs define them.

## Evidence
See `.ralph/runs/2026-07-09_125944_normal_run/`.

Key logs under `evidence/terminal-logs/`:
- `backend-land-crop-red.log` and `backend-land-crop-green.log`
- `frontend-land-crop-red.log` and `frontend-land-crop-green.log`
- `backend-check.log`, `backend-tests.log`, `backend-makemigrations-check.log`,
  `backend-coverage.log`
- `frontend-typecheck.log`, `frontend-lint.log`, `frontend-tests.log`, `frontend-build.log`

Backend tests: 220 passed. Frontend tests: 73 passed. Coverage: 96%, above the 85% floor.

Visual/API evidence:
- `evidence/screenshots/land-crop-tab.html`
- `evidence/api-responses/land-crop-api-examples.md`

## Current Blocker
`004E-witness-shareholder-validation` remains blocked until a real loan-application boundary exists.
Shareholding facts now exist, but witness records belong to application documentation and must not
be implemented as member-level witness APIs.

## Notes For Next Run
- Run `004H-kyc-upload-and-verification` next.
- `004H` is High risk and already sharpened with KYC profile/document fields, KYC permission codes,
  metadata-only audit expectations, and frontend KYC tab wiring expectations if the APIs land.
- `004I` is sharpened to implement member PAN/Aadhaar reveal via
  `POST /api/v1/members/{member_id}/reveal-sensitive-field/` after 004H, with reason capture,
  field-specific reveal permissions, temporary response semantics, and audit rows without sensitive
  values.
