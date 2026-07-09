# Slice 004F: Shareholding and Share Certificate Records

## Status
Not Started

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal
Deliver this narrow capability as a small, testable Ralph implementation slice.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 004D2

## Source References
- docs/source/implementation-roadmap.md section 11
- docs/source/api-contracts.md sections 13-18
- docs/source/data-model.md member/KYC/shareholding tables
- docs/source/screen-spec.md member screens

## Prototype Reference
- sfpcl-lms/src/pages/members/*
- sfpcl-lms/src/data/mockData.ts

## Screens Involved
Member Profile — Shareholding tab.

## Frontend Scope
Replace the current backend-shell Shareholding tab with API-backed list/create behavior only if the
backend shareholding API lands in this slice. Reuse existing Member Profile card, empty panel, alert,
and form patterns. Do not restore `mockData` share rows or introduce new styling.

## Backend/API Scope
Implement `GET` and `POST /api/v1/members/{member_id}/shareholdings/` from `api-contracts.md`
§15.1-§15.2. Include `PATCH /api/v1/shareholdings/{shareholding_id}/` only if it stays within this
small slice; otherwise leave update to a separate follow-up. Return standard envelopes and paginate
lists consistently with the existing member/nominee endpoints.

This slice now precedes witness validation because `data-model.md` §10.5 and `screen-spec.md` S09
require witness shareholder verification to resolve against real shareholder/shareholding facts.

## Database/Model Impact
Add non-destructive model/migration changes for `shareholdings` from `data-model.md` §11.1:
member FK, folio number, `number_of_shares`, `holding_mode` (`physical`/`demat`/`mixed`), optional
demat and valuation references as nullable UUIDs, valuation snapshot fields, `pledged_share_count`,
`available_share_count`, `future_shares_pledge_flag`, status, and timestamps. Add
`share_certificates` from §11.2 only if it stays within this slice: shareholding FK, certificate
number, optional distinctive number range, share count, optional document UUID, and status.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Use `members.shareholding.read` for `GET`, `members.shareholding.create` for `POST`, and
`members.shareholding.update` for any `PATCH`; enforce the same current accessible-member boundary
used by member and nominee APIs until source-backed object-scope facts are modeled.

## Audit Requirements
Record audit/workflow events for critical create/update/approval/access actions.

## Validation Rules
Reject negative `number_of_shares` and `pledged_share_count`; reject pledged shares greater than
total shares; persist or derive `available_share_count = number_of_shares - pledged_share_count`;
require `demat_account_id` only for demat-specific behavior when a demat account table exists.
Do not invent share valuation calculation, CDSL integration, pledge eligibility, or loan-limit
rules in this slice.

## Test Cases
TDD: list/create success, missing member, missing auth, read/create permission separation, invalid
share counts, pledged-count overflow, available-share calculation, no mock Shareholding tab rows,
and frontend loading/empty/error/validation/success states when UI is touched.

## Visual Acceptance Criteria
None.

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched.

## Risk Level
Medium

## Acceptance Criteria
- The named capability works through the intended backend/API/frontend path, where applicable.
- Source-doc business rules are enforced or documented as assumptions.
- Permissions and audit expectations are tested when applicable.
- The implementation stays within one small Ralph slice.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested, if needed
- [ ] Audit events tested, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
