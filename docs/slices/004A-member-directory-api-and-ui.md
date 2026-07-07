# Slice 004A: Member Directory API and UI

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
- 003L

## Source References
- docs/source/implementation-roadmap.md section 11
- docs/source/api-contracts.md sections 13-18, especially §13.1 `GET /api/v1/members/`
- docs/source/data-model.md member/KYC/shareholding tables
- docs/source/screen-spec.md member screens
- docs/working/digests/epic-004-member-kyc-master.md

## Prototype Reference
- sfpcl-lms/src/pages/members/*
- sfpcl-lms/src/data/mockData.ts

## Screens Involved
Member Directory / member list area.

## Frontend Scope
Wire the existing Member Directory prototype pattern to the backend list API. Reuse existing table,
filter/search, card, loading, empty, error, and unauthorized patterns; do not introduce new styling.
Show only list fields returned by the backend contract until a later detail/profile slice owns
deeper member/KYC/shareholding panels.

Use the existing `sfpcl-lms/src/pages/members/MemberDirectory.tsx` table/card patterns. Remove the
backend-wired directory path's dependency on `mockData`; do not keep mock-only exposure totals,
supply-year values, land/crop filters, open-loan counts, or Borrower 360 links unless backed by the
new API response. Preserve masked contact display from §13.1 (`mobile_number` masked in the source
example).

## Backend/API Scope
Implement `GET /api/v1/members/?search=&member_type=&membership_status=&kyc_status=&default_status=&page=1&page_size=20`
as the narrow directory read API. Return standard paginated envelopes. The source §13.1 response
item includes `member_id`, `member_number`, `member_type`, `legal_name`, `display_name`,
`folio_number`, `membership_status`, `kyc_status`, `rekyc_due_date`, `default_status`,
`mobile_number`, `email`, `share_summary{number_of_shares, holding_mode, available_share_count}`,
and `active_member_status{status, verified_at}`.

Do not implement create/update member profile, nominee, witness, KYC verification, share
certificate, demat, landholding, crop plan, loan application, or borrower 360 behavior in 004A.
Do not implement sensitive-field reveal in 004A; §13.5 is owned by a later masking/reveal slice.

## Database/Model Impact
Non-destructive model/migration changes for the member directory fields needed by §13.1 only, if
models do not already exist. Keep share/active-member nested values as explicit shell data or
well-named nullable fields unless the source-backed member/shareholding tables are implemented in
the same narrow path.

If adding a model in 004A, include the source §10.1 directory fields required for §13.1 and the
minimum safe nested summary fields for `share_summary`/`active_member_status`; leave full
shareholding, active-member calculation, KYC documents, bank accounts, land/crop, and profile-detail
tables to their owning slices. PAN/Aadhaar must not be stored in plaintext test fixtures; use
synthetic encrypted/hash placeholder values only if fields are required by the schema.

## API Contracts
Create or update the API contract for the member list endpoint, including supported filters,
standard pagination, unknown-parameter handling, and masked sensitive fields. Do not add mutation
contracts in this slice.

## Permissions
Apply role and object-access rules from `docs/source/auth-permissions.md`; classify unknown access
as approval-required. Directory results must be permission-filtered or blocked rather than exposing
all members to every authenticated user.

If the source permission catalogue lacks an exact member-directory read code, choose the narrowest
source-backed member/profile read permission available, record the assumption, and test `401`/`403`.
Do not reuse dashboard, report-export, document-download, or import-administration permissions.

## Audit Requirements
Read-only list access should not create workflow events. If the implementation exposes sensitive
unmasked fields or export-style access, it must audit that reveal/export action; otherwise record
the read/no-audit decision in the review packet.

## Validation Rules
Validate query parameters and enum filters. Do not invent eligibility, KYC approval, active-member,
default, or share-availability business rules; leave those to later slices unless directly stated by
the source docs opened during 004A.

Reject unknown query parameters with the standard `400 VALIDATION_ERROR` pattern used by existing
list APIs. Validate only the supported §13.1 filters: `search`, `member_type`,
`membership_status`, `kyc_status`, `default_status`, `page`, and `page_size`.

## Test Cases
TDD backend tests first: authenticated list success, pagination envelope, supported filter behavior,
unknown/invalid filter rejection, and unauthorized/forbidden access. Frontend tests should cover
loading, API success rows, empty state, error state, and no fallback to `mockData` for the wired
directory path.

Add at least one regression asserting sensitive identifiers such as PAN/Aadhaar are absent from the
directory response and that `mobile_number` is masked or test-safe. Save API response examples using
synthetic member data only.

Add a frontend regression that the API-backed directory renders rows from `GET /api/v1/members/`
and does not import or render `sfpcl-lms/src/data/mockData.ts` member-directory fixtures on the
wired path.

## Visual Acceptance Criteria
Match the existing prototype patterns and include loading, empty, error, unauthorized, validation, and success states where relevant.

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched. For 004A, save at
least the populated directory, empty directory, API error, and unauthorized/forbidden state using
existing visual patterns.

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
