# Slice 012EA: Workflow Task Engine and Task Inbox APIs

## Status
Not Started

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

Screen S03 (Task Inbox) is listed under Epic 003, but its implementation was deliberately
deferred here (owner decision 2026-07-07) because task generation needs workflow states from
Epics 005-011 to exist first. This slice closes that gap as a UAT-critical item per this
epic's scope ("Any UAT-critical frontend gaps discovered in earlier slices").

## Goal
Build the source-backed task engine the Task Inbox (S03) and the dashboard `tasks[]` list have
been waiting for: a persisted task table, generation/closure rules driven by workflow events,
and task APIs matching the S03 screen spec — so staff work queues stop being mock shells.

## User Value
Every internal user gets a real "what needs my attention" queue: completeness checks, appraisals,
sanctions, document verification, SAP setup, disbursement, repayment posting, and default reviews
appear as actionable tasks with priority and SLA instead of hardcoded prototype rows.

## Depends On
- 012E

## Source References
- docs/source/screen-spec.md S03 (Task Inbox: columns, filters, actions)
- docs/source/api-contracts.md section 43.1 (dashboard `tasks[]` shape: `task_type`, `entity_id`, `title`, `due_at`), section 8 (pagination/filtering; §8.3 reserves `assigned_to_user_id` for task/workflow resources)
- docs/source/data-model.md (workflow event tables from 003B; entity states per module)
- docs/source/user-flows.md (which role acts at each workflow stage — the generation rules)
- docs/source/functional-spec.md M04-FR-001 and M04-FR-002 (create the appraisal task after
  application-number generation and assign appraisal preparation to Deputy Manager – Finance)
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-10_173305_architecture_review`

## Prototype Reference
- sfpcl-lms/src/pages/tasks/TaskInbox.tsx (columns and layout to serve)
- sfpcl-lms/src/pages/Dashboard.tsx (tasks list consumer, wired in 003H)

## Concrete Requirements
1. Persisted `tasks` table: task reference, task type (the eight S03 types), linked entity
   (application/loan account), assigned role and optional assigned user, priority
   (Normal/High/Critical), status, due date, blocked flag, created/closed timestamps. Reuse
   existing model conventions; migrations required.
2. Generation and closure rules: when a workflow event (003B) or state transition puts an entity
   into a state that requires role action, an open task is created for that role; when the entity
   leaves that state, the task closes automatically. Rules must be idempotent — re-processing an
   event or re-running a scan never duplicates an open task for the same entity + task type.
   The appraisal rule is explicit: successful application-number generation creates one open
   appraisal-preparation task assigned to role `deputy_manager_finance`; it closes when the
   appraisal is submitted for Credit Manager review and reopens on a 006F return to draft.
3. A scheduled reconciliation job on the 003J foundation: recomputes SLA/overdue standing
   (due date, overdue days) and backfills tasks for entities already in actionable states when
   this slice first deploys (so pre-existing in-flight records get tasks).
4. `GET /api/v1/tasks/` per api-contracts §8: pagination, and filters covering the S03 filter
   list (task type, due today, overdue, borrower type, amount threshold, special case, exception
   required, `assigned_to_user_id`, assigned-to-my-team). Response rows carry the S03 columns.
5. Task actions with object-level permission checks and 003A audit events: reassign (where
   permitted), add comment, mark blocked / unblock. Task close is system-driven only — no manual
   "complete" that bypasses the underlying workflow.
6. `GET /api/v1/dashboard/` `tasks[]` (003G shell) now returns the caller's open tasks in the
   §43.1 shape instead of an empty list.
7. Document the new endpoints and generation rules in `docs/working/API_CONTRACTS.md` (source
   contracts define no dedicated task-inbox API; §43.1 and §8 conventions are the baseline).

## Test Cases
- For each of the eight task types: seeding an entity into the actionable state creates exactly
  one open task for the correct role; advancing the entity's state closes it.
- M04 regression: application-number generation creates exactly one Deputy Manager – Finance
  appraisal task with the source TAT due date; event replay does not duplicate it, review return
  reopens it, and review/rejection/sanction paths cannot leave a stale preparation task open.
- Re-running generation (event replay or reconciliation scan) creates no duplicate open tasks.
- Overdue computation: a task past its due date reports overdue days; "due today" filter matches.
- Permission checks: a user sees only tasks for their role/team; reassign by a non-permitted role
  returns 403; reassign/block/comment emit audit events.
- `GET /api/v1/dashboard/` returns the caller's open tasks in the §43.1 shape.

## Out of Scope
Task Inbox frontend wiring (012EB). Compliance tasks — they remain a separate resource per
api-contracts §37.2 and are not duplicated into this engine. Notification fan-out for tasks
(003I adapter policies unchanged). Export of task lists (012EB decides whether to reuse 012B
export jobs). Scheduler UI.

## Risk Level
Medium

## Acceptance Criteria
- Task generation, closure, SLA recomputation, and task APIs run on real workflow data for all
  eight S03 task types, with permissions and audit enforced.
- Dashboard `tasks[]` is populated from the same engine; `docs/working/API_CONTRACTS.md` updated.
- All gates pass.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Substantive unresolved risk or decision recorded only if needed
- [ ] Commit created only after passing gates
