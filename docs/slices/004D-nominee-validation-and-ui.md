# Slice 004D: Nominee Validation and UI

## Status
Complete

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal
Deliver this narrow capability as a small, testable Ralph implementation slice.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 004C

## Source References
- docs/source/implementation-roadmap.md section 11
- docs/source/api-contracts.md sections 13-18
- docs/source/data-model.md member/KYC/shareholding tables
- docs/source/screen-spec.md member screens

## Prototype Reference
- sfpcl-lms/src/pages/members/*
- sfpcl-lms/src/data/mockData.ts

## Screens Involved
Member Profile — Nominee tab.

## Frontend Scope
Replace the 004B deferred Nominee tab with API-backed nominee list/create behavior. Reuse the
existing card, empty panel, form/modal, alert, and validation patterns. Do not restore `mockData`
nominees or add new styling.

## Backend/API Scope
Implement `GET` and `POST /api/v1/members/{member_id}/nominees/` from source §14.1-§14.3.
Create only member-level nominees; `loan_application_id` remains nullable and application snapshot
behavior is deferred.

## Database/Model Impact
Add one `nominees` model/migration matching data-model §10.4: member FK, nullable application FK
only when that module exists, name, DOB/age snapshot, gender, relationship, encrypted+hashed PAN
and Aadhaar, KYC status, `minor_flag`, signature-required flag, and timestamps. Never store plaintext
PAN/Aadhaar.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Use `members.nominee.read` for GET and `members.nominee.create` for POST, plus accessible-member
enforcement using the same currently implemented member boundary. Do not reuse `members.member.read`
for nominee creation.

## Audit Requirements
Audit nominee creation metadata without full PAN/Aadhaar. Read-only masked list access creates no
workflow event.

## Validation Rules
Reject nominees below legal majority with `NOMINEE_MINOR_NOT_ALLOWED`; require PAN and Aadhaar and
return `MISSING_REQUIRED_FIELD` when absent; validate their source-defined formats with
`INVALID_PAN_FORMAT` / `INVALID_AADHAAR_FORMAT`. Persist `minor_flag = false` and the calculated
`age_at_application` snapshot. Do not invent nominee-count, relationship, or KYC-approval rules.

## Test Cases
TDD: masked list/create success, missing member, missing auth, read/create permission separation,
minor rejection, required/invalid PAN and Aadhaar, no plaintext leakage in responses/audit, and
Member Profile list/empty/validation/error states with no mock nominee rows.

## Visual Acceptance Criteria
Match the existing prototype patterns and include loading, empty, error, unauthorized, validation, and success states where relevant.

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
