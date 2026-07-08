# Execution Plan

Selected slice: 004A-member-directory-api-and-ui

## Source Scope
- Implement only `GET /api/v1/members/` from `docs/source/api-contracts.md` §13.1.
- Use source `members.member.read` from `docs/source/auth-permissions.md` §12.2, §23.3, §25.1, and endpoint table §25.2.
- Persist the narrow member directory fields from `docs/source/data-model.md` §10.1 plus nullable shell fields for §13.1 `share_summary` and `active_member_status`.
- Frontend must reuse the existing `MemberDirectory.tsx` table/filter/card patterns and remove backend-wired dependency on `mockData`.

## Implementation Steps
1. Add TDD backend tests for authenticated list success, pagination envelope, filters, unknown/invalid filter rejection, 401/403, and no PAN/Aadhaar exposure.
2. Implement a narrow `members` Django app with model, migration, service, and read-only view wired at `/api/v1/members/`.
3. Update `docs/working/API_CONTRACTS.md` with the implemented member list contract and record any source-silent assumptions in `docs/working/ASSUMPTIONS.md`.
4. Add frontend API client and member directory tests covering loading, success, empty, error/unauthorized, and no mock fallback.
5. Wire `MemberDirectory.tsx` to `GET /api/v1/members/`, keeping existing visual classes and removing mock-only columns/actions from the backend-wired directory path.
6. Update prototype inventory/gap report to mark Member Directory as API-backed.
7. Save red/green/backend/frontend gate logs, API response examples, visual screenshots, changed files, risk assessment, review packet, final summary, state, progress, handoff, and slice status.

## Validation Plan
- Backend red test first using `/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python sfpcl_credit/manage.py test ...`.
- Backend gates: `check`, full tests, `makemigrations --check`, and coverage with the configured floor.
- Frontend gates: `npm run typecheck`, `npm run lint`, `npm test`, and `npm run build`.
- Use browser/screenshot evidence for populated, empty, API error, and unauthorized/forbidden member directory states.
