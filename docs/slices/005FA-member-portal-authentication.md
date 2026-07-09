# Slice 005FA: Member Portal Authentication (Login, Activation, Recovery, Security Settings)

## Status
Not Started

## Parent Epic
Epic 005: Loan Application Intake, Documents, Completeness, and Deficiencies (member portal entry)
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal
Give borrowers/members a real way into the portal: portal login (MP00), first-time account activation tied to an existing member record (MP01), password/OTP recovery (MP02), and profile security settings (MP25). Without this slice no member-portal screen from 005G onward is reachable by a real borrower.

## User Value
A member invited to the portal can activate their account, log in securely, recover access, and manage their password — the front door for every borrower self-service feature.

## Depends On
- 005F2

## Prior Slice Facts To Preserve
- MP08 copy says a borrower receives the official `LO...` reference only after submitted details
  and documents are checked. Portal status screens must therefore handle submitted applications
  with no reference number.
- 005E generates references only after staff completeness pass. Borrower auth must not grant access
  to staff completeness/pass endpoints.
- 005F is expected to create structured deficiency records before borrower deficiency response
  screens are wired; portal tokens introduced here must carry enough member/object scope for later
  own-application deficiency reads and responses.
- 005F implemented structured deficiency records and staff endpoints:
  `POST /api/v1/loan-applications/{loan_application_id}/return-with-deficiencies/`,
  `GET /api/v1/loan-applications/{loan_application_id}/deficiencies/`, and
  `POST /api/v1/deficiencies/{deficiency_id}/resolve/`. Borrower portal auth must not grant those
  staff complete-check actions, but it must expose a member scope that future portal endpoints can
  use to read/respond only to the borrower's own returned applications.
- 005F2 corrected returned deficiency applications to the source-backed `application_status =
  incomplete_returned`, kept `completeness_status = incomplete`, and kept `current_stage =
  initial_loan_request`. Portal auth must not depend on returned applications still looking like
  plain `submitted` applications.
- 005F2 blocks repeat staff return attempts from `incomplete_returned` until a future source-backed
  borrower resubmission flow defines the transition back to submitted/completeness review. Portal
  auth must provide member scope only; it must not grant borrowers staff complete-check or repeat
  return authority.
- Member portal source access boundaries say borrowers can access their own profile, own loan
  applications, own documents, own loan accounts/repayments, own notices, and own grievances only.
  Treat every cross-member portal read/write as object-access denied.

## Source References
- docs/source/screen-spec-member-portal.md screens MP00, MP01, MP02, MP25 (including OTP and activation rules)
- docs/source/auth-permissions.md section 4.2 (external roles: Borrower/Member) and session policy sections
- docs/source/api-contracts.md section 11 (authentication API conventions)
- docs/source/data-model.md identity/access tables (portal account link to member record)
- docs/source/security-privacy.md (credential and OTP handling rules)

## Prototype Reference
- sfpcl-lms/src/pages/borrower/portal/auth/MP00_Login.tsx
- sfpcl-lms/src/pages/borrower/portal/auth/MP01_Activation.tsx
- sfpcl-lms/src/pages/borrower/portal/auth/MP02_ForgotPassword.tsx
- sfpcl-lms/src/pages/borrower/portal/auth/MP25_SecuritySettings.tsx

## Concrete Requirements
1. Backend: portal account model linked one-to-one to a Member record; activation flow validating member identity per MP01 spec; login/refresh/logout reusing the 002B/002B2 JWT foundation with the Borrower role; password reset flow per MP02. If the docs do not specify an OTP delivery channel, implement the mechanism behind the 003I notification adapter shell and log the channel choice in ASSUMPTIONS.md — do not invent a provider.
2. Borrower tokens must carry the member/borrower object scope so every portal API can enforce own-data-only access.
   Token/session payloads should include the linked `member_id` and a borrower/member portal role
   marker, not staff role grants.
3. Frontend: wire MP00/MP01/MP02/MP25 to the real APIs; protected portal routes redirect to MP00 when unauthenticated; loading, error, invalid-credential, expired-link, and success states covered per existing prototype patterns.
4. All auth events (activation, login success/failure, reset, password change, session revocation) create audit events.

## Test Cases
- Activation succeeds only for a valid invited member; already-active and unknown members are rejected.
- Borrower login yields tokens scoped to own member record; a borrower calling a staff API or another member's data gets 403 (object-permission test via 002I harness).
- Password reset token single-use and expiring; replay rejected.
- Route guard: unauthenticated portal access redirects to MP00.

## Out of Scope
Portal dashboard/profile content (005FB), staff auth changes, MFA beyond what the source docs require, real SMS/email delivery.

## Risk Level
High

## Acceptance Criteria
- A seeded member can activate, log in, recover, and change their password end to end against the real backend.
- Borrower access is provably own-data-only.
- All gates pass; screenshots of MP00/MP01/MP02/MP25 states saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
