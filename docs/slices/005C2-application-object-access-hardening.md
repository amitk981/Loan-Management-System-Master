# Slice 005C2: Application Object Access Hardening

## Status
Not Started

## Parent Epic
Epic 005: Loan Application Intake, Documents, Completeness, and Deficiencies
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal
Close the architecture-review finding from `2026-07-09_190655_architecture_review` before adding
application documents and completeness work.

## User Value
Field staff and credit users can act only on loan applications inside their permitted assignment or
role scope, preventing same-permission users from reading or moving unrelated applications.

## Depends On
- 005C

## Prior Slice Facts
- 005A added draft loan-application create/read/update with global permission checks only.
- 005B added `draft -> submitted` submit with global `applications.loan_application.submit`.
- 005C added successful completeness-pass reference generation and the loan request register with
  global `applications.loan_application.complete_check`.
- 002I already provides the domain-neutral object-access helper
  `sfpcl_credit.identity.modules.object_permissions.evaluate_object_access(...)`.
- Architecture review `2026-07-09_190655_architecture_review` found that application detail,
  update, submit, and reference-generation actions currently do not use object-level scope.

## Source References
- `docs/source/auth-permissions.md` §19.2 application object access:
  - Field Officer: created/assigned applications.
  - Deputy Manager Finance: credit assessment queue/assigned applications.
  - Credit Manager: all applications in Credit Assessment domain.
- `docs/source/auth-permissions.md` endpoint map: `GET /loan-applications/{id}/` requires
  `applications.loan_application.read` plus object access; `PATCH` also requires workflow state.
- `docs/source/auth-permissions.md` §37.3: Field Officer viewing an unrelated application is denied.
- `docs/working/digests/epic-005-application-intake.md` object-access extract from this review.

## Prototype Reference
None.

## Screens Involved
None.

## Frontend Scope
None.

## Backend/API Scope
Integrate application object-access enforcement for the application APIs implemented so far:
- `GET /api/v1/loan-applications/{loan_application_id}/`
- `PATCH /api/v1/loan-applications/{loan_application_id}/`
- `POST /api/v1/loan-applications/{loan_application_id}/submit/`
- `POST /api/v1/loan-applications/{loan_application_id}/generate-reference/`

Use the existing 002I helper rather than inventing a second object-access mechanism. For the
current schema, treat `LoanApplication.created_by_user` / `received_by_user` as the source-backed
"created application" owner fact for Field Officer-style access. If Credit Manager global
credit-assessment scope cannot be represented with existing role/team facts yet, record a narrow
assumption and make that override explicit in code and tests.

Do not implement application list filtering, assigned-user queues, team assignment tables, member
portal borrower-self access, application documents, completeness decisions, deficiencies,
eligibility, appraisal, sanction, or frontend wiring in this slice.

## Database/Model Impact
None expected. Add schema only if the source-backed scope cannot be represented from existing
application actor fields and current user/team facts; keep any such change to one migration.

## API Contracts
Update `docs/working/API_CONTRACTS.md` to state that object-scoped detail/action endpoints may
return `403 OBJECT_ACCESS_DENIED` when the actor has the permission code but is outside the
application scope.

## Permissions
Preserve existing source permission codes:
- Read: `applications.loan_application.read`
- Update draft: `applications.loan_application.update`
- Submit: `applications.loan_application.submit`
- Reference generation/completeness pass: `applications.loan_application.complete_check`

Add object-access checks after authentication and global permission checks, before serialization or
mutation. Missing global permission should remain `403 PERMISSION_DENIED`; scope mismatch should be
`403 OBJECT_ACCESS_DENIED`.

## Audit Requirements
No new success audit action is required. Failed object-access denials should not mutate application,
workflow, sequence, register, or existing success-audit rows. Add denial audit only if there is an
existing project convention for authorization denials; otherwise record the no-denial-audit
assumption.

## Validation Rules
- Unknown applications still return `404 NOT_FOUND`.
- A same-permission user who did not create/receive the application and does not have an explicit
  source-backed global/credit-domain override receives `403 OBJECT_ACCESS_DENIED`.
- The creator/receiver with the required permission can still read, patch drafts, submit drafts, and
  generate references when state rules pass.
- State errors remain `409 INVALID_STATE_TRANSITION` only after object access is allowed.
- Denied object access must not create audit/workflow/register rows or advance the sequence.

## Test Cases
TDD backend tests first:
- A second user with `applications.loan_application.read` cannot read an application created by the
  first user; expect `403 OBJECT_ACCESS_DENIED`.
- A second user with update/submit/complete-check permissions cannot patch, submit, or generate a
  reference for the first user's application.
- The creating/receiving user with the same permission set can still read, update a draft, submit,
  and generate the `LO...` reference through the existing happy path.
- Object-access denial creates no update audit, submit audit, reference audit, workflow event,
  register row, or visible sequence advancement.
- Existing missing-permission tests still return `403 PERMISSION_DENIED`.

## Visual Acceptance Criteria
None.

## Evidence Required
Backend red/green logs and standard quality-gate logs.

## Risk Level
Medium

## Acceptance Criteria
- Application detail and mutating actions enforce object access in addition to global permissions.
- Tests prove unrelated same-permission users are denied without side effects.
- The implementation reuses the existing object-access helper and records any remaining schema/scope
  assumption.
- No production scope beyond application access hardening is introduced.

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
