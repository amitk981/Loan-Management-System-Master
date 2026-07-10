# Slice 004K: Borrower 360, KYC Panel, and Sensitive Reveal UI Wiring

## Status
Complete

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal
Wire the remaining Epic 004 staff screens to the backend: Borrower 360 (S07), the KYC verification panel (S17), and the masked-field reveal workflow, so the member master built in 004A-004J is fully visible and operable in the UI.

## User Value
Credit and compliance staff can see the complete member/borrower picture — profile, KYC status, shareholding, land/crop, loans — from real data, and reveal sensitive fields only through the audited reveal flow.

## Depends On
- 004J

## Prior Slice Facts
- 004I implemented member PAN/Aadhaar reveal only through
  `POST /api/v1/members/{member_id}/reveal-sensitive-field/` with request
  `{field_name: "pan"|"aadhaar", reason: non-empty text}`. Success returns the full value only in
  the immediate response with `expires_at`, `Cache-Control: no-store`, and `Pragma: no-cache`.
- 004I field permissions are exact: `members.sensitive.reveal_pan` for PAN and
  `members.sensitive.reveal_aadhaar` for Aadhaar, plus base `members.member.read`. Broad member,
  KYC, document, admin, export, or bank permissions are not reveal permissions.
- 004I audit actions are `members.sensitive_field.revealed` and
  `members.sensitive_field.reveal_denied`, metadata-only. 004K should test UI wiring against the
  endpoint and avoid duplicating backend audit contract tests unless UI behavior depends on them.
- 004J implemented member-profile bank metadata endpoints:
  `GET/POST /api/v1/members/{member_id}/bank-accounts/` and
  `GET/POST /api/v1/members/{member_id}/cancelled-cheques/`.
- 004J bank/cancelled-cheque responses expose only masked account-number objects
  `{masked, last4, can_view_full: false}` plus metadata such as IFSC, bank/branch name,
  verification status, signature flags, status, linked cancelled-cheque ID, and created timestamp.
  The endpoints never return full account numbers, protected token values, or hashes.
- 004J permission assumption A-034: lists use `members.member.read`, creates use
  `members.member.update`. Do not add UI affordances that imply PAN/Aadhaar reveal, KYC,
  document-download, disbursement, export, or security permissions can reveal bank account numbers.
- 004J explicitly deferred duplicate-active-borrower warnings, bank verification letters, signature
  mismatch resolution, blank-dated cheque custody, disbursement gates, payment initiation, and
  bank-account full reveal.

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
3. Implement remaining masked-field reveal UI outside the Member Profile overview: masked display by
   default (api-contracts §9.6 masked value type), reveal via the 004I §13.5 endpoint with reason
   capture, no local storage/mock-data/full-value caching, temporary expiry messaging only from the
   backend response, and hide/clear controls using existing Member Profile/Borrower360 patterns.
4. Display bank-account and cancelled-cheque metadata only as masked values from 004J endpoints. Do
   not add a bank-account reveal control, duplicate warning, signature-mismatch workflow, payment
   initiation, or disbursement-readiness UI in this slice.
5. Follow `docs/working/FRONTEND_DESIGN_RULES.md`: reuse existing panels/cards; loading, empty, error, unauthorized, and masked states covered.

## Test Cases
- Unauthorized user sees masked values and cannot reveal.
- Reveal with reason succeeds for permitted role through the 004I endpoint; blank reason blocks the
  UI call; full values are not persisted to local storage, mock data, URLs, or long-lived app state.
- Borrower 360 renders real data for a seeded member; empty and error states covered.
- Bank-account/cancelled-cheque panels render masked 004J metadata and do not leak full account
  numbers into DOM text, local storage, mock data, URLs, or long-lived app state.

## Out of Scope
Loan account ledger detail (009J/010A), witness/nominee editing (004D/004E own those flows).

## Risk Level
Medium

## Acceptance Criteria
- Borrower 360 and KYC panels run on backend data with no mock-data remnants.
- Sensitive values never render unmasked without the audited reveal flow.
- All gates pass; screenshots include masked and revealed states.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated, if needed
- [x] Permissions tested
- [x] Audit events tested
- [x] Visual evidence saved
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates
