# Slice 004D2: Member Profile and Nominee Contract Hardening

## Status
Not Started

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal
Close the architecture-review findings from `2026-07-09_114836_architecture_review` before the queue
continues into witness/shareholding work.

## User Value
Sensitive nominee identity metadata stays out of audit logs, and member profile action buttons do
not imply loan-start eligibility before the loan-application and eligibility modules exist.

## Depends On
- 004D

## Source References
- `docs/source/auth-permissions.md` §30.2-§30.3 audit contents and sensitive-data audit rules
- `docs/source/api-contracts.md` §13.3 and §44 `available_actions[]`
- `docs/source/api-contracts.md` §14.1-§14.3 nominee APIs and validation rules
- `docs/working/API_CONTRACTS.md` Member Profile Detail API and Member Nominee API
- `docs/working/digests/epic-004-member-kyc-master.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-09_114836_architecture_review`

## Prototype Reference
- `sfpcl-lms/src/pages/members/MemberProfile.tsx`
- `sfpcl-lms/src/pages/members/MemberProfile.test.tsx`

## Screens Involved
Member Profile overview action area and Nominee tab.

## Frontend Scope
Adjust only the existing Member Profile action rendering/tests if backend `available_actions[]`
changes. Reuse the current action-button mapping and existing empty/no-action behavior; do not add
new styling, new buttons, or new explanatory UI.

## Backend/API Scope
1. Nominee audit hardening:
   - Add a failing-first regression proving `members.nominee.created` audit metadata does not contain
     `pan_hash`, `aadhaar_hash`, `pan_encrypted`, `aadhaar_encrypted`, full PAN, full Aadhaar, or
     hash values derived from the submitted identifiers.
   - Remove nominee PAN/Aadhaar hash fields from `AuditLog.new_value_json`.
   - Keep nominee API responses masked and keep nominee model hash storage unchanged for
     duplicate/search support.
2. Member profile action hardening:
   - Add a failing-first regression proving `GET /api/v1/members/{member_id}/` does not decide
     `create_loan_application` availability from `membership_status`, `kyc_status`, or
     `default_status` before the loan-application and eligibility slices exist.
   - Prefer returning an empty `available_actions[]` for member profile detail until `005A` owns the
     create-application endpoint and a later eligibility slice owns source-backed blockers. If an
     action placeholder remains, it must be disabled for an implementation-not-ready reason and must
     not encode KYC/default/active-member eligibility logic.

## Database/Model Impact
No migrations expected. Do not change stored nominee hash columns; only remove them from audit
metadata.

## API Contracts
Update `docs/working/API_CONTRACTS.md` if the member profile `available_actions[]` behavior changes.
Keep the nominee contract explicit that audit metadata contains no identity hash fields.

## Permissions
Do not add or seed new permissions. Do not grant or infer `applications.loan_application.create`
action availability from member profile reads.

## Audit Requirements
Nominee creation must still write one `members.nominee.created` audit row with actor, entity, member
ID, nominee ID, nominee name, age/minor/KYC/signature metadata, IP, and user agent, but without PAN,
Aadhaar, encrypted tokens, or hash values.

## Validation Rules
No validation changes except tests proving existing nominee validation and masking still work.

## Test Cases
TDD backend tests first:
- Nominee create audit rejects identity hash/encrypted/plain fields in `new_value_json`.
- Nominee create still masks response PAN/Aadhaar and writes exactly one audit row.
- Member profile `available_actions[]` is empty or neutral/deferred even when a user has
  `applications.loan_application.create` and the member is active/KYC-verified/no-default.
- Member profile does not enable/disable loan-start based on KYC/default/member status before the
  owning workflow exists.

Frontend tests only if the rendered action area changes:
- Member Profile does not show an enabled Start Application button when the backend returns no
  action or a disabled/deferred action.
- Existing profile/nominee loading, empty, error, and validation states remain unchanged.

## Visual Acceptance Criteria
No new visual design. Existing action area should simply omit or disable the premature action using
current button styles.

## Evidence Required
Red/green backend test logs, frontend logs if touched, full backend/frontend quality gates, and a
review packet explaining both architecture-review findings were closed.

## Risk Level
Medium

## Acceptance Criteria
- Nominee create audit metadata no longer includes identity hash/encrypted/plain fields.
- Member profile detail no longer encodes premature loan-start eligibility.
- API contracts and tests match the corrected behavior.
- No production scope beyond this hardening is introduced.

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
