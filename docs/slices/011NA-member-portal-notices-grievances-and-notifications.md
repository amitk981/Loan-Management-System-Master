# Slice 011NA: Member Portal Notices, Grievances, Notifications, and Closure/NOC View

## Status
Not Started

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance
Epic file: `docs/epics/011-default-recovery-closure-compliance.md`

## Goal
Wire the remaining member-portal communication surfaces: Notices & Letters (MP19), grievance submission and tracking (spec MP21/MP22 — the prototype consolidates both into `MP24_SupportGrievance.tsx`), portal Notifications Center (MP23), and the static Help & Required Documents guide content (spec MP24) sourced from the content spec.

## User Value
Borrowers can read their real deficiency notes, sanction letters, reminders, invoices, and NOC; raise and track grievances; and see portal alerts — closing the borrower communication loop.

## Depends On
- 011N

## Source References
- docs/source/screen-spec-member-portal.md screens MP19, MP21, MP22, MP23, MP24
- docs/source/api-contracts.md sections 38 (grievance APIs), 39 (communication APIs)
- docs/source/content-spec.md (notice wording and help-guide content)
- docs/source/auth-permissions.md (borrowers see only own records)

## Prototype Reference
- sfpcl-lms/src/pages/borrower/portal/notices/MP19_NoticesLetters.tsx
- sfpcl-lms/src/pages/borrower/portal/support/MP24_SupportGrievance.tsx (covers spec MP21 + MP22)
- sfpcl-lms/src/pages/borrower/portal/notifications/MP23_Notifications.tsx
- sfpcl-lms/src/pages/borrower/portal/loans/MP20_ClosureNOC.tsx

## Concrete Requirements
1. Wire MP19 to member-scoped communications: deficiency notes (005F), rejection notes (005H), sanction outcome letters (007x), reminders (010J), interest invoices (010F), NOC (011H) — listed with document download via the audited signed-download flow (003D).
2. Wire grievance create/list/detail from the 011N APIs into `MP24_SupportGrievance.tsx`; borrowers see only their own grievances; status and resolution reason displayed.
3. Wire MP23 to the notification records for the logged-in member (003I foundation).
4. Render the Help & Required Documents guide from content-spec-derived static content within the existing portal layout — no new visual patterns.
5. Wire the Closure & NOC view (MP20, `MP20_ClosureNOC.tsx`): full-repayment closure status (011G), NOC availability/download (011H), and security return/unpledge status (011I) for the borrower's own loans.
6. Own-data-only enforcement on every endpoint; loading, empty, error states; mobile-friendly.

## Test Cases
- Borrower A cannot list or fetch borrower B's notices, grievances, or notifications (object-permission tests).
- Grievance create requires the required fields; resolution status displays after staff action via 011N.
- Notice download goes through the signed, audited download path.

## Out of Scope
Staff grievance workflow (011N done), closure/NOC issuance logic (011G/011H), real email/SMS delivery.

## Risk Level
Medium

## Acceptance Criteria
- MP19/MP21-24 surfaces run on backend data for a logged-in member end to end.
- All gates pass; screenshots at mobile width saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Ralph owns mechanical bookkeeping; record only substantive unresolved risks/decisions in `review-packet.md` and `HANDOFF` if needed
- [ ] Commit created only after passing gates
