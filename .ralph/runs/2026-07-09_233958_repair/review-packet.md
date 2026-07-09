# Review Packet

## Slice
`005FB-member-portal-dashboard-profile-and-supply-view`

## Summary
- Added `GET /api/v1/portal/dashboard/`, `GET /api/v1/portal/profile/`, and
  `GET /api/v1/portal/produce-supply/`.
- Added `sfpcl-lms/src/services/portalApi.ts` and wired MP03/MP04/prototype MP22 to real portal
  APIs.
- Updated API contracts, A-043, Epic 005 digest, prototype inventory/gap report, handoff, progress,
  state, and next slice requirements.

## Traceability
- Source says MP03/MP04 are own-only portal screens
  (`screen-spec-member-portal.md` permissions matrix). Code derives member scope from active
  `PortalAccount.member_id`; test:
  `test_portal_dashboard_profile_and_supply_use_authenticated_member_scope`.
- Source says MP03 includes pending actions. Code counts open own deficiencies and leaves future
  action types as zero placeholders; test:
  `test_portal_dashboard_profile_and_supply_use_authenticated_member_scope`.
- Source says MP04 shows profile, nominee, shareholding, land/crop, bank, and KYC data. Code reuses
  existing Epic 004 serializers; frontend test: `PortalMemberViews.test.tsx`.
- Source requires sensitive values masked. Code forces portal PAN/Aadhaar reveal flags false and
  reuses masked bank serializers; backend and frontend tests assert masked values.
- Source/data model defines `produce_supply_records`, but no backend model exists. Code returns an
  empty shell with `source_status = model_not_implemented`; A-043 records the assumption.

## Validation
- Backend focused red: `evidence/terminal-logs/backend-portal-member-red.log`
- Backend focused green: `evidence/terminal-logs/backend-portal-member-green.log`
- Frontend API red/green:
  `evidence/terminal-logs/frontend-portal-api-red.log`,
  `evidence/terminal-logs/frontend-portal-api-green.log`
- Frontend view red/green:
  `evidence/terminal-logs/frontend-portal-views-red.log`,
  `evidence/terminal-logs/frontend-portal-views-green.log`
- Full backend tests: 262 passed.
- Backend coverage: 95%.
- Frontend tests: 88 passed.
- Frontend lint/typecheck/build passed.

## Visual Evidence
- Static self-contained HTML:
  `evidence/member-portal-005fb-visual-evidence.html`
- Playwright screenshot attempt failed with macOS Mach port permission denial:
  `evidence/terminal-logs/frontend-playwright-screenshot-attempt.log`
