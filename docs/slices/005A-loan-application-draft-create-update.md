# Slice 005A: Loan Application Draft Create Update

## Status
Not Started

## Parent Epic
Epic 005: Loan Application Intake, Documents, Completeness, and Deficiencies
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal
Deliver this narrow capability as a small, testable Ralph implementation slice.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 004K2

## Prior Slice Facts
- Epic 004 now provides member profile foundations needed by intake: member detail, nominees,
  shareholding, land/crop, KYC profile/document metadata, sensitive PAN/Aadhaar reveal, and
  member bank-account/cancelled-cheque metadata.
- 004J bank metadata endpoints persist protected account numbers and expose only masked account
  values. Loan-application-specific cancelled-cheque behavior remains a placeholder because real
  application persistence starts in Epic 005.
- 004K closed the staff Borrower 360 UI wiring for Epic 004 member-master facts. Application,
  loan-account, repayment, communication, risk/exception, and audit rows on Borrower 360 are still
  source-backed empty states until Epic 005+ APIs exist.
- 004K2 must close the Borrower 360 bank-account holder-name DTO mismatch before this slice runs:
  the 004J backend/contract field is `account_holder_name`, and loan-application draft work must
  reuse that canonical field name for bank metadata summaries rather than the frontend-only
  `holder_name` alias.
- 004K2 is complete: the frontend `MemberBankAccountDetail` type, normalizer, Borrower 360 render
  path, and regression fixtures now use `account_holder_name`. 005A must not add a loan-application
  DTO or response summary that revives `holder_name`, copies full bank-account values, or broadens
  bank reveal behavior.
- `screen-spec.md` S11 says duplicate draft review should warn on same bank account used in other
  active borrower records, but 004J explicitly deferred that decision because active borrower and
  loan-application records did not exist yet. 005A may store enough draft references for a later
  duplicate-warning slice, but must not invent the duplicate-active-borrower rule.
- `api-contracts.md` §31.2 and §45 reserve bank-account IDs and idempotency for future
  disbursement initiation, not for draft application create/update.

## Source References
- docs/source/implementation-roadmap.md section 11
- docs/source/api-contracts.md sections 19-21
- docs/source/data-model.md loan origination tables
- docs/source/screen-spec.md application screens
- docs/source/screen-spec-member-portal.md application screens

## Prototype Reference
- sfpcl-lms/src/pages/applications/*
- sfpcl-lms/src/pages/borrower/portal/applications/*

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
Implement the named backend/API capability only.

Narrow this first slice to draft loan-application create/update and read-back of stored draft
facts. Do not implement submit, completeness check, reference-number generation, document checklist
verification, deficiency workflow, eligibility, loan limit, appraisal, sanction, disbursement, or
member portal flows unless this slice is split.

Concrete 005A scope:
- Add persistent draft loan-application storage with a stable application UUID, borrower member FK,
  draft status, requested amount, requested tenure/months when supplied, loan purpose/category text
  or source-backed enum if already defined in the docs opened for the run, optional crop-plan and
  land-holding references, optional bank-account/cancelled-cheque references by ID only, free-text
  borrower request notes, created/updated timestamps, and actor audit fields.
- Add `POST /api/v1/loan-applications/` to create a draft, `GET /api/v1/loan-applications/{id}/`
  to read it back, and `PATCH /api/v1/loan-applications/{id}/` to update draft facts only.
- Responses must include member identity summary and only masked member/bank metadata already
  exposed by Epic 004 APIs. Never copy or serialize full PAN, Aadhaar, bank account numbers,
  protected tokens, or hashes into the application response.
- Audit create/update with metadata-only values and no full sensitive identifiers. Workflow events
  may record draft creation/update state only if the existing workflow-event foundation supports it
  without inventing submit/completeness transitions.

## Database/Model Impact
Non-destructive model/migration changes for this capability, if needed.

If a draft stores borrower/member references, use existing `members.member_id` and existing member
profile facts rather than copying PAN/Aadhaar or full bank-account numbers into the application
record. Bank references must use IDs/masked metadata only.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Apply the role and object-access rules from `docs/source/auth-permissions.md`; classify unknown access as approval-required.

## Audit Requirements
Record audit/workflow events for critical create/update/approval/access actions.

## Validation Rules
Enforce source-doc business rules and block invalid state transitions.

For this foundation slice, validate required draft fields and malformed UUIDs, but do not invent
eligibility, duplicate-bank-account, payment-initiation, or disbursement-readiness rules. Record
any missing source-backed draft status or permission detail in `docs/working/ASSUMPTIONS.md`.

Specific validation to cover:
- Reject missing or unknown `borrower_member_id`.
- Reject malformed member, land-holding, crop-plan, bank-account, and cancelled-cheque UUIDs.
- Reject references that do not belong to the selected member.
- Reject non-positive requested amounts when an amount is supplied.
- Allow draft saves with incomplete KYC/documents; 005B+ own submit/completeness blockers.

## Test Cases
Unit/service/API/permission tests plus frontend tests where UI is touched.

Minimum regression tests:
- Create draft with a real member returns standard success envelope and metadata-only audit row.
- Patch draft updates only allowed draft fields and preserves borrower/member ownership.
- Unknown member and cross-member subresource references return standard validation errors.
- Response and audit metadata do not contain full PAN, Aadhaar, bank account numbers, token values,
  or hashes.
- User without the source-backed loan-application create/update permission is denied.

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
