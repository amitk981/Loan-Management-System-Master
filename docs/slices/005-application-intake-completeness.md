# Slice 005: Loan Application Intake, Documents, Completeness, and Deficiencies

## Status
Not Started

## Goal
Implement loan application draft/update/submit, reference numbering, application documents, completeness check, deficiencies, rejection note shell, and frontend intake/detail workflows.

## User Value
Credit users and members can create complete loan applications and route incomplete applications back with traceable deficiencies.

## Depends On
- Slice 004

## Source References
- `docs/source/implementation-roadmap.md` sections 11, 20.1, 20.2, 20.3, 21.3, 22.1
- `docs/source/api-contracts.md` sections 19, 20, 21
- `docs/source/data-model.md` loan origination and application document tables
- `docs/source/screen-spec.md` application screens
- `docs/source/screen-spec-member-portal.md` application screens
- `docs/source/functional-spec.md`

## Screens Involved
- Application list
- New loan application
- Application detail
- Completeness workbench
- Document upload
- Deficiency resolution
- Rejection note builder
- Member portal application start/status

## Prototype Reference
- `ApplicationList.tsx`
- `NewApplication.tsx`
- `ApplicationDetail.tsx`
- `CompletenessWorkbench.tsx`
- `MP05_NewApplication.tsx`
- `MP09_MyApplications.tsx`
- `MP10_ApplicationStatus.tsx`

## Frontend Scope
- Wire application list/detail/new application to APIs.
- Add real draft autosave or explicit save behavior according to source docs.
- Add document upload and completeness states.
- Add deficiency creation/resolution and rejection note shell.
- Cover member portal application status and deficiency response gaps.

## Backend/API Scope
- Loan application draft/create/update/submit/list/detail APIs.
- Reference number generation.
- Application document list/upload/verify APIs.
- Completeness check, return with deficiencies, resolve deficiencies.
- Rejection note create/send shell with audit events.

## Database/Model Impact
- Loan applications, loan request register entries, application documents, deficiencies, rejection notes, sequence/config references.

## API Contracts
- Loan Application APIs
- Application Document APIs
- Deficiency and Rejection APIs

## Permissions
- Field Officer/Credit/Finance/member portal permissions per source docs.
- Members only access their own portal applications.

## Validation Rules
- Application requires member.
- Purpose category must be valid.
- Required application and KYC document placeholders exist before submit.
- Appraisal cannot begin until completeness passes.
- Deficiency resolution must retain audit history.

## Test Cases
- Draft/create/update/submit.
- Reference uniqueness.
- Completeness pass/fail and deficiency creation.
- Member portal deficiency response.
- Rejection note reason required.
- Unauthorized access blocked.

## Visual Acceptance Criteria
- Multi-step form remains usable and does not lose prototype structure.
- Deficiency and document states are obvious to staff and members.

## Evidence Required
- API tests.
- Screenshots of new application, completeness failure, deficiency resolution, and application detail.

## Risk Level
Medium

## Acceptance Criteria
- Applications persist through backend APIs.
- Completeness gates block downstream appraisal.
- Staff and member frontend flows reflect backend status.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
