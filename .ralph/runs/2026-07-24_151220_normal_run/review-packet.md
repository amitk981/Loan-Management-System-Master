# Review Packet: 2026-07-24_151220_normal_run

## Result
Ready for independent validation

## Slice
012EA-workflow-task-engine-and-task-inbox-apis

## What changed

- Added persisted workflow tasks/comments with eight S03 task types, source owner facts, SLA/block
  state, operational indexes, and database-enforced open-task idempotency.
- Added one task projector behind the canonical workflow-event seam plus a 003J scheduled
  reconciliation lifecycle that backfills every current actionable owner and recomputes overdue
  standing.
- Integrated application/appraisal, disbursement, direct/subsidiary repayment, sanction,
  documentation, SAP, and default states without duplicating compliance tasks.
- Added role/team/user-scoped `GET /api/v1/tasks/` and audited reassign, comment, block, and
  unblock actions. Manual task completion is deliberately unavailable.
- Replaced dashboard's empty `tasks[]` with the same scoped task engine through one bounded query.
- Documented routes, filters, actions, mapping, scheduler behavior, nullable unsourced SLA policy,
  and assumption A-174.

## Source-to-code traceability

| Source requirement | Implementation | Verification |
|---|---|---|
| `screen-spec.md` S03 requires eight task types, its columns, filters, and open/reassign/comment/block actions. | `WorkflowTask`, `WorkflowTaskComment`, `tasks.task_inbox`, and `task_views` persist and expose those task facts/actions. | `WorkflowTaskProjectionTests.test_all_eight_task_types_open_once_for_owner_role_and_close_on_exit`; `WorkflowTaskApiTests` list/action tests |
| `functional-spec.md` M04-FR-001-003 requires one post-reference appraisal task, Deputy Manager Finance assignment, and two-day TAT. | Canonical `reference_generated` events project one `appraisal` task assigned to `deputy_manager_finance`; due time uses the retained A-054 receipt proxy plus two days. Review closes it and return-to-draft reopens it. | appraisal replay and review/return/terminal tests; application-reference and appraisal reverse-consumer regressions |
| `data-model.md` §§26, 30, and 34 require canonical workflow events, operational indexing, and atomic integrity. | Event recording calls the projector in the owner transaction; migration 0002 adds role/user/due and entity indexes, bounded checks, and `uniq_open_workflow_task`. | migration SQL, migration-sync check, replay/reconciliation tests |
| `user-flows.md` stage actors require role-owned work across origination, appraisal, sanction, documentation, SAP, disbursement, repayment, and default. | `task_state_mapping()` records the exact eight mappings; owner transitions project/close them and reconciliation backfills pre-existing rows. | `task-state-role-mapping.md`; eight-type executable mapping/closure tests |
| `api-contracts.md` §8 requires pagination/filtering and reserves `assigned_to_user_id`; §43.1 defines dashboard task shape. | `/api/v1/tasks/` uses strict filters and standard pagination after role/team/user scoping; dashboard emits `task_type`, `entity_id`, `title`, `due_at`. | task list test; dashboard section-43 test; all dashboard query-budget tests |
| Slice requirement 5 requires object permissions and 003A audit for mutable actions, while close is system-only. | Reassign requires object scope plus `users.team.manage`; all actions audit; no close route exists. | forbidden/permitted reassignment and four-action audit assertion |

## Focused validation

- 54 workflow-task, workflow-event, scheduler, dashboard, repayment, subsidiary reconciliation,
  disbursement, appraisal, and reference-generation tests passed.
- Final task/dashboard post-refactor rerun: 26 tests passed.
- `manage.py check`, `makemigrations --check --dry-run`, migration SQL rendering, impacted Python
  compilation, and `git diff --check` passed.
- Query budgets pass with exactly one bounded dashboard task query; inbox pagination uses a fixed
  scope query, count query, and bounded page query rather than one query per row.
- No frontend files changed; S03 frontend wiring and browser evidence belong to 012EB. Runtime
  capability is `none`.
- The complete backend suite/coverage was not run by the implementation agent; independent Ralph
  validation owns the authoritative lane selected for this schema/routing/multi-module candidate.

## Review focus

- Confirm the independent backend lane covers the new migration/routing and all reverse consumers.
- Confirm A-174's fail-honest null SLA/Normal priority and CFO + Sanction Committee team mapping
  remain preferable to inventing a universal task policy.
- Inspect the first production reconciliation duration and ensure the scheduled runner invokes it
  off the request path.
- Verify no task read/action can substitute for the linked application's or loan account's own
  permission checks.

## Recommended Next Action
Run Ralph independent validation; if green, commit and merge through the orchestrator.
