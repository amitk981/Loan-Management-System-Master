# Ralph Handoff

## Last Run
2026-07-10_073826_repair

## Current Status
Completed `006C-loan-limit-configuration-and-calculator` after diagnosing the prior normal-run
no-op as a missing Codex command-host binary; no failed product changes were salvaged.

What changed:
- Added `POST /api/v1/loan-applications/{loan_application_id}/loan-limit-assessment/calculate/`.
- Added one-to-one `loan_limit_assessments` persistence and migration with all source §14.2
  share, land, policy, result, boundary, rule-version, actor, and timestamp snapshots.
- Calculation requires stored 006B `overall_result = eligible`; absent, pending-manual, and
  ineligible states return `409` with no loan-limit success evidence.
- Shareholding, every land holding, and crop plan must belong to the application member. Crop plans
  linked to another application/non-agriculture purpose and missing source facts return validation
  errors. Requested amount must match the stored application request.
- Exactly one active/effective Board-referenced loan policy must supply positive scale of finance
  and a percentage and/or per-share cap. Missing, overlapping, or unresolved config blocks.
- Percentage derives the per-share value from stored valuation; an optional cap is the ceiling.
  Land limit is selected acreage times configured scale of finance; final amount is lower-of-two.
- Above-limit requests return `REQUESTED_AMOUNT_EXCEEDS_LIMIT`, set within-limit false and
  exception-required true; equal/below boundaries need no exception.
- Successful reruns preserve the one-to-one assessment UUID and atomically write metadata-only
  `loan_limit.calculated` audit plus `loan_limit_assessment` workflow evidence. Denied/invalid/
  validation paths write none.
- Updated `API_CONTRACTS.md`, Epic 006 digest, and assumption A-047. Sharpened 006D immutable
  snapshot readback and 006E appraisal/risk/TAT/submit-review requirements.

## Validation
- Backend TDD endpoint tracer: red `404`, then green stored calculation.
- Focused loan-application API suite passed: 37 tests.
- Backend `manage.py check` passed.
- Backend full suite passed: 288 tests.
- Backend `makemigrations --check --dry-run` passed.
- Backend coverage passed: 95%, above the 85% floor.
- Frontend lint and typecheck passed.
- Frontend tests passed: 98 tests.
- Frontend build passed.
- `git diff --check` passed; no protected files changed; diff limits remain within configured caps.

Evidence is in `.ralph/runs/2026-07-10_073826_repair/`.

## Next Run
Run `006D-loan-limit-snapshot-storage`.

Key instructions for 006D:
- Add the stored snapshot read companion at
  `GET /api/v1/loan-applications/{loan_application_id}/loan-limit-assessment/`; do not recalculate.
- Prove mutations to shareholding, land/crop, application amount, and policy do not change GET
  output until a new successful calculate call replaces the snapshot.
- Persist the smallest immutable policy-source metadata needed to reproduce 006C's
  `configuration_source` without reading mutable config rows.
- GET uses application read plus existing object access and creates no audit/workflow evidence.
- Failed reruns must leave the prior stored snapshot unchanged and create no success evidence.
