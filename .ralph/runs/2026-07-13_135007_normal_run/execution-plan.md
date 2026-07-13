# Execution Plan

Selected slice: `007C3-approval-case-source-read-scope-closure`

## Scope and seams

- Keep the public HTTP list/detail/action endpoints unchanged.
- Add one approval-owned persisted read-scope grant with an active role, one bounded scope type,
  active/inactive status, and a role/scope uniqueness constraint. Seed only Company Secretary
  (`legal_readonly`) and Internal Auditor (`audit_readonly`).
- Deepen the existing approval-case engine interface so its attributable read decision and selector
  own assignment, Credit Manager credit-domain ownership, and persisted read-only grants. Do not
  infer case scope from permission codes or query flags.
- Database-narrow the collection to the actor's candidate rows before routability checks,
  pagination, counts, and serialization. Preserve immutable acted-history access and all 007C2
  snapshot-coherence rules.

## TDD sequence

1. RED/GREEN: public list/detail proves a Credit Manager can read their submitted sanction package
   but not an unrelated case.
2. RED/GREEN: public list/detail proves active Company Secretary and Internal Auditor grants allow
   read-only access; inactive/deleted grants revoke access immediately.
3. RED/GREEN: assigned queues, available actions, action endpoints, and complete write ledgers stay
   unchanged for read-only actors; arbitrary readers and unassigned Directors remain denied.
4. RED/GREEN: scoped pagination/counts and query-count work remain bounded when unrelated cases are
   added.
5. Add catalogue/migration tests for exact permission seeding, grant scope/status constraints, and
   idempotent seed behavior.

Each backend cycle uses `/Users/amitkallapa/LMS/.ralph/venv/bin/python`; RED and GREEN output is
retained under `evidence/terminal-logs/`.

## Verification and closeout

- Run focused approval/catalogue tests regularly, then Django check, migration sync, full backend
  coverage, and all configured frontend build/typecheck/lint/test gates.
- Run the implementation review workflow against this slice as the specification and resolve any
  in-scope findings.
- Save changed-files, risk assessment, review packet, final summary, and self-contained evidence.
- Update the slice status, Ralph state/progress/handoff, epic digest/API contract if applicable,
  and sharpen the next one or two Not Started slices using only already-opened Epic 007 material.
- Do not add/commit/push; the Ralph orchestrator owns validation and integration.
