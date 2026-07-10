# Slice 004K2: Borrower 360 Bank Holder Contract Hardening

## Status
Complete

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal
Close the architecture-review finding from `2026-07-09_163909_architecture_review` before loan
application intake starts.

## User Value
Credit and compliance staff see the bank-account holder name that the backend actually returns on
Borrower 360, instead of a blank value caused by a frontend DTO-name mismatch.

## Depends On
- 004K

## Source References
- `docs/working/API_CONTRACTS.md` member bank-account metadata API, `004J`
- `docs/working/digests/epic-004-member-kyc-master.md`
- `docs/slices/004J-bank-account-and-cancelled-cheque-profile-foundation.md`
- `docs/slices/004K-borrower-360-kyc-panel-and-masking-ui-wiring.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-09_163909_architecture_review`

## Prototype Reference
- `sfpcl-lms/src/pages/members/Borrower360.tsx`
- `sfpcl-lms/src/pages/members/Borrower360.test.tsx`
- `sfpcl-lms/src/services/memberProfileApi.ts`

## Screens Involved
Borrower 360 Bank & Security tab.

## Frontend Scope
Fix the frontend bank-account DTO and Borrower 360 rendering to consume the backend/contract field
`account_holder_name`. Do not rename the backend response, add new styling, or introduce new bank
account behaviors.

Concrete scope:
- update the frontend `MemberBankAccountDetail` type and normalizer to preserve
  `account_holder_name`;
- keep account-number normalization masked-only with `can_view_full: false`;
- update Borrower 360 bank-account rendering to display `account_holder_name`;
- update tests so the API-client fixture uses the backend response shape, not the frontend-only
  `holder_name` alias;
- add a regression that fails if `account_holder_name` from the backend is not rendered.

## Backend/API Scope
No backend behavior change expected. Preserve the 004J response field `account_holder_name` and the
existing member-scoped `GET /api/v1/members/{member_id}/bank-accounts/` contract.

## Database/Model Impact
None expected.

## API Contracts
No contract rename. If docs are touched, keep `account_holder_name` as the canonical response field.

## Permissions
No permission changes. Preserve 004J/A-034 bank metadata read behavior.

## Audit Requirements
No audit behavior changes.

## Validation Rules
No validation behavior changes.

## Test Cases
TDD frontend test first:
- a mocked `GET /api/v1/members/{member_id}/bank-accounts/` response with
  `account_holder_name: "Ramesh Patil"` normalizes that value;
- Borrower 360 Bank & Security tab renders the account holder name from `account_holder_name`;
- the normalized bank account still does not contain full account numbers, token values, hashes, or
  a bank reveal affordance.

Run the existing Borrower 360 test suite and standard gates.

## Visual Acceptance Criteria
No visual design changes. Use the existing Bank & Security card/list pattern.

## Evidence Required
Frontend red/green logs and standard quality-gate logs.

## Risk Level
Medium

## Acceptance Criteria
- Borrower 360 displays bank-account holder names returned by the backend contract.
- Frontend tests use the backend `account_holder_name` response shape.
- Bank account numbers remain masked-only and unrevealable in the UI.
- No production scope beyond this contract hardening is introduced.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated, if needed
- [x] Database rules followed, if needed
- [x] Permissions tested, if needed
- [x] Audit events tested, if needed
- [x] Visual evidence saved, if frontend
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates
