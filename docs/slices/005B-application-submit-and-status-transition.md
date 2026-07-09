# Slice 005B: Application Submit and Status Transition

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
- 005A

## Prior Slice Facts
- 005A should create/read/update draft loan applications only. 005B must depend on those persisted
  draft fields and must not reintroduce member-master mock data or duplicate the Epic 004 member
  subresource APIs.
- Epic 004 sensitive data boundaries remain binding: submit responses and audit/workflow metadata
  must not include full PAN, Aadhaar, full bank account numbers, protected token values, or hashes.
- 004K2 closed the bank holder-name frontend/API contract mismatch. If 005B returns any
  application summary that includes selected bank metadata, the holder field must remain
  `account_holder_name`, with account-number data limited to masked/last-four metadata and
  `can_view_full: false`.
- Completeness, reference-number generation, document checklist verification, deficiency workflow,
  eligibility, loan limit, appraisal, sanction, disbursement, and payment initiation remain outside
  005B unless explicitly split into this slice later.
- 005A implemented `LoanApplication` with nullable `application_reference_number`,
  `application_status = draft`, `current_stage = initial_loan_request`, and
  `completeness_status = not_started`. Create/read/update APIs serialize member summaries and
  optional land/crop/bank/cancelled-cheque references with masked bank metadata only.
- 005A recorded A-035: formal `LO...` reference generation is deferred to 005C or the source-backed
  transition that owns the sequence. Do not generate or require a formal reference in 005B unless
  the source pass explicitly changes that assumption.
- Use `docs/working/digests/epic-005-application-intake.md` before reopening large source docs.

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

Concrete 005B scope:
- Add a submit action for 005A draft loan applications, such as
  `POST /api/v1/loan-applications/{application_id}/submit/`, using the existing state-machine guard
  foundation where practical.
- Permit only `draft -> submitted`, unless the source pass finds a more exact canonical submitted
  status. Preserve `current_stage = initial_loan_request` unless the opened source sections name a
  different pre-completeness stage; do not advance to `credit_assessment` or appraisal in 005B.
- Do not generate final application/reference numbers in this slice; leave nullable
  `application_reference_number` untouched and preserve 005C as the sequence/register owner.
- Persist submitted actor/timestamp and return a standard envelope with the updated application
  status plus masked member/bank metadata only.
- Write metadata-only audit and workflow event entries for submit; no workflow events for failed
  validation beyond existing audit conventions unless the source docs require them.
- Reuse the 005A serializer/service boundary so submit responses keep `account_holder_name`, masked
  account values, and no sensitive token/hash fields.

## Database/Model Impact
Non-destructive model/migration changes for this capability, if needed.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Apply the role and object-access rules from `docs/source/auth-permissions.md`; classify unknown access as approval-required.

## Audit Requirements
Record audit/workflow events for critical create/update/approval/access actions.

## Validation Rules
Enforce source-doc business rules and block invalid state transitions.

Specific validation to cover:
- Reject submit for unknown application IDs.
- Reject submit when the application is not in draft status.
- Reject submit when `member_id`, positive `required_loan_amount`, nonblank `declared_purpose`, and
  nonblank `purpose_category` are missing, because those are the source-backed S10/MP06 loan-request
  facts already persisted in 005A. Do not require KYC/document completeness, nominee, land/crop, or
  bank facts in 005B unless the source sections opened during that run explicitly put them in
  submit rather than completeness/document slices.
- Record any unresolved canonical submitted status name or permission mapping in
  `docs/working/ASSUMPTIONS.md` rather than inventing a business rule.

## Test Cases
Unit/service/API/permission tests plus frontend tests where UI is touched.

Minimum regression tests:
- Draft submit succeeds once, changes status, stamps submitted actor/time, and writes
  metadata-only audit/workflow evidence.
- Re-submitting or submitting a non-draft application returns a standard transition error envelope.
- User without the source-backed submit permission is denied.
- Submit response/audit/workflow metadata contains no full sensitive member or bank values.
- Submitted draft can still be read through `GET /api/v1/loan-applications/{id}/`, but `PATCH` must
  reject it because 005A update is draft-only.

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
