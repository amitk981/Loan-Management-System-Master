# Ralph Handoff

## Last Run
2026-07-09_215632_normal_run

## Current Status
Slice `005F2-deficiency-return-status-contract-hardening` completed successfully.

What changed:
- Added `LoanApplication.STATUS_INCOMPLETE_RETURNED = "incomplete_returned"` and included it in
  model validation.
- `POST /api/v1/loan-applications/{loan_application_id}/return-with-deficiencies/` now persists
  and returns `application_status = incomplete_returned`, `completeness_status = incomplete`, and
  `current_stage = initial_loan_request`.
- Audit metadata and the loan-application workflow event now record
  `submitted -> incomplete_returned`.
- Repeat returns from `incomplete_returned` remain blocked with standard
  `409 INVALID_STATE_TRANSITION` and no duplicate deficiency/audit/workflow/register/reference or
  sequence side effects. Assumption A-041 records this because source docs do not define repeat
  returns before borrower resubmission.
- API contract docs, Epic 005 digest, and the next portal slices were sharpened with the corrected
  returned-incomplete contract.

Source facts used:
- `docs/source/data-model.md` lists `loan_application_status = incomplete_returned`.
- `docs/source/functional-spec.md` M03 deficiency flow says incomplete applications enter the
  incomplete state and retain deficiency history.
- `docs/source/screen-spec.md` S12 says returned applications become
  `Incomplete - Returned to Applicant` or rejected.

## Validation
- TDD red/green saved for the focused deficiency-return regression.
- Focused loan-application API module passed.
- Full backend suite passed: 256 tests.
- Backend coverage passed: 95% total, above 85% floor.
- Backend `manage.py check` and `makemigrations --check --dry-run` passed.
- Frontend lint, typecheck, tests (80/80), and build passed.
- `git diff --check` passed.

Evidence is in `.ralph/runs/2026-07-09_215632_normal_run/`.

## Next Run
Run `005FA-member-portal-authentication`.

Key instructions for 005FA:
- Borrower/member portal tokens must carry a linked `member_id` own-data scope and must not grant
  staff completeness/pass/deficiency-resolution permissions.
- Portal auth and later portal screens must treat returned deficiency applications as
  `application_status = incomplete_returned`, not plain `submitted`.
- Do not allow borrower flows to perform repeat staff returns; resubmission behavior needs a
  source-backed transition in a later portal deficiency-response slice.
