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
