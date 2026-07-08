# Slice 004C: Individual Farmer and FPC Profile Details

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
- 004B

## Source References
- docs/source/implementation-roadmap.md section 11
- docs/source/api-contracts.md sections 13-18
- docs/source/data-model.md member/KYC/shareholding tables
- docs/source/screen-spec.md member screens
- docs/working/digests/epic-004-member-kyc-master.md

## Prototype Reference
- sfpcl-lms/src/pages/members/*
- sfpcl-lms/src/data/mockData.ts

## Screens Involved
Member Profile type-specific profile sections beyond the 004B masked profile shell.

## Frontend Scope
004B already renders Member Profile from the backend. Wire only the additional type-specific fields
added by this slice into that existing profile layout. Reuse existing cards/tabs/badges/empty states;
do not add new styling or restore `mockData` rows.

## Backend/API Scope
Extend the 004B profile shell storage/serialization with the remaining source §10.2/§10.3 fields:
individual `first_name`, `middle_name`, `last_name`, `gender`, `date_of_birth`, `occupation`, and
`employment_or_service_years`; producer/FPC authorised-signatory sensitive fields must remain
masked/deferred unless this slice explicitly implements the §13.5 reveal controls. Do not implement
create/update member mutations unless this slice is rewritten before the run.

## Database/Model Impact
Add non-destructive columns/migration only to the existing 004B profile shell tables. Keep one
profile row per member (`member_id` FK/UQ). Do not add nominee, witness, shareholding, share
certificate, demat, KYC document, bank account, land/crop, loan, or communication tables in 004C.

## API Contracts
Update `docs/working/API_CONTRACTS.md` for the profile object added to
`GET /api/v1/members/{member_id}/`. Document the exact fields returned for individual farmers versus
FPC/producer institutions and the empty/null behavior when a profile row is missing.

## Permissions
Apply the role and object-access rules from `docs/source/auth-permissions.md`; classify unknown
access as approval-required. Use `members.member.read` for masked profile reads unless the source
documents opened during the run define a narrower code. Do not grant sensitive reveal permissions.

## Audit Requirements
Masked read-only profile detail should not create workflow events. If this slice adds no public
mutation endpoint, no create/update audit action is required. If the slice is explicitly widened to
create/update profile data, audit the mutation metadata only and never store full PAN/Aadhaar values
in audit rows.

## Validation Rules
Enforce only source-backed structural rules: profile member must exist, individual profile belongs
only to `individual_farmer`, and producer-institution profile belongs only to `fpc` or
`producer_institution`. Do not invent eligibility, KYC approval, active-member, nominee, witness,
shareholding, land/crop, loan-application, or appraisal blockers.

## Test Cases
TDD backend tests first: individual profile serialization, FPC/producer-institution profile
serialization, missing profile row behavior, wrong member-type/profile mismatch validation at the
service/model boundary, `401`, `403`, and no PAN/Aadhaar leakage. Frontend tests are required if the
profile UI is touched: API data renders for each member type, missing profile renders existing empty
state, and no `mockData` profile fixture is imported/rendered on the wired path.

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
