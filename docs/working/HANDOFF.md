# Ralph Handoff

## Last Run
2026-07-10_041851_architecture_review

## Current Status
Completed architecture review for the four-slice window after commit `353c6df`:
- `005G2-member-portal-session-and-audit-contract-hardening`
- `005H-rejection-note-shell`
- `005I-application-intake-frontend-wiring`
- `006A-active-member-eligibility-service`

What changed in this review:
- Appended findings to `docs/working/REVIEW_FINDINGS.md`.
- Created corrective slice `005I2-application-detail-api-state-hardening`.
- Made `006B-default-document-purpose-and-terms-eligibility-checks` depend on `005I2`.
- Added distilled review extracts to the Epic 005 and Epic 006 digests.
- Reset architecture-review cadence in `.ralph/state.json`.

Primary finding:
- `005I` moved staff intake screens toward API-backed data, but `ApplicationDetail.tsx` still has a
  frontend-only `LO00000035` special case and hardcoded witness/sensitive nominee display data.
  This can override real backend status/document/owner display for a live `LO00000035` reference.
- The same corrective slice should expose nullable staff rejection-note metadata on application
  detail so the UI can show 005H rejection-note state separately from `application_status`.

Passes:
- `005G2` materially closed the prior portal session/audit findings.
- `005H` and `006A` have meaningful backend behavior tests with no-side-effect assertions.
- `006A` correctly limits itself to active-member eligibility and leaves default/document/terms/
  purpose/nominee checks to 006B.

## Validation
- Backend `manage.py check` passed.
- Backend `makemigrations --check --dry-run` passed.
- Backend coverage test run passed: 277 tests.
- Backend coverage report passed: 95%, above 85% floor.
- Frontend lint passed.
- Frontend typecheck passed.
- Frontend tests passed: 95 tests.
- Frontend build passed.
- `git diff --check` passed.

Evidence is in `.ralph/runs/2026-07-10_041851_architecture_review/`.

## Next Run
Run `005I2-application-detail-api-state-hardening`.

Key instructions for 005I2:
- Remove all `LO00000035` special-case status/document/owner/stage overrides from
  `ApplicationDetail.tsx`.
- Remove hardcoded witness rows and hardcoded nominee sensitive values; render API-backed facts or
  empty/unavailable states using existing visual patterns.
- Add nullable `rejection_note` metadata to the staff application detail response, with read-only
  no-audit behavior and existing application read/object access.
- Do not expose staff rejection-note metadata on borrower portal routes.
- Add backend tests for detail response with/without rejection note and object denial.
- Add frontend render regressions proving `LO00000035` does not trigger mock overrides and
  rejection-note metadata displays when returned.
- Preserve frontend design rules: existing components/classes only, no new styling.

After 005I2, run `006B-default-document-purpose-and-terms-eligibility-checks`.
