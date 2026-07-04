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

Current schema check: the tracer model fields are `workflow_event_id`, `workflow_name`,
`entity_type`, `entity_id`, `from_state`, `to_state`, `triggered_by_user`,
`trigger_reason`, and `created_at`; `tracer.services.action_payload()` exposes
`workflow_event_id` to API callers. Preserve that response field while moving event
recording behind the canonical service.

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
1. Introduce the canonical workflow-event model/service boundary without colliding with
   the existing tracer migration that already owns database table `workflow_events`.
2. Prefer relocating ownership of the existing `workflow_events` table to the canonical
   foundation app/model and repointing `sfpcl_credit/tracer/services.py::_record_event`
   to that interface. If relocation is not migration-safe, rename the tracer copy to
   `tracer_workflow_events` and create the canonical table fresh in the same slice.
3. Add a small write interface such as `record_workflow_event(...)` that accepts explicit
   actor, workflow, entity, from-state, to-state, action, and metadata facts. Do not embed
   loan eligibility, sanction authority, document-completeness, or money rules here.
4. If a read endpoint is included, keep it to `GET /api/v1/workflow-events/` with the
   §42.2 filters `entity_type` and `entity_id`, top-level pagination, and standard
   002J success/error contract helpers. Do not build dashboard/task UI in this slice.

## Database/Model Impact
Exactly one non-destructive migration is expected. It must handle the tracer drift
explicitly so `migrate` succeeds on a clean database and on an existing database that has
the 002EX tracer migration. Do not create a second `workflow_events` table with the same
name.

## API Contracts
Update `docs/working/API_CONTRACTS.md` with the canonical workflow-event write/read
contract chosen in this slice, including how the tracer proof now records events.

## Permissions
For any read endpoint, require session-bound bearer auth plus existing
`audit.workflow_event.read`. Do not invent a new workflow-event permission code. The
write interface is internal service code called by guarded workflows; it should receive
an already-authenticated actor from the caller.

## Audit Requirements
This slice owns workflow-event persistence, not audit-log writes. Preserve existing tracer
`AuditLog` behavior exactly while migrating/repointing tracer workflow-event recording.

## Validation Rules
- `makemigrations --check`, `migrate`, and all tracer lifecycle tests must remain green.
- Existing tracer transitions still produce one workflow event per successful transition.
- No duplicate table-name collision with `workflow_events`.
- Missing/invalid auth and missing read permission, if a read endpoint is added, return
  002J-validated `401`/`403` envelopes.
- Invalid UUID filters, if a read endpoint is added, return `400 VALIDATION_ERROR`.

## Test Cases
- Backend TDD: migration/model ownership test or service test fails first against the
  current tracer-owned shape, then passes after canonical ownership is established.
- Backend service: `record_workflow_event(...)` persists the expected workflow/entity
  facts and metadata without importing tracer domain models.
- Backend regression: tracer action responses still include `workflow_event_id` after the
  ownership reconciliation.
- Backend regression: the existing tracer lifecycle still writes seven workflow events
  and seven tracer audit rows.
- Backend migration regression: clean `migrate` and `makemigrations --check --dry-run`
  pass without attempting duplicate `workflow_events` creation.
- Backend API, if read endpoint is included: authorized `audit.workflow_event.read` user
  can list/filter events with top-level pagination; no-permission user receives
  `403 PERMISSION_DENIED`.

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
