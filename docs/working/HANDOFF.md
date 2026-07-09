# Ralph Handoff

## Last Run
2026-07-10_023116_normal_run

## Current Status
Completed `005I-application-intake-frontend-wiring`.

What changed:
- Added staff read support for `GET /api/v1/loan-applications/` with standard pagination,
  search/filter/order parameters, `applications.loan_application.read`, and existing 005C2
  application object access.
- Added `GET /api/v1/loan-request-register/` for generated register rows, also protected by
  application read/object access.
- Added the frontend `applicationIntakeApi` client for staff list/detail/checklist/deficiency,
  create/update/submit, and register APIs.
- Rewired `ApplicationList.tsx` away from `mockData.ts`; it now renders backend application rows,
  backend filter/search state, `incomplete_returned` as borrower rectification work, and a Loan
  Request Register table.
- Rewired `NewApplication.tsx` away from mock member rows; it searches `GET /api/v1/members/` and
  saves/submits through staff `/api/v1/loan-applications/` endpoints.
- Rewired `ApplicationDetail.tsx` away from mock application/member/document/security/audit rows;
  it loads staff detail, document checklist, and deficiencies. Audit rows remain empty until a real
  audit UI/API wiring slice connects workflow/audit APIs.
- Added `incomplete_returned` to the frontend application status vocabulary and display logic.
- Updated `docs/working/API_CONTRACTS.md`.
- Created `docs/working/digests/epic-006-eligibility-loan-limit-appraisal.md` and sharpened
  `006A`/`006B`.

## Validation
- Backend red evidence: staff list returned `405` and register returned `404` before implementation.
- Backend focused list/register tests passed.
- Frontend red evidence: missing `applicationIntakeApi` client before implementation.
- Frontend focused API/list tests passed.
- Frontend lint passed.
- Frontend typecheck passed.
- Frontend tests passed: 95 tests.
- Frontend build passed.
- Backend `manage.py check` passed.
- Backend tests passed: 274 tests.
- Backend `makemigrations --check --dry-run` passed.
- Backend coverage passed: 95%, above 85% floor.
- `git diff --check` passed.

Evidence is in `.ralph/runs/2026-07-10_023116_normal_run/`.
Self-contained visual evidence is saved at
`.ralph/runs/2026-07-10_023116_normal_run/evidence/005I-visual-evidence.html`. Browser PNG
screenshots could not be captured because Playwright Chromium launch was blocked by the macOS
sandbox (`MachPortRendezvousServer` permission denied).

## Next Run
Run `006A-active-member-eligibility-service`.

Key instructions for 006A:
- Use `docs/working/digests/epic-006-eligibility-loan-limit-appraisal.md` before reopening large
  source docs.
- Implement only the eligibility-assessment foundation and active-member check.
- Run endpoint is `POST /api/v1/loan-applications/{loan_application_id}/eligibility-assessment/run/`;
  read endpoint is `GET /api/v1/loan-applications/{loan_application_id}/eligibility-assessment/`.
- Require `credit.eligibility.run` for run, preserve 005C2 application object access, and restrict
  run to reference-generated/completeness-complete applications in credit assessment.
- Do not implement override, loan limits, appraisal notes, Credit Manager review, or sanction
  submission in 006A.
- If produce/service history needed for BR-004 through BR-007 is not yet modelled, return a
  source-explicit manual-evidence/relaxation result and record the assumption; do not invent a
  supply-history calculation.
