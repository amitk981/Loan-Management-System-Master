# Slice 007F: Exception Approval Workflow

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Goal
Implement the exception route: cases that exceed the permissible limit (or are forced onto the exception route) require CFO + two Directors and produce an Exception Register entry whose status tracks the case outcome.

## User Value
Above-limit or policy-exception lending is possible only through the stricter authority route and always leaves a register trail (M05-FR-006).

## Depends On
- 007E2

## Source References
- docs/source/data-model.md §15.7 `exception_register_entries` (exception_type: exceeds limit / stage bypass / waiver; business_reason; risk_assessment; status lifecycle)
- docs/source/api-contracts.md §25.2 (`force_exception_route`), §25.10 (exception register read)
- docs/source/auth-permissions.md §12.6 (`approvals.exception.create` Critical), §16.2 (exceeds-limit and stage-bypass authority rows)
- docs/source/functional-spec.md M05-FR-006
- docs/slices/006D-loan-limit-snapshot-storage.md (the limit facts that define "exceeds")

## Prototype Reference
- sfpcl-lms/src/pages/registers/RegistersHub.tsx (exception register view; wiring is 007J)

## Concrete Requirements
1. Exception determination: at 007B enrichment, a recommended amount above the 006D loan-limit snapshot, or `force_exception_route: true`, selects the exception matrix rule (CFO + 2 Directors, register_required=exception) and records the exception condition/reason on the case.
2. Create the §15.7 exception register entry when the exception case is created: exception_type `exceeds_loan_limit` (or the source-backed type), description, business_reason (mandatory from the request), risk_assessment when provided, linked approval case; status `pending`.
3. Entry status follows the case outcome inside the 007D completion transaction: approved / rejected; `closed_at` set when the case closes. Register entries are system-generated — no manual create/edit API beyond the enrichment path; `approvals.exception.create` guards the system path per catalogue.
4. Stage-bypass exceptions (§16.2: CFO approval + register) reuse the same entry model with exception_type `stage_bypass`; implement the vocabulary and validation now, even if the first caller arrives later — reject unknown exception types.
5. `GET /api/v1/exception-register/?status=&exception_type=` per §25.10 with `approvals.exception_register.read`, pagination, and generated-view semantics (read-only).
6. Audit/workflow events for entry creation and status transitions.

## Test Cases
- Above-limit amount routes to the exception rule and creates a pending entry; within-limit does not.
- `force_exception_route` without business_reason → 400; entry status flips with case approval/rejection atomically.
- Register read: filters, pagination, permission negatives; no mutation endpoint exists.
- Unknown exception_type rejected.

## Run-Ahead Sharpening Review (007D, 2026-07-13)

- Attach exception status changes inside `approval_actions.record_action` after its locked coherent
  case checks and before canonical serialization. The register row must share the action transaction
  and never infer outcome from a later polling job.
- Final approval exposes the created sanction id; reject/return expose no sanction. Exception
  evidence must therefore reference the persisted action/case outcome and must not claim a sanction
  or completion artefact absent from the 007D result.

## Run-Ahead Sharpening Review (007D3, 2026-07-13)

- Exception-register identity is case/cycle-specific: enforce at most one entry per approval case,
  expose the linked case `cycle_number`, and never reuse or rewrite a returned cycle's entry when a
  corrected appraisal creates cycle N+1.
- Recompute exception routing from cycle N+1's frozen loan-limit/appraisal facts during enrichment.
  A prior returned cycle's exception condition, reason, register status, actions, and evidence are
  immutable history and cannot force or satisfy the later cycle.
- Keep the application-unique sanction decision linked only to the finally approved latest cycle;
  register projections may show multiple historical cycle rows but must make the cycle/case linkage
  unambiguous and preserve object scope before pagination.

## Run-Ahead Sharpening Review (007E, 2026-07-13)

- Consume 007E's canonical case outcome rather than independently interpreting exclusions. A
  `blocked_by_conflict` exception case has no sanction decision and its register projection must
  expose the exact case/cycle and conflict-block reason without claiming approval or rejection.
- Register status transition logic must preserve the COI-006 exception: a denied conflicted write
  adds only its denial audit and cannot create, close, or mutate an exception-register entry.
- An abstention that leaves frozen alternate authority satisfiable keeps the exception entry
  pending; a terminal conflict-blocked abstention and its communication share the existing locked
  case action transaction. Confirm the source §15.7 status vocabulary before naming that terminal
  register status; do not infer one from display text.

## Run-Ahead Sharpening Review (Architecture Review 2026-07-13_164911, 2026-07-13)

- Consume 007E2's distinct effective-authority projection. An exception case requiring two
  Directors must never become approved, close its register as approved, or expose an authority
  summary when one Director identity has filled two slots.
- Generate `authority_applied_summary` and conflict/abstention register facts only from the
  canonical history-aware case projection. Preserve original route authority, replacement mapping,
  and acted alternate identity; do not reconstruct authority from `required_approvers_json`, live
  committee membership, display role text, or register-local calculations.
- Register collection counts and cycle rows must use the corrected approval-case object boundary.
  An unused or merely conflicted committee candidate cannot learn an exception row or count; an
  authorised historical actor sees the exact cycle without gaining action authority.

## Run-Ahead Sharpening Review (007E2 delivered contract, 2026-07-13)

- Read authority/action facts only from the canonical `route_approvers`, `required_approvers`, and
  `approval_actions` projection documented in `API_CONTRACTS.md`. A replacement row carries
  `replacement_for_user_id`; register code must not re-run conflict replacement.
- Register selectors must join or delegate to the exact original/effective/acted reader projection
  before count and pagination. `routing_snapshot_is_coherent` alone is not object scope.
- `blocked_by_conflict` plus `conflict_block_reason` is the terminal no-sanction outcome for an
  unsatisfied two-Director route; preserve the immutable action list, including abstentions.

## Out of Scope
Loan-limit calculation (006C/006D), general-meeting evidence (007G), register UI (007J), waiver workflows beyond vocabulary.

## Risk Level
Medium

## Acceptance Criteria
- Every exception-routed case has exactly one register entry whose status matches the case outcome.
- All gates pass; API examples saved.

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
