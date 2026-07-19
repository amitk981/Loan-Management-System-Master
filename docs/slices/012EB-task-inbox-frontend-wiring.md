# Slice 012EB: Task Inbox Frontend Wiring

## Status
Not Started

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

Companion to 012EA (see that slice's note on why S03 lives in Epic 012). This is the last
staff screen still reading from `mockData.ts`; after this slice, no staff screen runs on
prototype mock data.

## Goal
Wire the Task Inbox screen (S03) to the 012EA task APIs — columns, filters, and actions per the
screen spec — and retire its mock-data reads.

## User Value
Staff open one screen to see and act on their real pending work across every module, with
priority and SLA visible, instead of a static prototype table.

## Depends On
- 012EA

## Runtime Capabilities

- `localhost-e2e-server`

## Trusted Browser Acceptance

- Spec: `e2e/task-inbox.e2e.spec.ts`
- Screenshot: `task-inbox-populated.png`
- Screenshot: `task-inbox-filtered.png`
- Screenshot: `task-inbox-action.png`
- Screenshot: `task-inbox-unauthorised.png`

## Source References
- docs/source/screen-spec.md S03 (Task Inbox: columns, filters, actions)
- docs/source/api-contracts.md section 8 (pagination/filtering), section 44 (available_actions convention)
- docs/working/API_CONTRACTS.md task endpoints (added by 012EA)
- docs/source/information-architecture.md (Task Inbox navigation placement)
- `docs/working/digests/epic-012-reports-exports-hardening-uat.md` §012EA / §012EB

## Prototype Reference
- sfpcl-lms/src/pages/tasks/TaskInbox.tsx
- sfpcl-lms/src/pages/Dashboard.tsx (task list pattern from 003H)

## Concrete Requirements
1. Wire `TaskInbox.tsx` to `GET /api/v1/tasks/` with real pagination per api-contracts §8 — no
   client-side-only filtering of mock arrays. Render the S03 columns (task reference, type,
   linked record, borrower, amount, priority, SLA/TAT remaining or overdue days, status,
   assigned to, created date, due date, open action).
2. S03 filters wired to API parameters: task type, due today, overdue, borrower type, amount
   threshold, special case, exception required, assigned to me, assigned to my team.
3. S03 actions using existing patterns and role gating: Open navigates to the linked
   application/loan screen; Reassign, Add comment, and Mark blocked call the 012EA action
   endpoints and appear only where permitted (available_actions per §44 where returned);
   unauthorized attempts surface the backend rejection.
4. Export action: reuse the 012B/012C export-job pattern if task export is exposed by the
   backend; otherwise hide the control and record the decision in `docs/working/API_CONTRACTS.md`.
5. Loading, empty, error, and unauthorized states throughout; compose only from existing
   components per FRONTEND_DESIGN_RULES.
6. Verify the staff dashboard task list (003H) now renders real tasks end to end, and update
   `docs/working/PROTOTYPE_GAP_REPORT.md` and `docs/working/PROTOTYPE_INVENTORY.md`: Task Inbox
   moves from prototype/mock to API-backed; no staff screen reads `mockData.ts` after this slice.

## Test Cases
- Task rows render from seeded backend tasks and match the S03 column set; pagination
  round-trips.
- "Assigned to me", "due today", and "overdue" filters return only matching seeded tasks.
- Reassign/comment/block succeed for a permitted role and are rejected and surfaced for a
  non-permitted role; Open navigates to the correct linked record.
- Dashboard task list shows the same seeded tasks (no empty-tasks regression).

## Out of Scope
Task engine changes (012EA). Compliance task screens (011K-011M surfaces). Borrower portal
task views (staff-only screen per S03 access roles). New components beyond existing patterns.

## Evidence Required
Saved RED/GREEN frontend request/filter/action/navigation output; permission denial, dashboard parity,
pagination, and final staff-mock-removal proof; all four trusted-browser screenshots from two passing
contract runs; focused task/dashboard regressions and full gates.

## Risk Level
Medium

## Acceptance Criteria
- S03 runs on backend data end to end with filters, actions, and role gating per the screen spec.
- No mock-data reads remain in the Task Inbox screen — and with it, no staff screen still reads
  `mockData.ts`.
- All gates pass; screenshots of the populated inbox, a filter result, a permitted action, and
  an unauthorized state saved.

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
