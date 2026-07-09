# Slice 005FB: Member Portal Dashboard, My Profile, and Produce Supply View

## Status
Complete

## Parent Epic
Epic 005: Loan Application Intake, Documents, Completeness, and Deficiencies (member portal entry)
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal
Wire the logged-in member's portal home: dashboard (MP03), My Profile (MP04), and the produce supply history view (prototype `MP22_ProduceSupply.tsx` — note: the spec's MP22 is grievance tracking; the prototype reused the number for supply history, see PROTOTYPE_GAP_REPORT).

## User Value
A borrower who logs in sees their real profile, applications, loans, alerts, and produce supply history — the portal stops being a mock-up.

## Depends On
- 005FA

## Prior Slice Facts To Preserve
- 005FA must provide a borrower/member portal token scoped to exactly one linked `member_id`.
  005FB must consume that member scope instead of accepting arbitrary member IDs from the client.
- 005F persists open/resolved deficiency rows for loan applications. MP03 pending actions should be
  able to count open deficiency actions for the logged-in member's own applications once those
  applications are visible, but 005FB must not implement application list/status screens from 005G.
- 005F2 corrected returned deficiency applications to `application_status = incomplete_returned`
  with `completeness_status = incomplete` and `current_stage = initial_loan_request`. Dashboard
  pending-action counts may use open deficiency rows, but any application-status summaries exposed
  by 005FB must preserve that returned-incomplete state rather than reporting the application as
  merely submitted.
- 005F2 blocks repeat staff return attempts from `incomplete_returned`; if 005FB exposes pending
  action counts for returned applications, it must treat them as borrower/member rectification work,
  not staff completeness actions.
- Portal source snippets opened during 005F define MP03 dashboard widgets for Pending Actions and
  Notices, and MP04 as profile content. The portal must not expose staff-only completeness,
  reference-generation, or deficiency-resolution actions.
- 005FA implemented `/api/v1/portal/auth/login/`, activation, reset, and password-change
  endpoints. Borrower access tokens and `/api/v1/auth/me/` now include `member_id`,
  `portal_account_id`, and `portal_role = borrower_member`; 005FB must derive the member from
  that authenticated scope and never from user-editable route/query values.
- 005FA exposes only portal own-data permission codes such as
  `portal.loan_application.read_own`; do not require or grant staff permissions like
  `members.member.read`, `applications.loan_application.read`, or
  `applications.loan_application.complete_check` for borrower portal reads.

## Source References
- docs/source/screen-spec-member-portal.md screens MP03 (dashboard), MP04 (profile)
- docs/source/api-contracts.md sections 13 (member), 43 (dashboard) for envelope/naming conventions
- docs/source/data-model.md section 11 (membership/shareholding/eligibility tables incl. produce supply records)
- docs/source/content-spec.md (portal wording)

## Prototype Reference
- sfpcl-lms/src/pages/borrower/portal/MP03_Dashboard.tsx
- sfpcl-lms/src/pages/borrower/portal/MP04_MyProfile.tsx
- sfpcl-lms/src/pages/borrower/portal/supply/MP22_ProduceSupply.tsx
- sfpcl-lms/src/pages/borrower/portal/MemberPortalLayout.tsx

## Concrete Requirements
1. Backend: member-scoped portal endpoints for dashboard summary (profile snapshot,
   application/loan counts, pending actions) and produce supply history, enforcing own-data-only
   access via the 005FA borrower scope. Do not accept a path/query `member_id` as authority when a
   portal token is present.
2. Dashboard summary should return at least:
   - member identity/status snapshot (`member_id`, display name, member number/folio, member type,
     membership status, KYC status, default status);
   - counts for own applications and own loans using currently implemented tables only;
   - pending action counts for open deficiencies where available from 005F, plus placeholders/zeroes
     for future signature, repayment, KYC update, and closure actions until their modules exist;
   - latest notice shell data only if backed by existing notification/communication rows.
3. Profile endpoint/response should reuse existing member profile, nominee, shareholding,
   land/crop, KYC, bank-account, and cancelled-cheque serializers where possible and preserve their
   masking rules. No PAN/Aadhaar/full bank reveal is allowed on the portal side unless a later
   source-backed slice explicitly permits it.
4. Produce supply history should be read-only and member-scoped. If no produce-supply model exists
   yet, return an empty list with a documented assumption rather than inventing source data.
5. Frontend: replace mock data in MP03, MP04, and the supply view with real APIs; masked sensitive
   fields per api-contracts §9.6.
6. Loading, empty, error, and unauthorized states per existing portal patterns; mobile-friendly per
   VISUAL_ACCEPTANCE.md.

## Test Cases
- Borrower sees only own profile/supply data (object-permission test).
- Staff tokens without `portal_role = borrower_member` cannot call member-portal own-data APIs
  unless a later source-backed staff-assist endpoint explicitly allows it.
- Dashboard counts reflect seeded fixtures; empty states covered.
- Sensitive fields render masked on the portal.
- A borrower cannot request another member's profile/dashboard/supply data even if they know the
  other member UUID.

## Out of Scope
Applications list/status (005G), documents (008L), loans/repayments (010L), notices/grievances (011NA).

## Risk Level
Medium

## Acceptance Criteria
- MP03/MP04/supply views run on backend data end to end for a logged-in member.
- All gates pass; screenshots saved at mobile width.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated
- [x] Permissions tested
- [x] Visual evidence saved
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates
