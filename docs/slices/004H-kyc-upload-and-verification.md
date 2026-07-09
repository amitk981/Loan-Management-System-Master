# Slice 004H: KYC Upload and Verification

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
- 004G

## Source References
- docs/source/implementation-roadmap.md section 11
- docs/source/api-contracts.md sections 13-18
- docs/source/data-model.md member/KYC/shareholding tables
- docs/source/screen-spec.md member screens

## Prototype Reference
- sfpcl-lms/src/pages/members/*
- sfpcl-lms/src/data/mockData.ts

## Screens Involved
Member Profile — KYC tab; KYC verification panel may remain deferred to 004K if this slice stays
backend-only.

## Frontend Scope
If KYC profile/document APIs land in this slice, replace the current backend-shell Member Profile
KYC tab with API-backed profile/document metadata and upload/verify actions using existing card,
empty panel, alert, and form patterns. Do not implement sensitive reveal UI here; 004I owns reveal
reason, expiry, and audit behavior.

## Backend/API Scope
Implement `GET /api/v1/kyc-profiles/?party_type=member&party_id={member_id}`,
`POST /api/v1/kyc-profiles/`, `PATCH /api/v1/kyc-profiles/{kyc_profile_id}/`,
`POST /api/v1/kyc-profiles/{kyc_profile_id}/documents/`, and
`POST /api/v1/kyc-documents/{kyc_document_id}/verify/` from `api-contracts.md` §18.1-§18.4.
Include §18.5 re-KYC review endpoints only if they remain small; otherwise split re-KYC task
management to a follow-up slice.

## Database/Model Impact
Add non-destructive model/migration changes for `kyc_profiles` from `data-model.md` §12.1:
party type, party ID, KYC status, optional encrypted CKYC identifier, CKYC consent flag, optional
beneficial ownership flag, risk rating, last verified timestamp/user, re-KYC due date, and rejection
reason. Add `kyc_documents` from §12.2: profile FK, document type, document file FK,
self-attestation flag, verification status, verifier/timestamp, and remarks.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Use source/catalogue KYC permissions: `kyc.profile.read`, `kyc.profile.create`,
`kyc.profile.update`, `kyc.document.upload`, `kyc.document.read`, and `kyc.document.verify`.
Do not use `kyc.document.download`, `kyc.sensitive.reveal`, or `kyc.rekyc.manage` unless the
corresponding endpoint is implemented and tested in this slice.

## Audit Requirements
Audit profile create/update, document upload, and document verification with metadata only. Do not
store PAN/Aadhaar plaintext, encrypted token keys, or identity hashes in audit logs.

## Validation Rules
Require `party_type=member` for 004H unless nominee/witness/signatory KYC is explicitly added.
Require `party_id`, CKYC consent flag, document type, file/document ID, and self-attestation for PAN
or Aadhaar documents. KYC must be complete before disbursement and re-KYC recurs every two years,
but 004H must not invent disbursement blockers or task scheduling rules beyond persisted profile
status/due date fields.

## Test Cases
TDD: profile read/create/update success, missing member/party, missing auth, permission separation,
document upload success, unsupported document type, missing self-attestation for PAN/Aadhaar,
document verification success/rejection, audit metadata without sensitive values, and frontend
loading/empty/error/validation/success states when UI is touched.

## Visual Acceptance Criteria
None.

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched.

## Risk Level
High

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
