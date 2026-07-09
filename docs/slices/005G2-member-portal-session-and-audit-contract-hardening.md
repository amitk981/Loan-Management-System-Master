# Slice 005G2: Member Portal Session and Audit Contract Hardening

## Status
Not Started

## Parent Epic
Epic 005: Loan Application Intake, Documents, Completeness, and Deficiencies
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal
Close the architecture-review findings from `2026-07-10_005716_architecture_review` before
staff-side rejection-note work continues.

## User Value
Suspended or inactive portal accounts cannot keep using an already-issued session, and borrower
portal actions are auditable under the source-backed portal event names.

## Depends On
- 005G

## Prior Slice Facts To Preserve
- 005FA added `PortalAccount`, portal login, activation, password reset, and password change.
  Portal login already blocks inactive/suspended accounts through `PortalAccount.can_authenticate()`.
- 005FB and 005G portal data/application endpoints already call the active `PortalAccount.member_id`
  scope helper and deny staff/non-portal users with `403 PERMISSION_DENIED`.
- 005G application create/update/submit reuses existing 005A/005B application services, creating
  valid metadata-only audit rows and workflow events with the linked portal user as actor.
- Do not broaden staff permissions, portal own-data permissions, or application object access.

## Source References
- `docs/source/screen-spec-member-portal.md` MP00 validations: inactive/suspended portal users are
  blocked.
- `docs/source/screen-spec-member-portal.md` §14.1 Login and Access: inactive or unauthorised portal
  accounts are blocked.
- `docs/source/screen-spec-member-portal.md` §11 Audit Events: source portal action names include
  `portal.login.success`, `portal.login.failed`, `portal.account.activated`,
  `portal.application.draft_created`, `portal.application.saved`,
  `portal.application.submitted`, and `portal.password.changed`.
- `docs/working/digests/epic-005-application-intake.md` architecture-review extract for
  `2026-07-10_005716_architecture_review`.

## Prototype Reference
- `sfpcl-lms/src/pages/borrower/portal/auth/MP00_Login.tsx`
- `sfpcl-lms/src/pages/borrower/portal/auth/MP25_SecuritySettings.tsx`
- `sfpcl-lms/src/pages/borrower/portal/applications/MP05_NewApplication.tsx`

## Screens Involved
None required unless frontend tests need copy/state updates. This is primarily backend/API contract
hardening.

## Frontend Scope
No visual change expected. If API error handling is touched, preserve existing portal auth and
application screen patterns.

## Backend/API Scope
- Add a single portal-session validity boundary used by:
  - portal login token issuance;
  - access-token session validation for `/api/v1/auth/me/`;
  - portal password change;
  - portal own-data/application endpoints.
- If the linked `PortalAccount` is no longer active, existing access/refresh sessions must stop
  exposing portal `member_id`, `portal_account_id`, `portal_role`, or portal own-data permissions.
  Prefer revoking active sessions with a clear reason such as `portal_account_status_changed`.
- Suspended portal accounts must receive `401 INVALID_TOKEN` for session-bound current-user reads
  and `403 PERMISSION_DENIED` for portal data routes after validation, matching existing envelope
  conventions. Choose the exact route-level status by existing auth helper semantics and document it
  in API contracts.
- Align portal audit action names with the source audit table:
  - activation complete: `portal.account.activated`;
  - login success/failure: `portal.login.success` / `portal.login.failed`;
  - password change: `portal.password.changed`;
  - portal application draft create: `portal.application.draft_created`;
  - portal application draft update: `portal.application.saved`;
  - portal application submit: `portal.application.submitted`.
- Preserve existing internal staff audit action names for staff routes. Portal-specific action names
  should apply only when the portal route invokes the shared application service.
- Keep all audit payloads metadata-only: no PAN, Aadhaar, full bank account values, encrypted
  values, token hashes, raw document contents, or OTP values.

## Database/Model Impact
No migration expected.

## API Contracts
Update `docs/working/API_CONTRACTS.md` with:
- portal account status/session invalidation behavior;
- canonical portal audit action names;
- explicit note that staff application routes keep internal `applications.*` audit action names.

## Permissions
- Portal account status is part of portal authority, not an optional display fact.
- Staff tokens remain denied on portal routes.
- Portal tokens remain denied on staff completeness, reference-generation, rejection-note,
  return-with-deficiencies, and deficiency-resolution routes.

## Audit Requirements
- Add failing-first tests that currently see the wrong action names, then update implementation.
- Successful portal actions should produce the source-backed portal audit action.
- Failed portal login should audit `portal.login.failed` without revealing whether the account
  exists.
- Suspended-account session rejection should not create success audit rows or portal application
  side effects.

## Validation Rules
- An active portal account can still activate/login/change password/use own-data APIs as before.
- A suspended portal account cannot log in and cannot keep using already-issued sessions for
  `/auth/me`, password change, portal dashboard/profile/supply, or portal application endpoints.
- Cross-member portal application attempts continue to return `403 OBJECT_ACCESS_DENIED` with no
  application, audit, workflow, register, reference, or sequence side effects.

## Test Cases
TDD backend tests first:
- Existing portal access token returns `401 INVALID_TOKEN` or equivalent session-bound auth failure
  after its `PortalAccount.status` is changed to `suspended`, and the session is revoked.
- Suspended portal account cannot call password-change or own-data portal APIs with an old token.
- Portal login failed/success and activation/password-change audit rows use the source event names.
- Portal application create/update/submit via `/api/v1/portal/applications/` write
  `portal.application.draft_created`, `portal.application.saved`, and
  `portal.application.submitted`, while staff create/update/submit tests still assert
  `applications.loan_application.*`.
- No portal audit payload includes sensitive values, OTPs, token hashes, or raw document data.

## Visual Acceptance Criteria
None.

## Evidence Required
Backend red/green logs, focused portal auth/application tests, and standard quality-gate logs.

## Risk Level
High

## Acceptance Criteria
- Portal account suspension blocks already-issued portal sessions and current-user portal claims.
- Portal audit action names match the source portal audit table without breaking staff audit
  actions.
- Tests cover the status/session boundary, source audit names, sensitive payload exclusions, and
  no side effects on denied portal actions.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Database rules followed, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
