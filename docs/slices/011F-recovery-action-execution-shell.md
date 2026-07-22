# Slice 011F: Recovery Action Execution Shell

## Status
Complete

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance

## Goal
Initiate and complete only the recovery action authorised by 011E, post verified proceeds through the
canonical loan-ledger owner, and expose a focused S57 execution UI with fair-conduct evidence.

## User Value
Company Secretary can execute an approved recovery route without uncontrolled security movement.

## Depends On
- 011E

## Runtime Capabilities

- `postgresql-five-race-acceptance`
- `localhost-e2e-server`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance.RecoveryActionPostgreSQLAcceptanceTests`
- Expected tests: 3

## Trusted Browser Acceptance

- Spec: `e2e/recovery-action-execution.e2e.spec.ts`
- Screenshot: `recovery-action-blocked.png`
- Screenshot: `recovery-action-approved.png`

## Source References
- `docs/source/api-contracts.md` §§35.9-35.10
- `docs/source/data-model.md` §21.6
- `docs/source/user-flows.md` §32
- `docs/source/screen-spec.md` S57
- `docs/source/functional-spec.md` recovery posting and ledger requirements
- `docs/source/component-spec.md` §§17.7-17.8
- `docs/source/security-privacy.md` §23
- `docs/source/auth-permissions.md` §§12.10, 20.3, 25.8, 26.7
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011F

## Scope
- Add `RecoveryAction`, `RecoveryWorkflow.initiate_recovery_action/complete_recovery_action`, and
  POST action/complete APIs with pending/completed/failed states, amount recovered, timestamps,
  remarks, and governed evidence.
- Require the exact approved decision/action, a usable matching security instrument, CS/authorised
  executor, and evidence. Delegate SH-4, CDSL, and cheque decisions to existing security-instrument
  module interfaces; never copy or mutate their custody/pledge policy directly.
- Preserve one action attempt/history per approved route. Successful completion atomically posts the
  verified recovery amount through the canonical 010A loan-ledger/balance owner, retaining the
  recovery action, source security/evidence, and compensating financial references. External SAP
  remains explicitly pending unless an existing governed adapter records real acceptance.
- Wire only the S57 execution portion of `DefaultRecoveryHub.tsx`: selected approved action,
  instrument status, checklist/evidence upload, initiate/complete controls, and recovery interaction
  log using existing UI patterns and backend `available_actions`.
- Retain call/visit/borrower-contact evidence and grievance link without debt disclosure or harassment.

## Permissions and Audit
- `recovery.action.initiate/complete` are Critical, limited to CS/authorised recovery users after
  approval; Credit/Committee/Auditor are read only.
- Initiation, external-security handoff, completion/failure, amount, evidence, and every denied action
  are correlated in immutable audit/workflow history without sensitive payloads in logs.

## Acceptance and Negative Tests
- Each SH-4/CDSL/cheque mode uses its existing owner and only the approved matching instrument/action;
  valid completion retains evidence and outcome.
- Reject missing/rejected/no-action/mismatched approval, unavailable/foreign security, missing evidence,
  wrong role/scope, negative/excess amount, complete-before-initiate, duplicate/change replay, and
  stale concurrent completion with zero partial writes.
- PostgreSQL races prove one initiation/terminal transition; failed owner call rolls back local state.
- Recovery completion and its loan-ledger movement commit together; duplicate/change replay and a
  stale concurrent loser produce no second posting, balance change, or success event.
- Reverse consumers: SH-4/CDSL/cheque custody and authority suites remain green; 011E approval remains
  immutable; API and UI expose no execution action to read-only or unapproved users.

## Non-Goals
Automating DP/bank/share sale, external SAP posting, defining sale/write-off policy, broad S53-S56
frontend wiring (011P), or grievance resolution (011N).

## Evidence
RED/GREEN orchestration/API/security-owner/permission tests; PostgreSQL races and rollback probes;
audit/fair-conduct evidence; frontend tests/typecheck/lint/build; trusted-browser screenshots for
blocked and approved execution; full backend gate.

## Risk Level
High

## Acceptance Criteria
- `REC-AC-001/004-006`, `MOD-REC-004-010`, and `API-REC-003-004` pass, including one canonical
  recovery-proceeds ledger movement and updated outstanding balance.
- Recovery UI and APIs cannot bypass approval, security ownership, evidence, or audit.

## Done Checklist
- [ ] Execution plan and TDD evidence saved
- [ ] Backend orchestration/API and focused S57 UI completed
- [ ] Security-owner, race/rollback, reverse-consumer, visual, and full gates passed
- [ ] Evidence saved; substantive risks/decisions recorded in review-packet/HANDOFF only when needed; mechanical bookkeeping left to Ralph
