# Execution Plan

Selected slice: 004G-landholding-and-crop-plan-records

## Scope
- Implement `GET` and `POST /api/v1/members/{member_id}/land-holdings/`.
- Implement `GET` and `POST /api/v1/members/{member_id}/crop-plans/`.
- Add persistence for `land_holdings` and `crop_plans` matching `docs/source/data-model.md` §11.7-§11.8.
- Wire Member Profile's Land & Crop tab to the real APIs using existing Member Profile patterns only.
- Update working API contracts, assumptions, digest, handoff/state/progress/slice status, and run evidence.

## Source Rules Applied
- `api-contracts.md` §17.1-§17.2 defines the land-holding and crop-plan collection endpoints and create fields.
- `data-model.md` §11.7 requires non-null land `document_id`, land verification fields, and positive acreage.
- `data-model.md` §11.8 requires crop verification fields and allows nullable `loan_application_id` and `document_id`.
- `screen-spec.md` S06 requires a Member Profile Land and Crop Evidence tab.
- `implementation-roadmap.md` §11.2-§11.5 keeps loan-limit calculations, eligibility blockers, and scale-of-finance rules out of this slice.

## Permission Decision
- Source permission catalogue has no land/crop-specific codes.
- Per `DECISION_POLICY.md` and the slice instruction, record an assumption and use existing member-data permissions:
  `members.member.read` for list/read and `members.member.update` for create.
- Do not seed or invent new permission codes in this slice.

## TDD Plan
1. Backend red: add API tests for land/crop create+list, auth, read/create permission split, missing member, validation, malformed UUIDs, and audit/no workflow event.
2. Backend green: add models, migration, service serializers/validators, views, URLs.
3. Frontend red: add Member Profile tests for Land & Crop loading/empty/error/validation/success states.
4. Frontend green: extend `memberProfileApi.ts` and replace the Land & Crop tab mock/backend-shell state with API-backed list/create behavior.

## Quality Gates
- Backend commands use `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Save red/green TDD logs under `.ralph/runs/2026-07-09_125944_normal_run/evidence/terminal-logs/`.
- Run backend `manage.py check`, tests, `makemigrations --check`, coverage.
- Run frontend typecheck, lint, tests, build.

## Evidence
- Save API response examples under `evidence/api-responses/`.
- Save self-contained frontend visual evidence for the tab if live screenshot capture is blocked.
- Save changed files, risk assessment, review packet, and final summary.
