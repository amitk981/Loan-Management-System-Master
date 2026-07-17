# Slice 009F2: CFC Authorisation Integrity and Bank-Evidence Closure

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement

## Depends On
- 009E3
- 009F

## Runtime Capabilities

postgresql-five-race-acceptance

## Goal

Make CFC approval/rejection consume the exact current borrower/source-bank decision and enforce one
database-valid pending/terminal aggregate with no pre-existing transfer-success truth.

## Source / Review References

- `docs/source/api-contracts.md` §§6-8 and 31.3-31.4
- `docs/source/integrations.md` §§9.1-9.7 and 9.10
- `docs/source/data-model.md` §§12.3, 19.3-19.4, 29-30, and 34
- `docs/source/auth-permissions.md` §§15.7, 16.3, 26.5, and 30
- `docs/source/codebase-design.md` §§6.5, 16.4, 26-28, 36-37, and 42
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-17_105635_architecture_review`

## Concrete Requirements

1. Add an application-owned narrow bank-decision reconciliation interface for authorisation. Under
   the application/bank locks, require the exact current `BankVerificationDecision` identity frozen
   by 009E2 and its bank/cancelled-cheque/file/checksum/verifier/action/audit/workflow/version facts.
   Changed IFSC/account hash/status, a newer/replaced decision, duplicate ledger, or cross-object
   evidence conflicts. Do not recompose legal, security, SAP, approval, or checklist readiness.
2. Consume 009E3's complete current governed source-bank lifecycle, including its activation and
   any predecessor/deactivation facts, under locks. The authorisation decision must bind the exact
   borrower decision and source-governance identities already frozen by initiation. Also reconcile
   the three frozen loan-owner creation identities (status history, audit, workflow) so a later
   mutation invalidates CFC scope and mutation through the same typed decision.
3. Before either approval or rejection, require UTR/reference, disbursed time, transfer evidence,
   advice, register flag, account funding/activation, and other 009G+ truth to remain absent/zero.
   A forged or stale pending row carrying any later-state truth conflicts without changing it.
4. Strengthen model/database constraints so a pending authorisation has no terminal checker/action/
   comments/evidence/request/audit/workflow facts and cannot have non-pending transfer truth; an
   approved/rejected authorisation has every required terminal fact, a non-empty bounded comment,
   the CFC role, and distinct maker/checker. Rejection can never coexist with processing/successful
   transfer truth; any later transfer state requires approval.
5. Centralise initiation-ledger/current-CFC-scope reconciliation into one typed internal decision
   consumed by readiness scope, authorisation, and later 009G. Remove the divergent copies in
   `disbursement_scope` and `disbursement_authorisation` without exposing private evidence through
   HTTP or creating a pass-through public owner.
6. Preserve exact §31.3 response/replay semantics, immutable terminal audit/workflow/task evidence,
   no transfer side effects, nondisclosing object errors, and one `DisbursementWorkflow` public
   mutation owner. Retain safe comments in the authoritative row and bind the audit to the exact
   comment/digest per auth §30.2.

## Test Cases

- Reproduce both review probes: change the current borrower-bank fact/decision after initiation,
  and preload pending disbursement with UTR/disbursed/register truth; approval and rejection both
  return zero-write conflict.
- Mutate each borrower/source decision, initiation action/audit/workflow/task, amount/account/member,
  and terminal decision field one at a time. CFC scope and authorisation consume the same typed
  result and fail together.
- Direct ORM/database cases reject incomplete active/terminal tuples, pending transfer success,
  rejected transfer success, missing comments/digest/request/role/team/audit/workflow, and same
  maker/checker. Prove the valid pending, approved, and rejected tuples remain migration-safe.
- Repeat approve and reject for primary CFC and governed CFC-on-non-finance-primary actors; inactive,
  unknown, missing grant, cross-object, pre-initiation, and post-terminal scope are denied. Exact
  replay is zero-write; changed/opposite replay conflicts.
- Twice run the five-caller PostgreSQL approve/reject race with genuine borrower/source owners and
  assert one complete terminal winner plus zero loser artifacts.

## Evidence Required

Failing-first review probes; aggregate constraint matrix; bank/source reconciliation manifest;
scope/authorisation parity matrix; twice-run PostgreSQL races; focused tests, Django check,
migration sync, and full configured gates.

## Risk Level
High

## Acceptance Criteria

- CFC cannot approve or reject after beneficiary/source evidence changes or when any later transfer
  truth already exists.
- The database cannot retain an incomplete or impossible authorisation/transfer tuple.
- Read scope, terminal mutation, replay, and 009G consume one exact evidence decision without
  duplicating policy or leaking private facts.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit delegated to the orchestrator only after passing configured gates
