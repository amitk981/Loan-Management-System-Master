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
1. Backend: member-scoped portal endpoints for dashboard summary (profile snapshot, application/loan counts, pending actions) and produce supply history, enforcing own-data-only access via the 005FA borrower scope.
2. Frontend: replace mock data in MP03, MP04, and the supply view with real APIs; masked sensitive fields per api-contracts §9.6 (no reveal on the portal side unless the source docs permit it).
3. Loading, empty, error, and unauthorized states per existing portal patterns; mobile-friendly per VISUAL_ACCEPTANCE.md.

## Test Cases
- Borrower sees only own profile/supply data (object-permission test).
- Dashboard counts reflect seeded fixtures; empty states covered.
- Sensitive fields render masked on the portal.

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
