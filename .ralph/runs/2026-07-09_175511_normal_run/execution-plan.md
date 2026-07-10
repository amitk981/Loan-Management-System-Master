# Execution Plan

Selected slice: 005B-application-submit-and-status-transition

## Context Read
- Read required Ralph files in order: `AGENTS.md`, token rules, project context, runbook,
  config, permissions, state, handoff, decision policy, frontend rules, the selected slice,
  parent epic, and the Epic 005 digest.
- Opened only the source sections needed to settle submit status and permissions:
  `api-contracts.md` §19.5 and audit example, `data-model.md` loan application status/table/event
  snippets, `auth-permissions.md` §12.4, §20.1, and endpoint map, plus portal submission text.

## Slice Boundary
- Implement `POST /api/v1/loan-applications/{loan_application_id}/submit/`.
- Permit only `draft -> submitted`.
- Preserve `current_stage = initial_loan_request`, `completeness_status = not_started`, and
  nullable `application_reference_number`.
- Enforce only the 005B-scoped submit facts: member exists through FK, positive requested amount,
  nonblank declared purpose, and nonblank purpose category.
- Do not implement reference number generation, document placeholders, nominee/document
  completeness, deficiencies, eligibility, appraisal, sanction, or frontend screens.

## TDD Plan
1. Add public API regression coverage in `sfpcl_credit/tests/test_loan_applications_api.py`:
   successful submit stamps actor/time, writes metadata-only audit/workflow evidence, keeps response
   masked, and preserves read access.
2. Run that targeted test with
   `/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py test ...` and save the
   expected red output under `.ralph/runs/2026-07-09_175511_normal_run/evidence/terminal-logs/`.
3. Implement the minimal backend behavior in `sfpcl_credit/applications/` and URL routing.
4. Add/extend tests for invalid state, permission denial, missing submit facts, not found, and PATCH
   rejection after submit; run targeted green tests and save output.

## Implementation Plan
- Add submitted status constants and `submitted_by_user` persistence if needed, with one
  non-destructive migration.
- Add submit permission helper and service function that uses the workflow guard foundation.
- Add submit view and URL route, returning standard success/error envelopes.
- Update serializer to include submitted actor/time without exposing sensitive values.
- Update `docs/working/API_CONTRACTS.md`, Epic 005 digest if needed, assumptions if any, and final
  Ralph artifacts.

## Gates And Evidence
- Save red/green targeted test output in `evidence/terminal-logs/`.
- Run backend checks/tests/migration sync/coverage with the required Ralph Python interpreter.
- Run frontend lint/typecheck/tests/build even though no frontend code is planned, because Ralph
  gates require them.
- Save API response examples, changed-files, risk assessment, review packet, final summary, and
  update state/progress/handoff/slice status before finishing.
