# Risk Assessment

Risk level: Medium

- Selected slice: 012EB-task-inbox-frontend-wiring
- Mode: normal_run

## Implemented risk controls

- Task collection reads use the shared authenticated strict-pagination transport; malformed
  pagination or task rows fail visibly instead of becoming an empty list.
- Every source-listed S03 filter is sent to the backend. No task list is filtered from a local
  business array.
- Comment, block, and reassign use the 012EA endpoints. Backend denial is preserved; reassign is
  additionally hidden without `users.team.manage`, and future row `available_actions` narrows the
  visible controls.
- Open routes use the server-linked application/loan identity and re-enter the existing resource
  route guard. No Task Inbox authority is treated as linked-record authority.
- The prototype CSV control is removed because there is no governed task-export endpoint or report
  code.
- No backend/schema/dependency change, sensitive fixture, real communication, or deployment was
  introduced.

## Residual risks for independent validation

- The connected browser surface was unavailable to this AFK agent. The required
  `e2e/task-inbox.e2e.spec.ts` is discoverable and defines all four exact screenshot outputs, but
  the trusted validator must execute it twice and retain the PNGs; none were fabricated.
- The slice text says no staff screen should still import `mockData.ts`, but the current frozen
  queue still has five separately owned production imports in `ReportsMIS`, `RegistersHub`,
  `ComplianceDashboard`, `GrievancesHub`, and `AuditArchiveHub`. Evidence is saved in
  `evidence/terminal-logs/remaining-production-mock-owners.log`. Editing them here would violate
  the one-slice boundary; their prepared successors remain the remediation owners.
- The 012EA row contract returns `due_at` and server-calculated `overdue_days`, but no
  server-calculated remaining-duration value. The UI truthfully renders the due date or overdue
  days and does not derive new TAT state from the browser clock. A future backend contract must own
  any exact remaining-hours/days projection.
- The production build retains the repository's existing bundle-size advisory. It is non-failing
  and this slice adds no dependency.
