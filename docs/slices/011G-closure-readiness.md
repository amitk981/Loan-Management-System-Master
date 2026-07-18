# Slice 011G: Closure Readiness

## Status
Not Started

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance

## Goal
Derive named closure blockers from canonical servicing facts and perform one controlled financial
close only when principal, interest, charges, ledger, and recovery checks pass.

## User Value
Staff can close a settled loan confidently and see exactly why an unsettled loan is blocked.

## Depends On
- 011F

## Source References
- `docs/source/api-contracts.md` §§36.1-36.2
- `docs/source/data-model.md` §22.1
- `docs/source/product-requirements.md` §11.28
- `docs/source/functional-spec.md` M13-FR-001-003, M13-FR-011
- `docs/source/screen-spec.md` S58
- `docs/source/test-plan.md` §13.19, API-CLOSE-001-002
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011G

## Scope
- Add the closure owner, `LoanClosure`, and `LoanClosureModule.evaluate_readiness/close`.
- Implement GET `/api/v1/loan-accounts/{id}/closure-readiness/` with named pass/fail checks and
  server-derived total outstanding; include principal, interest/approved adjustment, charges,
  unresolved ledger/reconciliation, pending recovery, and applicable security-task facts.
- Implement POST `/api/v1/loan-accounts/{id}/closure/` for one full-repayment financial closure,
  freezing source balances/checks, actor/time/type/notes, and creating explicit NOC, security-return,
  and archive requirements for 011H-J.
- Preserve the source conflict explicitly: API §36.2 reports account `closed` after financial close,
  while M13-FR-011 reserves terminal completion for the full checklist. Do not claim `Fully Closed
  and Archived`; post-close mutations are forbidden except controlled NOC/security/archive actions.
- Re-evaluate readiness inside the same transaction as close; client-visible readiness is not authority.

## Permissions and Audit
- Scoped read via `closure.readiness.read`; Critical `closure.loan.close` for Credit/CS according to
  the source stage matrix; Auditor read only.
- Readiness is non-mutating; close and denied/stale attempts append safe audit/workflow evidence.

## Acceptance and Negative Tests
- Exact zero principal/interest/charges and no other blockers closes once and returns required tasks;
  each named blocker independently prevents close with no writes.
- Reject caller-forged zero, stale readiness, wrong loan/scope/role, unsupported closure type,
  duplicate/change replay, unresolved recovery/ledger, and direct mutation of a closed account.
- PostgreSQL close-vs-repayment/recovery and duplicate-close races prove a locked fresh decision.
- Reverse consumers: repayment allocation, interest, loan status history, DPD/default/recovery, and
  security package suites remain green; closing never deletes their retained records.

## Non-Goals
Settlement/write-off policy, NOC (011H), security return (011I), archive (011J), broad UI wiring, or
changing canonical balance calculations.

## Evidence
RED/GREEN readiness/close/API/permission tests; migration and PostgreSQL races; one-blocker-at-a-time
matrix; audit/status-history proof; full backend gate and response examples.

## Risk Level
Medium

## Acceptance Criteria
- `CLOSE-AC-001-002`, `MOD-CLOSURE-001-003/010`, and `API-CLOSE-001-002` pass.
- Financial closure is fresh, backend-derived, unique, auditable, and does not misstate terminal archive.

## Done Checklist
- [ ] Execution plan and TDD evidence saved
- [ ] Closure model/module/readiness and close APIs completed
- [ ] Blocker matrix, concurrency, reverse-consumer, and full gates passed
- [ ] Evidence saved; substantive risks/decisions recorded in review-packet/HANDOFF only when needed; mechanical bookkeeping left to Ralph
