# Slice 003B: Workflow Event Foundation

## Status
Not Started

## Parent Epic
Epic 003: Audit, Documents, Config, and Dashboard Foundation
Epic file: `docs/epics/003-audit-documents-config-foundation.md`

## Goal
Deliver the canonical workflow-event foundation (the `workflow_events` table and its write interface) as a small, testable Ralph implementation slice — AND reconcile the pre-existing tracer drift that already created a `workflow_events` table so there is no table-name collision.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 003A

## Source References
- docs/source/implementation-roadmap.md sections 10, 20-22
- docs/source/api-contracts.md sections 26, 39, 41, 42-43
- docs/source/data-model.md §26 workflow_events schema (authoritative for this slice), plus document/config/audit tables
- docs/source/component-spec.md
- docs/source/design-system.md
- Architecture review finding: `2026-07-04_071340_architecture_review` Finding 1 (tracer squats on `workflow_events`)

## Drift to reconcile (MANDATORY — from architecture review 2026-07-04)
Slice `002EX` already created a `WorkflowEvent` model whose `db_table = "workflow_events"` lives in the throwaway `sfpcl_credit/tracer/` app (`sfpcl_credit/tracer/models.py`, migration `0001_initial`). That is the canonical table this slice owns. This slice MUST NOT run `CreateModel("workflow_events")` on top of it (migrate would fail with "table already exists"). Do exactly one of:
1. Relocate the canonical `WorkflowEvent` model into this slice's owning app, base its schema on `data-model.md §26` (not the tracer's minimal fields), migrate the existing `workflow_events` table into the new owner without data loss, and repoint `sfpcl_credit/tracer/services.py::_record_event` at the canonical model; OR
2. Rename the tracer copy's table to `tracer_workflow_events` in the same slice (so the tracer stays self-contained and disposable per A-011) and create the canonical `workflow_events` table fresh from `data-model.md §26`.
Prefer option 1 unless the tracer is scheduled for removal first. Either way: `makemigrations --check` and `migrate` must both pass on a clean database, and the tracer lifecycle test must still be green afterward.

## Prototype Reference
- sfpcl-lms/src/pages/Dashboard.tsx
- sfpcl-lms/src/pages/tasks/TaskInbox.tsx
- sfpcl-lms/src/components/loan/AuditTimeline.tsx
- sfpcl-lms/src/components/loan/DocumentPackModal.tsx

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
Implement the named backend/API capability only.

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

## Test Cases
Unit/service/API/permission tests plus frontend tests where UI is touched.

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
