# Slice 004E: Witness Shareholder Validation

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
- 004D

## Source References
- docs/source/implementation-roadmap.md section 11
- docs/source/api-contracts.md sections 13-18
- docs/source/data-model.md member/KYC/shareholding tables
- docs/source/screen-spec.md member screens

## Prototype Reference
- sfpcl-lms/src/pages/members/*
- sfpcl-lms/src/data/mockData.ts

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
First confirm an owning loan-application boundary and a source-backed witness endpoint exist by the
time this slice runs. Implement witness capture only against a real loan application and real member
/shareholding records; do not create a member-level witness API or boolean-only verification stub.

## Database/Model Impact
Add the data-model §10.5 witness fields only when their required loan-application FK can reference
an implemented table: application FK, optional member FK, name, encrypted+hashed PAN/Aadhaar,
shareholder verification flag/status, verifier/time, and created time.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Apply application object access and the exact witness permission available at run time. Source roles
allow Credit/Compliance capture and read-only audit access, but no exact witness endpoint permission
code was confirmed in the 004C source pass; record/stub this gap rather than borrowing nominee or KYC
permissions.

## Audit Requirements
Record audit/workflow events for critical create/update/approval/access actions.

## Validation Rules
Witness must resolve to an existing SFPCL shareholder and requires KYC. Documentation completion
must not treat the witness as complete until verification is complete. Do not accept a caller-supplied
`shareholder_verified_flag` without checking persisted shareholding facts.

## Test Cases
TDD: existing-shareholder success, non-shareholder rejection, missing application/member,
permission/object-access denial, encrypted identity persistence/no plaintext response leakage, and
verification metadata. If application/shareholding prerequisites are still absent, sharpen/reorder
the queue instead of implementing an unverifiable witness shell.

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
