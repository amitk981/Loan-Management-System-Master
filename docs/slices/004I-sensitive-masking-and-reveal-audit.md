# Slice 004I: Sensitive Masking and Reveal Audit

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
- 004H2

## Prior Slice Facts
- 004H added member-party KYC profile/document APIs and a Member Profile KYC tab, but did not add
  sensitive reveal. Keep 004I focused on member PAN/Aadhaar reveal from the existing masked member
  profile path; do not reopen KYC document upload/verify or document download behavior.
- 004H2 is expected to harden duplicate member-party KYC profile creates before this slice runs.
  Do not reopen that create-profile contract here except to keep the KYC tab from regressing while
  adding reveal controls.
- 004H2 closes the duplicate KYC profile create contract with `400 VALIDATION_ERROR` on `party_id:
  "A KYC profile already exists for this member."` and keeps `GET /api/v1/kyc-profiles/?party_type=member&party_id=...`
  as the existing-profile read path. 004I must preserve that behavior while adding member
  PAN/Aadhaar reveal only.

## Source References
- docs/source/implementation-roadmap.md section 11
- docs/source/api-contracts.md sections 13-18
- docs/source/data-model.md member/KYC/shareholding tables
- docs/source/screen-spec.md member screens

## Prototype Reference
- sfpcl-lms/src/pages/members/*
- sfpcl-lms/src/data/mockData.ts

## Screens Involved
Member Profile sensitive identifier read path; optional reveal-control wiring only if it can reuse
the existing Member Profile card, alert, and form/modal patterns without new styling.

## Frontend Scope
Add or update frontend behavior only for `POST /api/v1/members/{member_id}/reveal-sensitive-field/`
from `api-contracts.md` §13.5. The frontend must:
- keep PAN/Aadhaar masked by default;
- require a reason before reveal;
- avoid storing full values in local storage, mock data, or long-lived state;
- show expiry/temporary access messaging only if returned by the backend contract;
- use existing Member Profile UI patterns and no new styling.

## Backend/API Scope
Implement `POST /api/v1/members/{member_id}/reveal-sensitive-field/` from `api-contracts.md`
§13.5 for member PAN and Aadhaar only. Request fields:
- `field_name`: `pan` or `aadhaar`;
- `reason`: non-empty text.

Return the full sensitive value only in the immediate success response with an expiry timestamp or
TTL field; do not change the existing masked `GET /api/v1/members/{member_id}/` response shape
except setting `can_view_full` accurately if the backend can do so without caching full values.
Do not implement nominee, witness, signatory, KYC document download, export reveal, or generic
sensitive-data APIs in this slice.

## Database/Model Impact
Prefer no schema change unless needed for short-lived reveal sessions. Existing member sensitive
values are stored as protected/encrypted tokens and hashes; do not add plaintext columns. If a
temporary reveal grant table is introduced, include member FK, actor FK, field name, reason,
expiry timestamp, created timestamp, and revoked/used marker as needed.

## API Contracts
Update `docs/working/API_CONTRACTS.md` with the request/response shape, permission checks, expiry
semantics, and audit contents.

## Permissions
Use source permissions exactly:
- `members.sensitive.reveal_pan` for `field_name=pan`;
- `members.sensitive.reveal_aadhaar` for `field_name=aadhaar`.

Also require the actor to pass the same base member read/object-access check used by member detail.
Do not treat broad `members.member.read`, KYC, document, admin, or export permissions as reveal
permissions.

## Audit Requirements
Every successful reveal and every denied reveal attempt must write an audit row with metadata only:
actor, member ID, field name, reason, outcome, request ID/IP/user-agent, and expiry when applicable.
Audit logs must never include full PAN/Aadhaar, encrypted token keys, hashes, or derived submitted
identifier values. Do not write workflow events for simple sensitive-field reveal.

## Validation Rules
Reject missing/unsupported `field_name`, blank `reason`, missing auth, missing base member read
access, missing field-specific reveal permission, unknown/soft-deleted member, and unavailable
source value. Full values must not be cached by the frontend; backend response should include
no-cache headers if the existing response helper can support them safely in this slice.

## Test Cases
TDD: missing auth, missing base member read permission, missing field-specific reveal permission,
PAN reveal success, Aadhaar reveal success, unsupported field, blank reason, unknown/deleted
member, masked profile remains masked, audit metadata for success and denial without sensitive
values, no workflow event, and frontend reason-required/success/expiry/error states if UI is
touched.

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
