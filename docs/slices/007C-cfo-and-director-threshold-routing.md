# Slice 007C: CFO and Director Threshold Routing

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Goal
Expose routed approval cases to their approvers: list/retrieve APIs with `assigned_to_me` filtering and a resource-level `available_actions` projection, so each CFO/Director sees exactly the cases awaiting their decision.

## User Value
Committee members work a real queue routed by the matrix (M05-FR-001/003) instead of being told out-of-band which applications await them.

## Depends On
- 007B

## Source References
- docs/source/api-contracts.md §25.3 (`GET /api/v1/approval-cases/?current_status=&approval_type=&assigned_to_me=`), §25.4 (retrieve with `required_approvers` decisions, `excluded_approvers`, `available_actions`), §44 (action projection shape)
- docs/source/data-model.md §15.3 `approval_cases`
- docs/source/auth-permissions.md §12.6 (`approvals.case.read`), §16.2
- docs/source/functional-spec.md M05-FR-001/002/003 and the ten-point Sanction Committee checklist facts
- docs/source/codebase-design.md §13.1 Approval Case Engine

## Prototype Reference
- sfpcl-lms/src/pages/sanction/SanctionWorkbench.tsx (queue/detail consumer; wiring is 007I)

## Concrete Requirements
1. `GET /api/v1/approval-cases/` per §25.3: standard pagination, filters `current_status`, `approval_type`, `assigned_to_me`; `assigned_to_me=true` returns only cases whose immutable snapshot names the current user and whose decision from that user is still pending. Reject unknown params with the standard 400 pattern.
2. `GET /api/v1/approval-cases/{id}/` per §25.4: required approvers with per-approver decision/acted_at, excluded approvers, and `available_actions` in the §44 shape (approve/reject/return with enabled flag and disabled reason).
3. Object-level access: a user not in the snapshot (and without a broader source-backed read permission) gets 403/404 per the object-access harness conventions (002I); `approvals.case.read` alone must not expose assignment-scoped actions.
4. The detail response exposes the M05-FR-002 review facts needed by the checklist (eligibility, amounts, purpose, compliance, history, risk, documentation completeness) as read-through references to the owning modules' data — do not copy/denormalise business facts the owning APIs already serve; list which fields are projections in API_CONTRACTS.md.
5. Boundary behaviour: routing/authority always reflects the 007B snapshot, never a live matrix lookup.
6. Audit: read access is not audited; assignment-scope denials follow the standard 403 contract (002J2).

## Test Cases
- `assigned_to_me` returns pending-for-me cases only; acted and excluded users drop out; pagination envelope and unknown-filter rejection covered.
- Snapshot user sees enabled actions; non-snapshot user with global read sees the case per permission but no enabled actions; unauthorized user gets 403/404.
- Boundary case at exactly 500000.00 routes to the ≤5L snapshot (per 007A assumption).

## Out of Scope
Action execution (007D), conflict exclusion population (007E), sanction decision (007D response wiring), UI (007I).

## Risk Level
Medium

## Acceptance Criteria
- Approver queues derive purely from immutable snapshots with object-level enforcement.
- All gates pass; list/detail API examples saved.

## Run-Ahead Sharpening Review (007A, 2026-07-13)

- Treat 007B's stored matrix and committee projections as the only routing authority. Queue/detail
  code must not import matrix models, call the resolver again, compare against ₹5,00,000, derive
  director count, or consult the currently active committee.
- Include the stored rule id/version, committee id/version, and decision date in detail provenance;
  activate later matrix/committee versions in a regression test and prove queue membership and
  actions for the historical case remain byte-for-byte unchanged.

## Run-Ahead Sharpening Review (007A4, 2026-07-13)

- Read assignment solely from 007A4/007B's stored `required_approvers_json` and return the stored
  case `version` for later optimistic action writes. Never join current committee membership to
  decide queue inclusion or action eligibility.
- Exercise an unrelated authenticated user, a configured matrix reader who is not assigned, the
  maker, and each snapshotted authority independently. Proposal-detail eligibility from 007A4 does
  not grant approval-case object access; case access remains governed by `approvals.case.read` plus
  the approval-case object boundary.

## Run-Ahead Sharpening Review (Architecture Review 2026-07-13_083408, 2026-07-13)

- Exclude the pre-enrichment 006G shell from `assigned_to_me` and return no enabled approval action
  from detail until every 007B routing snapshot fact is populated. Empty/default snapshot JSON must
  never mean globally assigned or fall back to the current matrix/committee.
- Add contradictory fixtures: a historical case whose stored approvers differ from the current
  committee and an unrouted shell with the same amount/status. Only the stored historical snapshot
  determines queue membership; amount, current status, live configuration, and proposal-detail
  eligibility cannot infer assignment.

## Run-Ahead Sharpening Review (007A5, 2026-07-13)

- Independently route a case snapshotted to the retained historical committee and one to the current
  committee on their boundary dates. A rejected/conflicting committee backfill proposal must not
  alter either queue, detail provenance, stored case version, or action projection.
- Proposal-detail `available_actions` describes configuration governance only and grants no case
  assignment. Prove an eligible configuration checker absent from `required_approvers_json` sees no
  case action and cannot enter `assigned_to_me`.

## Run-Ahead Sharpening Review (007B, 2026-07-13)

- A routable row has non-null rule/committee ids, matching stored versions and decision date,
  `version >= 2`, a non-empty list-shaped `required_approvers_json`, and complete matrix/committee
  projections. Exclude any row missing one of those facts even if amount/status resembles a case.
- Consume the stored ordered `{role_code,user_id,full_name}` approver items unchanged; do not join
  current users or committees to rebuild assignment. Preserve `excluded_approvers_json` separately
  for 007E instead of destructively filtering the required snapshot.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
