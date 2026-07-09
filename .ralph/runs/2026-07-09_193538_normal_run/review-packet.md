# Review Packet

## Slice
`005C2-application-object-access-hardening`

## What Changed
- Added `applications.services.evaluate_application_object_access(...)`, reusing the existing 002I `evaluate_object_access(...)` helper.
- Enforced object access for:
  - `GET /api/v1/loan-applications/{loan_application_id}/`
  - `PATCH /api/v1/loan-applications/{loan_application_id}/`
  - `POST /api/v1/loan-applications/{loan_application_id}/submit/`
  - `POST /api/v1/loan-applications/{loan_application_id}/generate-reference/`
- Updated API contract notes, assumption A-038, Epic 005 digest, 005C2 status, and sharpened 005D/005E.

## Traceability
- Source says Field Officers are scoped to created/assigned applications, Credit Managers to the Credit Assessment domain, and a Field Officer viewing an unrelated application is denied (`docs/source/auth-permissions.md` §19.2, §37.3).
- Code now allows created/received users and a `credit_manager` role only for `current_stage = credit_assessment`.
- Verified by `test_unrelated_same_permission_user_is_object_access_denied_without_side_effects` and `test_credit_manager_can_read_credit_assessment_application_by_domain_scope`.

## Verification
- Red evidence: `evidence/terminal-logs/backend-red-object-access.log`.
- Focused green evidence: `evidence/terminal-logs/backend-green-object-access-focused.log`.
- Loan application suite: `evidence/terminal-logs/backend-green-loan-applications-final.log` (9/9).
- Full backend tests: `evidence/terminal-logs/backend-tests-full.log` (247/247).
- Coverage: `evidence/terminal-logs/backend-coverage.log` (95%, floor 85).
- Frontend gates: typecheck, lint, test (80/80), build logs under `evidence/terminal-logs/`.

## Reviewer Notes
- Denial responses are intentionally not audited in this slice; A-038 records the assumption.
- No schema change was required.
