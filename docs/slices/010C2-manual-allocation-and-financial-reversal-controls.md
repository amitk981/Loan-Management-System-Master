# Slice 010C2: Manual Allocation and Financial Reversal Controls

## Status
Not Started

## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Origin
Owner-chat source-coverage audit on 2026-07-19 identified M09-FR-009 and the S44 reversal action as
unowned by the executable queue.

## Goal
Add one governed correction path for a repayment that cannot be auto-allocated and one immutable
reversal path for a posted financial movement, without allowing operators to rewrite ledger history.

## User Value
Accounts can resolve genuine matching exceptions and correct an erroneous posting with approval,
reason, and complete audit evidence while balances remain reproducible.

## Depends On
- 010D

## Source References
- `docs/source/functional-spec.md` M09-FR-009 and M09-FR-010 through M09-FR-011
- `docs/source/screen-spec.md` S44 Actions and Controls, especially reversal with permission/reason
- `docs/source/data-model.md` repayment allocation, loan ledger, and immutable history sections
- `docs/source/auth-permissions.md` finance repayment and elevated financial correction controls
- `docs/source/security-privacy.md` financial transaction controls
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md`

## Prototype Reference
- `sfpcl-lms/src/pages/repayments/RepaymentsHub.tsx`
- `sfpcl-lms/src/components/loan/RepaymentLedger.tsx`

## Screens Involved
None in this slice; `010M` owns staff frontend wiring.

## Frontend Scope
None.

## Backend/API Scope
- Consume the unmatched/exception receipt and bank-line decision owned by 010D. Add the public
  manual-allocation action for that exact exception; it must reference terminal approval evidence,
  accept a mandatory bounded reason, and delegate the actual balance transition to the canonical
  allocation owner from 010C. This slice owns the financial allocation, while 010D owns statement
  ingestion, candidate matching, and the unmatched queue.
- Add a public reversal action for an eligible posted repayment/ledger movement. Preserve the
  original row and append compensating ledger/allocation truth; never edit or delete history.
- Return retained truth for exact idempotent replay and reject changed, duplicate, cross-loan, stale,
  already-reversed, or non-exception attempts before any financial write.
- Do not add refund settlement, charge ordering, write-off, cash handling, or a generic ledger editor.

## Database/Model Impact
At most one non-destructive migration for approval/reason/idempotency/reversal linkage and the
constraints needed to retain one accepted correction per source movement.

## API Contracts
Extend the repayment contracts in `docs/working/API_CONTRACTS.md` with exact manual-allocation and
reversal request/response/error shapes.

## Permissions
Use the narrow source-backed repayment-allocation authority for manual allocation and an elevated
financial-reversal authority for reversal. If the source catalogue does not name the latter code,
default-deny, record the bounded mapping assumption, and grant it to no role automatically.

## Audit Requirements
Audit request, approval evidence, reason, before/after balances, compensating references, outcome,
and every denial without copying bank evidence or sensitive values.

## Validation Rules
- Manual allocation is legal only for an unresolved 010D exception where automatic matching failed
  and terminal approval covers the exact proposed destination and amount.
- Reversal amount and source are server-owned; the compensating movement restores balances exactly
  and cannot make principal, interest, or unallocated amounts negative.
- Original financial and audit rows remain immutable.

## Trusted PostgreSQL Acceptance
- Test: `sfpcl_credit.tests.test_repayment_adjustment_api.RepaymentAdjustmentPostgreSQLAcceptanceTests`
- Expected tests: 4

## Test Cases
- RED then GREEN: approved exception allocation succeeds once and delegates principal-first math to
  010C; missing/pending/foreign approval, amount drift, and changed replay produce zero writes.
- RED then GREEN: authorised reversal appends one compensating movement and restores the exact prior
  balances; duplicate and concurrent reversal retain one winner.
- Permission, object-scope, stale-state, idempotency, immutable-history, and audit sanitisation tests.
- Reverse-consumer tests keep 010A through 010C and Epic 009 opening-balance truth green.

## Visual Acceptance Criteria
Not applicable (backend only).

## Evidence Required
Saved RED/GREEN commands and output; API examples; approval and permission matrix; before/after and
compensating ledger proof; twice-run PostgreSQL acceptance; reverse-consumer and full gates.

## Risk Level
High

## Acceptance Criteria
- Exception allocation and reversal are explicit, approved, reasoned, atomic, idempotent, and audited.
- No path rewrites immutable ledger history or bypasses the 010C allocation owner.
- Required focused, PostgreSQL, reverse-consumer, and full gates pass.

## Done Checklist
- [ ] Execution plan written
- [ ] TDD RED/GREEN evidence saved
- [ ] Code and contracts implemented
- [ ] Migration and database constraints verified, if needed
- [ ] Permissions and audit tested
- [ ] PostgreSQL acceptance passed twice
- [ ] Full gates passed
- [ ] Risk and review evidence completed
- [ ] Commit delegated to the orchestrator after gates
