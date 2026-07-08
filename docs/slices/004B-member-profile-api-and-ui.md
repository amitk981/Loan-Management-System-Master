# Slice 004B: Member Profile API and UI

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
- 004A

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
Relevant prototype screen area for this capability.

## Frontend Scope
Wire the existing `sfpcl-lms/src/pages/members/MemberProfile.tsx` overview/profile shell to the
backend detail API using existing tabs, cards, badges, alerts, table, and masked-field patterns. Do
not introduce new styling or components. Remove the backend-wired profile path's dependency on
`mockData`; any tab whose data is not backed by 004B should render an existing empty/placeholder
state rather than synthetic member, loan, communication, land, nominee, or audit rows.

Preserve masked PAN/Aadhaar display. Do not reveal full sensitive values in the frontend unless
004B explicitly implements §13.5 reveal with permission, reason capture, expiry, no caching, and
audit logging; otherwise leave reveal controls disabled/hidden and record the deferred reveal path.

## Backend/API Scope
Implement `GET /api/v1/members/{member_id}/` only, unless 004A already delivered a compatible member
model/service that this slice can reuse. Match §13.3 response shape: member identifiers, member
type, legal name, folio number, membership/KYC/default status, masked `pan` and `aadhaar` objects
with `can_view_full`, registered address, type-specific profile shell fields, and
`available_actions[]`.

004A delivered the `sfpcl_credit.members` app, `Member` model, `members.member.read` permission
gate, and read-only list serialization. Reuse that app/service boundary and add detail-only fields
or serializers there rather than creating a second member module. `GET /api/v1/members/{member_id}/`
must not include unmasked `pan_encrypted`, `aadhaar_encrypted`, `pan_hash`, or `aadhaar_hash`; the
response should expose only masked objects such as `{masked, can_view_full}` per §13.3.

Do not implement member create/update, nominee APIs, shareholding mutations, active-member
calculation, land/crop APIs, KYC profile/document upload or verification, loan application start,
Borrower 360, communications history, or audit timeline wiring in 004B unless the slice is
explicitly rewritten before the run.

## Database/Model Impact
Non-destructive model/migration changes for the member profile detail fields needed by §13.3 only,
if 004A did not already create them. Keep individual farmer profile fields and FPC/producer
institution fields explicit by member type. Do not add nominee, witness, shareholding, KYC document,
bank account, land/crop, loan, or communication tables in 004B unless required by the already
implemented 004A schema contract.

## API Contracts
Create or update the API contract for `GET /api/v1/members/{member_id}/`, including masked sensitive
field shape, `available_actions[]`, `401`, `403`, and not-found behavior. If §13.5 reveal is
deferred, state that explicitly in the contract/assumptions rather than documenting it as
implemented.

## Permissions
Apply the role and object-access rules from `docs/source/auth-permissions.md`; classify unknown
access as approval-required. If the exact member-detail read permission is absent, choose the
narrowest source-backed member/profile read permission available, record the assumption, and test
`401`/`403`. Sensitive full-value access requires separate permission and audit; masked detail read
must not imply reveal authority.

## Audit Requirements
Masked read-only profile access should not create workflow events. If §13.5 reveal is implemented,
record an audit row with actor, member, field name, reason, expiry, and no full sensitive value. If
reveal is deferred, include a review-packet note that 004B exposes masked values only.

## Validation Rules
Validate member UUID/path parameters and return standard errors. Do not invent eligibility,
active-member, KYC approval, default, nominee, witness, shareholding, land/crop, or loan-application
business rules in 004B. PAN/Aadhaar in responses must stay masked by default.

Use `404 NOT_FOUND` for a valid UUID that does not identify a non-deleted member. Invalid path UUIDs
may be handled by Django routing if the route uses `<uuid:member_id>`. Detail reads require
`members.member.read`; do not reuse dashboard/report/document/import permissions.

## Test Cases
TDD backend tests first: authenticated detail success, masked `pan`/`aadhaar` shape,
`available_actions[]` shape, not found, `401`, and `403`. If frontend is touched, test loading,
success, empty/deferred tabs, error, unauthorized/forbidden, masked sensitive display, and no
fallback to `mockData` on the wired profile path. Add reveal tests only if §13.5 is implemented in
this slice.

Add a frontend regression that backend-wired profile tabs render API data or existing empty states
only; they must not render synthetic loan, KYC, land/crop, nominee, communication, or audit rows
from `sfpcl-lms/src/data/mockData.ts` unless a later slice implements the matching backend path.

## Visual Acceptance Criteria
Match the existing prototype patterns and include loading, empty, error, unauthorized, validation, and success states where relevant.

## Evidence Required
Test output, API response examples with synthetic member data, and screenshots when frontend is
touched. Screenshots must use existing profile layout and masked identifiers, including populated
overview, deferred/empty tab, API error, and unauthorized/forbidden states.

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
