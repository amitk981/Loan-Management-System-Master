# Slice 003G: Dashboard Task Summary API

## Status
Not Started

## Parent Epic
Epic 003: Audit, Documents, Config, and Dashboard Foundation
Epic file: `docs/epics/003-audit-documents-config-foundation.md`

## Goal
Deliver the backend `GET /api/v1/dashboard/` role-based dashboard summary shell with standard
cards and task metadata, without implementing downstream loan/compliance calculations that do not
exist yet.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 003F

## Source References
- docs/source/implementation-roadmap.md sections 10, 20-22
- docs/source/api-contracts.md sections 26, 39, 41, 42-43
- docs/source/data-model.md document/config/audit tables
- docs/source/component-spec.md
- docs/source/design-system.md

## Prototype Reference
- sfpcl-lms/src/pages/Dashboard.tsx
- sfpcl-lms/src/pages/tasks/TaskInbox.tsx
- sfpcl-lms/src/components/loan/AuditTimeline.tsx
- sfpcl-lms/src/components/loan/DocumentPackModal.tsx

## Screens Involved
None directly; 003H wires the existing frontend dashboard to this API.

## Frontend Scope
None for this slice.

## Backend/API Scope
1. Implement `GET /api/v1/dashboard/` matching `docs/source/api-contracts.md` §43.1:
   response `data.role_context`, `data.cards[]`, and `data.tasks[]`.
2. Return standard envelope data:
   - cards: `code`, `label`, `count`, `link`
   - tasks: `task_type`, `entity_id`, `title`, `due_at`
3. Build the shell from role context and existing data only. Because the real application,
   appraisal, loan, DPD, reminder, default, compliance, treasury, sanction, and management tables
   are not implemented yet, return source-named zero-count cards and an empty `tasks` list rather
   than inventing business calculations.
4. Include at least the Credit Manager cards from §43.1:
   `applications_pending_completeness`, `appraisals_due_today`,
   `loans_outstanding_beyond_one_year`.
5. Include source-backed placeholder card sets for these role contexts using the widget lists in
   `functional-spec.md` §12.2-§12.6:
   `credit_manager`, `sanction_committee`, `compliance`, `treasury`, and `management`.
6. Do not implement specialist endpoints `/dashboard/sanction-committee/`, `/dashboard/compliance/`,
   or `/dashboard/treasury/` in this slice unless required only as redirects/aliases to the same
   service; prefer the single §43.1 endpoint.
7. Do not create task persistence tables in this slice unless the source table already exists.

## Database/Model Impact
None expected. If a model is proposed, stop and justify why zero-count/read-only shell data cannot
be produced from existing state.

## API Contracts
Update `docs/working/API_CONTRACTS.md` with the dashboard response shape, role contexts, permission
assumption, zero-count shell behavior, and explicit deferral of specialist calculations.

## Permissions
Require session-bound bearer auth. Choose the narrowest source-backed dashboard read permission
handling and record it in `ASSUMPTIONS.md` because the seeded catalogue has report/compliance
read permissions but no exact `dashboard.read` code. Test:
- missing/revoked bearer token returns `401`;
- authenticated actor without the chosen permission/scope returns `403`;
- authorized actors receive only the role-context shell appropriate to their role/permission.

## Audit Requirements
Read-only dashboard summary access does not create audit rows in this shell unless source docs
explicitly require it; if no audit is written, assert that in tests.

## Validation Rules
No query parameters are supported in 003G. Unknown query parameters return standard
`400 VALIDATION_ERROR`.

## Test Cases
- TDD red/green: dashboard API test fails before endpoint/service exists.
- API: authorized Credit Manager receives standard success envelope with `role_context:
  "credit_manager"`, §43.1 card fields, zero counts, links, and empty tasks.
- API: sanction/compliance/treasury/management contexts return source-named card shells from
  `functional-spec.md` §12.3-§12.6 without calculations.
- Permissions: unauthenticated/revoked requests return `401`; no-permission actor returns `403`.
- Contract: unknown query parameter returns `400 VALIDATION_ERROR`.
- Audit: dashboard reads do not write `AuditLog` rows unless a source-backed audit rule is added.
- Security: no borrower/member/loan-specific sensitive values are returned in this shell.

## Visual Acceptance Criteria
Match the existing prototype patterns and include loading, empty, error, unauthorized, validation, and success states where relevant.

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
