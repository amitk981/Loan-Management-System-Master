# Slice 007D: Approval Action API — Approve, Reject, Return

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Goal
Implement the individual approver actions (approve / reject / return-for-clarification) with immutable action records, joint-approval completion, and sanction-decision creation on final approval.

## User Value
CFO and Directors record real decisions with reasons; a loan is sanctioned only when every required approver has approved (M05-FR-007/008).

## Depends On
- 007C2

## Source References
- docs/source/api-contracts.md §25.5 approve (response includes `sanction_decision_created`/`sanction_decision_id`), §25.6 reject, §25.7 return-for-clarification, §25.8 sanction decision shape
- docs/source/data-model.md §15.4 `approval_actions` (immutable; unique case+approver; comments mandatory for reject/return; ip/user-agent audit columns), §15.5 `sanction_decisions` (unique per application)
- docs/source/auth-permissions.md §12.6 (`approvals.case.approve/reject/return` Critical/High, `approvals.sanction.create`)
- docs/source/functional-spec.md M05-FR-007/008/009/010
- docs/source/technical-architecture.md §13.3 (sanction approval transaction boundary)
- docs/slices/002H-state-machine-and-transition-guard-foundation.md (transition guards)

## Prototype Reference
- sfpcl-lms/src/pages/sanction/SanctionWorkbench.tsx (action consumer; wiring is 007I)

## Concrete Requirements
1. `POST /api/v1/approval-cases/{id}/approve|reject|return-for-clarification/` per §25.5-§25.7. Actor must hold the matching permission AND be a pending approver in the case snapshot; conflict exclusion hooks land in 007E but the snapshot/excluded checks must be structured so 007E only adds the conflict source.
2. Write one immutable `approval_actions` row per action (actor, role_code, decision, comments, acted_at, ip/user-agent); enforce the unique (case, approver) constraint — a second action by the same approver is rejected, not versioned.
3. Comments are mandatory for reject and return (M05-FR-008); approve accepts optional comments.
4. Case completion inside one transaction (§13.3): all required approvers approved → case `approved`, create the §15.5 sanction decision (unique per application; sanctioned amount/tenure/rate/security summary per §25.8 fields, sourced from the appraisal recommendation) and return `sanction_decision_created: true`. Any reject → case `rejected` with reason. Return → case goes back to the clarification state and the application returns to the source-defined pre-committee state via 002H guards.
5. Concurrency: two approvers acting simultaneously must not double-complete the case or create two sanction decisions; lock ordering consistent with 006F3 conventions.
6. Notify the Credit Assessment Team on completion via the 003I notification adapter and record workflow events (M05-FR-010); register entry generation is 007H.
7. Standard error contracts: acting on a closed case → contract error; non-snapshot actor → 403 per 002J2.

## Test Cases
- Joint approval: partial approvals keep the case pending; final approval completes case + sanction decision atomically; concurrent final approvals race-tested (single decision row).
- Reject and return without comments → 400; duplicate action by the same approver → rejected.
- Acting while excluded/closed/not-in-snapshot negatives; permission negatives per action code.
- Sanction decision fields match §25.8 with the appraisal's recommended facts; notification/workflow events asserted.

## Out of Scope
Conflict determination (007E), exception register (007F), general-meeting gate (007G), register generation (007H), UI (007I).

## Run-Ahead Sharpening Review (007B, 2026-07-13)

- Require the complete 007B routing snapshot and optimistic `case.version` before any action;
  unrouted version-1 shells are invalid state and must never be routed from current configuration.
- Preserve the original 006G `workflow_event_id` as submission identity. Action/completion events
  are additional rows. Source amount and authority come from immutable 007B projections, never
  request payload or a fresh rule/committee resolver call.

## Run-Ahead Sharpening Review (007C, 2026-07-13)

- Reuse the source §15.4 `ApprovalAction` model/migration introduced as 007C's read ledger; do not
  create a parallel decision table or mutate `required_approvers_json`. After every successful
  action, the 007C queue/detail public reads must immediately show the actor removed from
  `assigned_to_me`, the decision/acted-at projection populated, and all actor actions disabled.
- Execute through the same complete-routing and pending-assignment predicates that drive 007C's
  projections. Add parity tests proving any actor/action reported disabled by detail receives the
  matching write denial with unchanged case/action/sanction/audit/workflow ledgers.

## Run-Ahead Sharpening Review (Architecture Review 2026-07-13_100911, 2026-07-13)

- Consume 007C2's single case object-access and coherent-snapshot predicates before locking/writing
  an action. An action permission or `approvals.case.read` alone is never global object authority;
  an unassigned Director/custom-role reader and every contradictory snapshot receive the same
  denial as the read projection with zero action/case/sanction/evidence writes.
- Preserve serializer parity: after an action, collection/detail/status/action projections must all
  be produced through the deep approval-case module. Do not add a third case serializer or a second
  required-approver parser in the action adapter.

## Run-Ahead Sharpening Review (007A6, 2026-07-13)

- Assert action audit content, not counts: actor/type, action, case/application target, request id,
  IP/user-agent metadata, decision/comments metadata, and masked old/new case status. Evidence must
  identify only the executed action and must not claim a sanction decision or notification that the
  transaction did not create.
- Snapshot complete action/case/sanction/workflow/audit ledgers before denied, duplicate, and losing
  concurrent actions. Zero-write losers require exact equality; the winner adds only attributable
  action/completion evidence required by the stored snapshot.

## Run-Ahead Sharpening Review (007C2, 2026-07-13)

- Lock the application/appraisal/case in the established order, then re-run the public
  `is_routable_approval_case`, `can_read_approval_case`, and
  `is_pending_approval_case_actor` predicates inside that transaction before inserting an action.
  The pre-lock §44 projection is not write authority, and no action adapter may parse
  `required_approvers_json` independently.
- Require the caller's submitted case `version` and reject a stale version with the complete
  case/action/sanction/audit/workflow ledger unchanged. A contradictory snapshot stays hidden and
  non-actionable; an unassigned permission holder receives `OBJECT_ACCESS_DENIED`; an assigned but
  acted/excluded/closed caller receives the action-specific disabled-state conflict.
- Return the canonical case projection by composing `approval_case_engine` after the successful
  write. Collection, detail, and action response must agree on `current_status`, immutable routing
  provenance, per-approver decision/acted-at, and remaining actions without a new serializer.

## Risk Level
High

## Acceptance Criteria
- Approval outcomes are immutable, joint-approval complete, transactional, and produce exactly one sanction decision per application.
- All gates pass; action API examples and race-test output saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Database rules followed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
