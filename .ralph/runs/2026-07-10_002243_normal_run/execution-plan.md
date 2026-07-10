# Execution Plan

Selected slice: 005G-member-portal-application-start-status

## Scope
- Add authenticated borrower portal application endpoints for own-member draft create/update/read, submit, list, and status detail.
- Reuse the active `PortalAccount.member_id` scope from 005FB and existing 005A/005B application services.
- Wire MP05, MP09, and MP10 to real portal APIs while preserving existing portal visual patterns.
- Update API contracts, prototype tracking docs if needed, run artifacts, state, handoff, and selected slice status.

## Source Facts
- `screen-spec-member-portal.md` MP05/MP06/MP08/MP09/MP10 require create/resume/submit/list/status for own applications.
- `screen-spec-member-portal.md` permissions matrix limits MP05/MP09/MP10 to own portal applications and locks submitted applications from direct editing.
- `api-contracts.md` §19 defines draft create/update/read and submit behavior; §21 defines deficiency facts.
- `data-model.md` includes `incomplete_returned` and open `deficiencies`; 005F2 established returned applications as borrower rectification work with `completeness_status = incomplete`.

## TDD Plan
1. Backend RED: add portal member API tests for create/update/submit/list/status, member scope enforcement, staff endpoint denial, no LO reference before completeness, and returned-incomplete status facts.
2. Backend GREEN: add portal application service serializers/helpers, views, and URL routes using existing application services.
3. Frontend RED: extend `portalApi.test.ts` and portal view tests for application API mapping plus MP09/MP10 loading/error/empty states.
4. Frontend GREEN: add portal API client functions and wire MP05/MP09/MP10/BorrowerPortal state without new styling.
5. Run focused tests, then full Ralph gates.

## Expected Files
- `sfpcl_credit/members/portal_services.py`
- `sfpcl_credit/members/portal_views.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/tests/test_portal_member_api.py`
- `sfpcl-lms/src/services/portalApi.ts`
- `sfpcl-lms/src/services/portalApi.test.ts`
- `sfpcl-lms/src/pages/borrower/BorrowerPortal.tsx`
- `sfpcl-lms/src/pages/borrower/portal/applications/MP05_NewApplication.tsx`
- `sfpcl-lms/src/pages/borrower/portal/applications/MP09_MyApplications.tsx`
- `sfpcl-lms/src/pages/borrower/portal/applications/MP10_ApplicationStatus.tsx`
- `sfpcl-lms/src/pages/borrower/portal/PortalMemberViews.test.tsx`
- `docs/working/API_CONTRACTS.md`
- `docs/working/PROTOTYPE_INVENTORY.md`
- `docs/working/PROTOTYPE_GAP_REPORT.md`
- `docs/working/digests/epic-005-application-intake.md`
- Ralph state/progress/handoff/slice/run artifacts.

## Gates
- Backend focused tests with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Backend `manage.py check`, full tests, migrations check, coverage.
- Frontend `npm test`, `npm run typecheck`, `npm run lint`, `npm run build`.
