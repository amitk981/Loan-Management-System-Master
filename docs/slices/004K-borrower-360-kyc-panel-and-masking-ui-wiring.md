# Slice 004K: Borrower 360, KYC Panel, and Sensitive Reveal UI Wiring

## Status
Not Started

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal
Wire the remaining Epic 004 staff screens to the backend: Borrower 360 (S07), the KYC verification panel (S17), and the masked-field reveal workflow, so the member master built in 004A-004J is fully visible and operable in the UI.

## User Value
Credit and compliance staff can see the complete member/borrower picture — profile, KYC status, shareholding, land/crop, loans — from real data, and reveal sensitive fields only through the audited reveal flow.

## Depends On
- 004J

## Source References
- docs/source/screen-spec.md screens S07 (Borrower 360) and S17 (KYC Verification)
- docs/source/api-contracts.md sections 13.5 (view sensitive field), 18 (KYC APIs)
- docs/source/data-model.md sections 10-12 (party/member, shareholding, KYC tables)
- docs/source/auth-permissions.md (sensitive reveal permission and audit rules)
- docs/source/user-flows.md (member/KYC flows)

## Prototype Reference
- sfpcl-lms/src/pages/members/Borrower360.tsx
- sfpcl-lms/src/pages/members/MemberProfile.tsx (KYC and masking panels)

## Concrete Requirements
1. Wire `Borrower360.tsx` to real member, KYC, shareholding, land/crop, and loan-summary APIs from 004A-004J (add a thin aggregate endpoint only if the existing ones cannot compose the view).
2. Wire the KYC verification panel: document list, verify action, re-KYC status from 004H APIs.
3. Implement the masked-field reveal UI: masked display by default (api-contracts §9.6 masked value type), reveal via §13.5 endpoint with reason capture; reveal events audited per 004I.
4. Follow `docs/working/FRONTEND_DESIGN_RULES.md`: reuse existing panels/cards; loading, empty, error, unauthorized, and masked states covered.

## Test Cases
- Unauthorized user sees masked values and cannot reveal.
- Reveal with reason succeeds for permitted role and writes an audit event (asserted via API).
- Borrower 360 renders real data for a seeded member; empty and error states covered.

## Out of Scope
Loan account ledger detail (009J/010A), witness/nominee editing (004D/004E own those flows).

## Risk Level
Medium

## Acceptance Criteria
- Borrower 360 and KYC panels run on backend data with no mock-data remnants.
- Sensitive values never render unmasked without the audited reveal flow.
- All gates pass; screenshots include masked and revealed states.

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
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
