# Ralph Handoff

## Last Run
2026-07-10_052139_normal_run

## Current Status
Completed `006B-default-document-purpose-and-terms-eligibility-checks`.

What changed:
- Existing `POST /api/v1/loan-applications/{id}/eligibility-assessment/run/` now computes
  source-backed checks beyond 006A active-member status.
- `default_check = no_default` only for `Member.default_status = no_default`; existing/default-like
  statuses return `default_found` and `overall_result = ineligible`.
- `document_check` uses 005D/005E required checklist metadata. Any blocking required item returns
  `incomplete` and `overall_result = ineligible`; raw files are not read.
- `terms_acceptance_check = accepted` only when `LoanApplication.terms_acceptance_flag = true`;
  otherwise it returns `pending` and `overall_result = ineligible`.
- `purpose_check = agriculture_aligned` only for `crop_production` or `agriculture_activity`;
  other purpose categories return `non_agriculture` and `overall_result = ineligible`.
- `nominee_check` uses `Nominee.loan_application_id` only when that application-specific fact
  exists. Adult nominee returns `valid`; minor nominee returns `minor` and ineligible. Missing
  application-specific nominee evidence remains `pending` with
  `overall_result = pending_manual_evidence`.
- `overall_result = eligible` only when member-active, default, document, terms, purpose, and
  nominee checks all pass.
- Ineligible eligibility assessments do not advance `application_status` or `current_stage`.
- Reruns update the existing one-to-one `EligibilityAssessment`.
- 006A permission/object access/state guard/no-success-evidence behavior is preserved.
- `docs/working/API_CONTRACTS.md` and the Epic 006 digest now record the 006B contract.
- `006C` and `006D` were sharpened from the Epic 006 digest/source extracts.

## Validation
- Backend TDD red/green eligible-path test passed.
- Focused loan-application API tests passed: 31 tests.
- Backend `manage.py check` passed.
- Backend full tests passed: 282 tests.
- Backend `makemigrations --check --dry-run` passed.
- Backend coverage report passed: 95%, above 85% floor.
- Frontend lint passed.
- Frontend typecheck passed.
- Frontend tests passed: 98 tests.
- Frontend build passed.
- `git diff --check` passed.

Evidence is in `.ralph/runs/2026-07-10_052139_normal_run/`.

## Next Run
Run `006C-loan-limit-configuration-and-calculator`.

Key instructions for 006C:
- Require a stored 006B eligibility assessment with `overall_result = eligible` before normal
  loan-limit calculation.
- Treat 006B `pending_manual_evidence` and `ineligible` as blockers; do not invent override or
  exception behavior in 006C.
- Implement `POST /api/v1/loan-applications/{loan_application_id}/loan-limit-assessment/calculate/`.
- Use source-backed member shareholding, landholding, crop-plan, requested amount, and loan-policy
  configuration facts. Cross-member facts must fail validation without persisted assessment/audit
  or workflow evidence.
- Formula contract from the digest/source: shareholding-based limit, land-based limit, and final
  eligible amount as the lower of the two. If requested amount exceeds final eligible amount, return
  `amount_within_limit_flag = false`, `exception_required_flag = true`, and a
  `REQUESTED_AMOUNT_EXCEEDS_LIMIT` warning.
- Do not silently decide the unresolved 30% vs 10% vs Rs 200/share policy ambiguity. Use existing
  source-backed config if present; otherwise block and record the ambiguity rather than inventing
  a rule.
