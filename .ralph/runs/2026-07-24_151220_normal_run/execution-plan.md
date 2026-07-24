# Execution Plan

Selected slice: `012EA-workflow-task-engine-and-task-inbox-apis`

## Scope and interface

- Add the persisted workflow-task resource to the existing `workflows` owner, including the
  migration, eight source-defined task types, role/team assignment facts, SLA state, comments,
  blocking state, and system-only closure.
- Keep one deep module interface for task projection and reconciliation. Existing workflow owners
  continue to own entity states; the task module consumes their public persisted state/event facts
  and owns idempotent open/close behavior.
- Expose the scoped paginated task inbox and reassign/comment/block/unblock actions under
  `/api/v1/tasks/`, then use the same scoped selector for dashboard `tasks[]`.
- Register the reconciliation job on the existing scheduler foundation and document the routes,
  filters, actions, mappings, and dashboard projection in `docs/working/API_CONTRACTS.md`.

## TDD tracer bullets

1. RED/GREEN: application-reference generation creates one Deputy Manager Finance appraisal task,
   replay is idempotent, review closes it, and return-to-draft reopens it.
2. RED/GREEN: each remaining source task type projects once for its actionable state and closes
   when its owning entity leaves that state.
3. RED/GREEN: reconciliation backfills in-flight entities and recomputes due-today/overdue facts
   without duplicates.
4. RED/GREEN: task list pagination, S03 filters, role/team scope, and dashboard reverse consumer.
5. RED/GREEN: permitted reassign/comment/block/unblock actions mutate only allowed fields and emit
   003A audit rows; forbidden actors receive 403; manual close is absent.

Each cycle uses the public task module or HTTP interface and saves focused RED/GREEN output in
`evidence/terminal-logs/`.

## Verification

- Focused workflow-task, dashboard, application/appraisal integration, scheduler, permission, and
  audit tests using `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Django `check` and `makemigrations --check`; targeted query-count assertion for the inbox and
  dashboard projection.
- No frontend edit is in scope for `012EA`; frontend gates are left to independent validation.
- Inspect diff stats and targeted hunks, then write `risk-assessment.md`, `review-packet.md`, and
  final evidence with the exact ready result.

## Permission check

Planned product paths are under `sfpcl_credit/**`; contract/evidence paths are under
`docs/working/**` and `.ralph/runs/2026-07-24_151220_normal_run/**`. These are allowed by
`.ralph/permissions.json`. Protected configuration, scripts, source documents, orchestrator-owned
state/progress/status files, and Git metadata will not be edited.
