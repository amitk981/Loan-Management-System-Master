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
- 007C

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
