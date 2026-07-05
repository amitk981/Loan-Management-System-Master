# Slice 003H: Dashboard Task UI Wiring

## Status
Not Started

## Parent Epic
Epic 003: Audit, Documents, Config, and Dashboard Foundation
Epic file: `docs/epics/003-audit-documents-config-foundation.md`

## Goal
Wire the existing staff dashboard UI to the 003G `GET /api/v1/dashboard/` backend summary while
preserving the approved prototype layout and component patterns.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 003G2

## Source References
- docs/source/implementation-roadmap.md sections 10, 20-22
- docs/source/api-contracts.md section 43
- docs/source/data-model.md document/config/audit tables
- docs/source/functional-spec.md sections 12.2-12.6
- docs/source/component-spec.md
- docs/source/design-system.md

## Prototype Reference
- sfpcl-lms/src/pages/Dashboard.tsx
- sfpcl-lms/src/pages/tasks/TaskInbox.tsx
- sfpcl-lms/src/components/loan/AuditTimeline.tsx
- sfpcl-lms/src/components/loan/DocumentPackModal.tsx

## Screens Involved
- Dashboard
- Task inbox only if it already consumes dashboard/task summary data through existing patterns

## Frontend Scope
1. Replace the Dashboard mock summary/task data path with the 003G `/api/v1/dashboard/` API.
2. Reuse existing dashboard layout, metric/card/list patterns, spacing, colours, typography, badges,
   shell, and auth session helpers. Do not introduce new styling or new components.
3. Render the API card fields (`code`, `label`, `count`, `link`) through the existing prototype card
   pattern. Preserve existing route links where they already exist; if a source link points to a
   not-yet-implemented route, keep it non-destructive and visibly disabled only using existing
   patterns.
4. Render API tasks (`task_type`, `entity_id`, `title`, `due_at`) through an existing task/list
   pattern. For the 003G empty task shell, show the existing empty state pattern.
5. Implement loading, error, unauthorized/permission-denied, empty, and success states using existing
   alert/empty patterns.
6. Update `docs/working/PROTOTYPE_INVENTORY.md` and `docs/working/PROTOTYPE_GAP_REPORT.md` only if
   this wiring changes documented prototype coverage.
7. Use the exact 003G response contract from `docs/working/API_CONTRACTS.md`: `data.role_context`,
   `data.cards[]` with `code`, `label`, `count`, `link`, and `data.tasks[]` with `task_type`,
   `entity_id`, `title`, `due_at` when tasks eventually exist. The current backend returns
   `tasks: []`.
8. Cover all supported role contexts from 003G in frontend tests or fixtures:
   `credit_manager`, `sanction_committee`, `compliance`, `treasury`, and `management`.

## Backend/API Scope
No new backend behavior. 003H may only adjust frontend API client types or tests for the 003G
contract.

## Database/Model Impact
None.

## API Contracts
Do not change the 003G backend contract unless a frontend test exposes a mismatch. If changed,
update `docs/working/API_CONTRACTS.md` in the same run.

## Permissions
Frontend visibility is advisory. Use the authenticated session and API response/error status as the
source of truth; do not invent frontend-only dashboard permissions. Unauthorized and forbidden
responses must render existing auth/error patterns and must not show stale mock data.

## Audit Requirements
None in frontend. Do not add client-side audit side effects.

## Validation Rules
No new business validation in the frontend. Treat malformed/empty API data defensively without
crashing, and avoid displaying borrower/member/loan-specific sensitive data that the API does not
return.

## Test Cases
- Frontend TDD: dashboard renders loading then success cards from a mocked `/dashboard/` API response.
- Frontend: empty `tasks` array renders the existing empty state pattern.
- Frontend: `401`/`403` API responses render the existing auth/error state and do not render mock
  dashboard data.
- Frontend: network/server error renders existing error alert pattern.
- Frontend: role-specific card labels/counts/links come from the API response, not hardcoded mock
  dashboard arrays.
- Frontend: `management_readonly` may appear in `/auth/me` for dashboard-capable users, but the
  dashboard screen must still rely on the API success/error result instead of frontend-only grants.
- Frontend regression: `demo.zero@sfpcl.example` now uses role `it_head` as the neutral
  zero-permission demo account; do not assume `management_viewer` has no backend permissions after
  A-023.
- Existing backend 003G tests remain green.

## Visual Acceptance Criteria
Screenshots are required for Dashboard loading/empty-or-success/error/unauthorized states. They must
match the existing prototype patterns exactly: no colour, typography, spacing, card, table, queue,
or layout changes.

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
