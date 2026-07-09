# Slice 005FB: Member Portal Dashboard, My Profile, and Produce Supply View

## Status
Not Started

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
- 005F2 should have corrected returned deficiency applications to
  `application_status = incomplete_returned`. Dashboard pending-action counts may use open
  deficiency rows, but any application-status summaries exposed by 005FB must preserve that
  returned-incomplete state rather than reporting the application as merely submitted.
- Portal source snippets opened during 005F define MP03 dashboard widgets for Pending Actions and
  Notices, and MP04 as profile content. The portal must not expose staff-only completeness,
  reference-generation, or deficiency-resolution actions.

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
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Permissions tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
