# Execution Plan

Selected slice: `007F-exception-approval-workflow`

## Scope and source contract

- Add the source §15.7 case/cycle-specific Exception Register model with one row per approval case,
  canonical `exceeds_loan_limit`, `stage_bypass`, and `waiver` vocabulary, pending/approved/rejected
  lifecycle, application linkage, mandatory description/business reason, optional risk assessment,
  and terminal `closed_at`.
- Create the entry only through the existing §25.2 enrichment transaction when the frozen loan-limit
  facts require an exception or the caller forces the route with a non-blank business reason.
- Update an existing entry from the canonical locked case outcome inside the approval-action transaction;
  conflicted denied writes remain zero-write, while terminal `blocked_by_conflict` preserves a pending
  register row because §15.7 defines no additional terminal status.
- Expose only `GET /api/v1/exception-register/` with permission, object-scope-before-pagination,
  `status`/`exception_type` filters, standard envelopes, exact case cycle linkage, canonical authority and
  immutable action projections. Do not add mutation routes or frontend work owned by 007J.

## TDD tracer bullets

1. RED then GREEN: public enrichment for an above-limit frozen assessment selects the exception rule and
   atomically creates exactly one pending entry; within-limit enrichment creates none.
2. RED then GREEN: forced routing requires a non-blank business reason; unknown exception types are rejected
   by the exception module interface; replay is idempotent and cycle-specific.
3. RED then GREEN: final approve/reject actions atomically project approved/rejected plus `closed_at`, while
   partial approval, return, abstention, conflict denial, and conflict-blocked cases do not falsely close it.
4. RED then GREEN: register GET enforces `approvals.exception_register.read`, delegates object scope to the
   canonical approval reader selector before count/pagination, filters safely, returns cycle/authority/action
   facts, and has no POST/PATCH/DELETE route.
5. Assert exact audit/workflow creation and transition evidence through public behavior.

## Implementation and verification

- Add one migration and seed the two source permissions without changing protected configuration.
- Update the durable API contract and Epic 007 digest with the delivered projection and the source-backed
  decision that conflict-blocked rows remain pending.
- Run focused tests throughout each red/green cycle with the mandated Ralph Python interpreter, saving logs
  under `evidence/terminal-logs/`; then run backend check, migration sync, complete coverage suite, frontend
  typecheck/lint/tests/build, and repository validation-equivalent gates.
- Review the completed diff against the slice and source contract, save API examples/evidence, changed-files,
  risk assessment, review packet, final summary, and update slice/state/progress/handoff.
- Sharpen the next one or two Not Started slices only from already-opened Epic 007 source material.
