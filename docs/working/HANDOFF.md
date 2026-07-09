# Ralph Handoff

## Last Run
2026-07-10_044114_normal_run

## Current Status
Completed `005I2-application-detail-api-state-hardening`.

What changed:
- Staff `GET /api/v1/loan-applications/{id}/` responses now include nullable, metadata-only
  `rejection_note` summary data when a staff `RejectionNote` exists.
- Staff rejection-note detail summary omits `detailed_reason`, does not change
  `application_status`, and read-only detail access writes no success audit/workflow event.
- Borrower portal application detail still omits staff rejection-note metadata.
- `ApplicationDetail.tsx` no longer special-cases `LO00000035` and no longer renders hardcoded
  witness rows or hardcoded nominee PAN/Aadhaar reveal values.
- Missing API-backed nominee/witness facts render neutral unavailable states using existing
  visual patterns.
- `docs/working/API_CONTRACTS.md` records the staff detail `rejection_note` contract.
- `006B` and `006C` were sharpened from the existing Epic 006 digest.

## Validation
- Backend `manage.py check` passed.
- Backend focused loan-application API tests passed: 27 tests.
- Backend full tests passed: 278 tests.
- Backend `makemigrations --check --dry-run` passed.
- Backend coverage report passed: 95%, above 85% floor.
- Frontend lint passed.
- Frontend typecheck passed.
- Frontend tests passed: 98 tests.
- Frontend build passed.
- `git diff --check` passed.

Evidence is in `.ralph/runs/2026-07-10_044114_normal_run/`.

## Next Run
Run `006B-default-document-purpose-and-terms-eligibility-checks`.

Key instructions for 006B:
- Preserve 006A state guard, `credit.eligibility.run`, application object access, one-to-one
  assessment rerun behavior, metadata-only `eligibility.assessed` audit, and no-success-evidence
  behavior on denied/invalid paths.
- Replace pending checks for default, documents, purpose, terms, and nominee only where
  source-backed data exists.
- Use 005D/005E document checklist metadata, not raw files.
- Treat `Member.default_status = no_default`, `LoanApplication.terms_acceptance_flag = true`, and
  `purpose_category in {crop_production, agriculture_activity}` as the explicit pass paths.
- For nominee, do not invent an application nominee-selection rule; leave pending/manual evidence
  where current application schema lacks the submitted nominee fact.
