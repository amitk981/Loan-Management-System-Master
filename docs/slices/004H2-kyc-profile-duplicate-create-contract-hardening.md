# Slice 004H2: KYC Profile Duplicate Create Contract Hardening

## Status
Complete

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal
Close the architecture-review finding from `2026-07-09_141049_architecture_review` before sensitive
reveal work proceeds.

## User Value
Users get a predictable validation response when a member already has a KYC profile, rather than an
unhandled server error from the database constraint.

## Depends On
- 004H

## Source References
- `docs/source/api-contracts.md` §18.1-§18.4 KYC profile/document endpoints
- `docs/source/data-model.md` §12.1 KYC profile fields
- `docs/working/digests/epic-004-member-kyc-master.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-09_141049_architecture_review`

## Prototype Reference
- `sfpcl-lms/src/pages/members/MemberProfile.tsx`
- `sfpcl-lms/src/pages/members/MemberProfile.test.tsx`

## Screens Involved
Member Profile KYC tab create-profile form.

## Frontend Scope
Only adjust existing KYC create error handling/tests if the backend field error shape changes. Reuse
existing Member Profile alert, empty-panel, form-field, and validation-message patterns. No new
styling or screen layout.

## Backend/API Scope
Harden `POST /api/v1/kyc-profiles/` for member parties:
- detect an existing active `KycProfile` for `(party_type="member", party_id=<member_id>)` before
  calling `KycProfile.objects.create`;
- return a standard `400 VALIDATION_ERROR` envelope with a clear field or non-field error instead
  of allowing the unique constraint to raise an unhandled `IntegrityError`;
- keep `GET /api/v1/kyc-profiles/?party_type=member&party_id=...` as the read path for the existing
  profile;
- preserve one-profile-per-member storage and do not add multiple-profile/re-KYC task behavior here.

## Database/Model Impact
No migration expected. Keep the existing `kyc_profiles_unique_party` unique constraint as the final
database guard.

## API Contracts
Update `docs/working/API_CONTRACTS.md` to state duplicate member-party profile creates return a
standard validation error and clients should read/update the existing profile.

## Permissions
Keep existing 004H permissions: `kyc.profile.create` for create and `kyc.profile.read` for read.
Do not add new permission codes.

## Audit Requirements
Duplicate create rejection must not create `kyc.profile.created`, workflow events, or any audit row
that implies a new profile was created.

## Validation Rules
Reject duplicate `(party_type, party_id)` create requests with `400 VALIDATION_ERROR`. Missing auth,
missing create permission, unsupported party type, unknown/soft-deleted member, missing consent, and
unsupported risk rating must continue to behave as 004H already defined.

## Test Cases
TDD backend tests first:
- a second create for the same member-party returns `400 VALIDATION_ERROR` with a field or
  non-field error and no unhandled exception;
- duplicate create leaves exactly one `KycProfile`;
- duplicate create does not create a second `kyc.profile.created` audit row;
- existing 004H profile read/update/document upload/verify tests still pass.

Frontend test only if the validation message mapping changes:
- KYC tab displays the existing validation/alert pattern for duplicate create and does not create a
  new local profile state.

## Visual Acceptance Criteria
No visual design changes.

## Evidence Required
Red/green backend duplicate-create logs and full quality-gate logs.

## Risk Level
Medium

## Acceptance Criteria
- Duplicate KYC profile create attempts return a standard validation envelope.
- No duplicate profile/audit rows are created.
- Existing KYC read/update/document behavior remains unchanged.
- No production scope beyond this contract hardening is introduced.

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
