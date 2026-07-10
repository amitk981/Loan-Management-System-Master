# Review Packet

Run ID: 2026-07-10_002243_normal_run
Slice: 005G-member-portal-application-start-status

## Change Summary
- Added borrower portal application endpoints for own create/update/read/submit/list/status.
- Wired MP05 New Application, MP09 My Applications, and MP10 Application Status to the portal APIs.
- Updated API contracts, prototype inventory/gap report, Epic 005 digest, and sharpened 005H/005I.

## Traceability
- Source doc says MP05/MP06/MP08 allow the borrower to create/save/review/submit their own
  application. The code adds portal application create/update/submit routes in
  `sfpcl_credit/members/portal_views.py` and delegates to existing 005A/005B services in
  `sfpcl_credit/members/portal_services.py`. Verified by
  `test_portal_borrower_can_create_update_submit_list_and_read_own_application_status`.
- Source doc says MP09 lists applications belonging to the logged-in member. The code adds
  `GET /api/v1/portal/applications/` scoped to `PortalAccount.member_id` and wires
  `MP09_MyApplications.tsx` to `fetchPortalApplications()`. Verified by backend list assertions and
  frontend API/view tests.
- Source doc says MP10 shows lifecycle status, deficiencies, and next steps. The code adds portal
  detail serialization with status, pending owner, timeline, open deficiency count, and deficiency
  metadata, and wires `MP10_ApplicationStatus.tsx` to `fetchPortalApplication()`. Verified by
  `test_portal_status_marks_returned_incomplete_as_borrower_rectification_work`.
- Source permission matrix says MP05/MP09/MP10 are own-only. The code derives authority only from
  active `PortalAccount.member_id`, rejects cross-member path/payload access with
  `403 OBJECT_ACCESS_DENIED`, and denies staff/non-portal tokens with `403 PERMISSION_DENIED`.
  Verified by portal API permission tests.
- Prior source/digest facts say submitted applications can lack `LO...` references until
  completeness pass. The code leaves `application_reference_number` nullable in portal responses
  and does not invoke reference generation. Verified by backend submit assertions.

## Evidence
- Backend RED: `evidence/terminal-logs/backend-portal-applications-red.log`
- Backend focused GREEN: `evidence/terminal-logs/backend-portal-applications-green-1.log`
- Backend full tests: `evidence/terminal-logs/backend-tests.log`
- Backend coverage: `evidence/terminal-logs/backend-coverage.log`
- Backend check: `evidence/terminal-logs/backend-check.log`
- Backend migrations: `evidence/terminal-logs/backend-migrations-check.log`
- Frontend API RED: `evidence/terminal-logs/frontend-portal-api-red.log`
- Frontend API GREEN: `evidence/terminal-logs/frontend-portal-api-green.log`
- Frontend view GREEN: `evidence/terminal-logs/frontend-portal-views-green-2.log`
- Frontend full tests: `evidence/terminal-logs/frontend-tests.log`
- Frontend typecheck/lint/build:
  `evidence/terminal-logs/frontend-typecheck.log`,
  `evidence/terminal-logs/frontend-lint.log`,
  `evidence/terminal-logs/frontend-build.log`
- API examples: `evidence/portal-application-api-examples.json`
- Visual fallback: `evidence/portal-application-visual-evidence.html`
- Dev server failure log: `evidence/terminal-logs/frontend-dev-server.log`

## Known Limits
- Document upload/checklist, deficiency response/resubmission, rejection note, eligibility,
  appraisal, sanction, disbursement, and repayment behavior are explicitly out of scope for 005G.
- Live browser screenshot capture was blocked because the sandbox denied binding Vite to
  `127.0.0.1:5173`.
