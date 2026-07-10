# Execution Plan

Selected slice: 005I-application-intake-frontend-wiring

## Context Read
- `AGENTS.md`
- `docs/working/TOKEN_RULES.md`
- `docs/working/CONTEXT.md`
- `docs/working/AFK_RUNBOOK.md`
- `.ralph/config.yaml`
- `.ralph/permissions.json`
- `.ralph/state.json`
- `docs/working/HANDOFF.md`
- `docs/working/DECISION_POLICY.md`
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/slices/005I-application-intake-frontend-wiring.md`
- `docs/epics/005-application-intake-completeness.md`
- `docs/working/digests/epic-005-application-intake.md`
- Targeted source excerpts from `docs/source/api-contracts.md`, `docs/source/screen-spec.md`, and `docs/source/content-spec.md` for list pagination and S13 register columns.

## Scope
Wire staff Application List, New Application, Application Detail, and Loan Request Register surfaces to staff backend APIs. The existing backend lacks a staff GET collection and register list endpoint, so this run will add narrow read endpoints needed by the frontend without changing existing create/update/submit business rules.

## TDD Plan
1. Backend RED: add tests proving `GET /api/v1/loan-applications/` supports bearer auth, pagination, filtering/search, ordering, masked metadata-only list items, and no mock fallback assumptions.
2. Backend GREEN: implement list/query helpers and route `GET` on the existing collection endpoint.
3. Backend RED/GREEN: add and implement a narrow `GET /api/v1/loan-request-register/` endpoint returning generated register rows in the standard paginated envelope.
4. Frontend RED/GREEN: add an application intake API client test for list/detail/checklist/deficiency/register/create/submit calls and error envelope handling.
5. Frontend RED/GREEN: add server-rendered view tests proving list/detail/new application render API-backed data and state messages without `mockData` application rows.

## Implementation Plan
- Add backend list serialization/query helpers in `sfpcl_credit/applications/services.py`.
- Extend `sfpcl_credit/applications/views.py` and `sfpcl_credit/config/urls.py` with safe read endpoints only.
- Add `sfpcl-lms/src/services/applicationIntakeApi.ts` for staff APIs.
- Refactor `ApplicationList.tsx`, `NewApplication.tsx`, and `ApplicationDetail.tsx` to load from the API client, preserving existing visual structure and classes.
- Add or update tests under `sfpcl_credit/tests/` and `sfpcl-lms/src/pages/applications/` / `sfpcl-lms/src/services/`.

## Validation And Evidence
- Save red and green outputs in `.ralph/runs/2026-07-10_023116_normal_run/evidence/terminal-logs/`.
- Run focused frontend/backend tests during implementation.
- Run full required gates: backend check/tests/migrations/coverage with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`, frontend lint/typecheck/tests/build, and `git diff --check`.
- Save visual evidence for list, new application, and detail screens.
- Save `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, `final-summary.md`, and update state/progress/handoff/slice status.
