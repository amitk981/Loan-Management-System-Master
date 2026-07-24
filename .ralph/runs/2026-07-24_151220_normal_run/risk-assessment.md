# Risk Assessment

Risk level: Medium

- Selected slice: 012EA-workflow-task-engine-and-task-inbox-apis
- Mode: normal_run
- Manual review required: independent Ralph validation, including the schema/routing-selected
  authoritative backend lane.

## Integrity and permission controls

- `WorkflowTask` has bounded task/priority/status vocabularies, coherent open/closed timestamps,
  operational owner/due indexes, and a database partial unique constraint preventing two open
  tasks for the same linked entity and task type.
- Canonical workflow-event processing and the scheduled reconciliation job use the same projector.
  Replay refreshes one open row; leaving an actionable state system-closes it. No HTTP close or
  complete route exists.
- The M04 appraisal task uses the retained source TAT anchor, closes on review submission, reopens
  as a new task on a return to draft, and cannot remain open on reviewed/rejected/sanction paths.
- Task reads intersect direct assignment, effective role, and active team scope before applying
  caller filters. Reassignment additionally requires `users.team.manage` and a target in the
  retained role/team. Comment/block/unblock recheck open-task object scope.
- Reassign/comment/block/unblock emit central audit rows. Comment and block text are bounded and
  excluded from audit payloads; the task/comment resource retains the user-authored text.
- Dashboard task projection is one bounded query in addition to the established card selectors.
  Existing fixed query budgets increased by exactly one (credit maximum 11; cross-role maximum
  25) and pass.

## Residual risks and decisions

- The source does not supply a universal SLA/priority matrix or a Sanction Committee role code.
  A-174 records the fail-honest behavior: source-owned dates are used where they exist, otherwise
  due date is null and priority remains Normal; sanction uses the existing team with CFO as its
  role anchor. Governance should version these mappings prospectively.
- Reconciliation is memory-bounded with 200-row iterators and reuses database uniqueness, but its
  deployment backfill performs owner resolution per entity. Operations should schedule it off the
  request path and observe its first-run duration on production-scale in-flight data.
- Task rows intentionally denormalize safe S03 display facts. Reconciliation refreshes mutable
  operational display facts while immutable workflow/audit rows retain the authoritative
  transition history. Linked-resource permissions are rechecked when the user opens the resource.
- The migration, routing, scheduler, dashboard, and three workflow-owner integrations make the
  candidate broader than a localized module-only change. The implementation agent ran focused
  regressions only; Ralph independent validation owns the authoritative impacted/full lane and
  coverage decision.

## Evidence

- RED/GREEN logs:
  `evidence/terminal-logs/workflow-task-appraisal-red.log`,
  `evidence/terminal-logs/workflow-task-appraisal-green.log`,
  `evidence/terminal-logs/workflow-task-eight-types-red.log`,
  `evidence/terminal-logs/workflow-task-reconciliation-red.log`,
  `evidence/terminal-logs/workflow-task-list-red.log`,
  `evidence/terminal-logs/workflow-task-actions-red.log`,
  `evidence/terminal-logs/workflow-task-dashboard-red.log`, and
  `evidence/terminal-logs/workflow-task-scheduler-red.log`.
- Final focused regression output:
  `evidence/terminal-logs/workflow-task-focused-green.log`.
- Schema/check/migration output:
  `evidence/terminal-logs/workflow-task-schema-green.log`.
- Human-readable eight-type mapping:
  `evidence/task-state-role-mapping.md`.
