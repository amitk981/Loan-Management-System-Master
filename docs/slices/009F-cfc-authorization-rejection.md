# Slice 009F: CFC Authorization Rejection

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Record one immutable Chief Financial Controller approval or rejection for an exact pending manual-
bank disbursement while preserving maker-checker separation and creating no transfer-success truth.

## User Value
The CFC can independently approve or reject the payment instruction after reviewing its frozen
readiness, beneficiary, source-bank, amount, and maker evidence, without conflating authorisation
with execution in the external RBL portal.

## Depends On
- 009E

## Source References
- docs/source/implementation-roadmap.md section 14
- docs/source/api-contracts.md sections 29-31
- docs/source/integrations.md (SAP and bank adapter behaviour)
- docs/source/data-model.md finance/SAP/disbursement tables
- docs/source/functional-spec.md

## Prototype Reference
- sfpcl-lms/src/pages/disbursement/*
- sfpcl-lms/src/pages/loan-accounts/LoanAccount360.tsx
- sfpcl-lms/src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.tsx

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
1. Implement `disbursements.modules.disbursement_authorisation` behind one public terminal-decision
   interface. Lock the active CFC, initiated disbursement, account/application/member, 009E frozen
   initiation/readiness/bank evidence, and any existing decision before acting.
2. Accept only source decisions `approved` or `rejected` with required bounded comments. Freeze the
   checker, decision time, safe CFC role/team/request/network facts, and exact initiated evidence.
3. On approval set only `authorisation_status: approved`; on rejection set only
   `authorisation_status: rejected`. Keep transfer state pending and all UTR/disbursed/advice/
   register/account-activation fields null, false, or unchanged.
4. Close the pending CFC task with the same decision. Do not call a bank API/portal, mark transfer
   successful, change balances/status, create repayment/schedule truth, or notify the borrower.
5. Resolve CFC object scope only through the exact current 009E initiated-disbursement/CFC-task
   relation. Application intake assignment and a bare readiness/authorise permission remain
   irrelevant; replaced, closed, rejected, cross-account, or cross-member relations fail closed.

## Database/Model Impact
- Extend the 009E disbursement aggregate only where required for protected nullable CFC checker,
  authorised timestamp, bounded terminal authorisation status, comments/evidence digest, and one
  immutable action identity. Preserve source §19.3 amount/bank/maker/account relationships.
- Add no bank-transfer success, UTR, disbursed timestamp, advice, register update, schedule, balance,
  or activation row. Use at most one migration and retain historical initiated rows honestly.

## API Contracts
- Implement source §31.3 exactly:
  `POST /api/v1/disbursements/{disbursement_id}/authorise/` with JSON containing only required
  `decision` (`approved` or `rejected`) and required trimmed `comments`.
- Return only `disbursement_id`, `authorisation_status`, `bank_transfer_status: pending`,
  `authorised_at`, and the server-owned next action state in the standard envelope. Do not return
  bank plaintext, maker/checker contact data, internal evidence, or task/workflow ids.
- §45 does not require an `Idempotency-Key` for authorisation. Exact terminal replay returns the
  retained projection without writes; changed or opposite terminal replay returns stable conflict.
  Reject unknown fields and query parameters.

## Permissions
Require an active persisted `chief_financial_controller` with
`finance.disbursement.authorise` and exact disbursement/account/application object scope inside the
owner. Role strings, permission alone, or read scope do not grant the action. The checker must be
different from 009E's Senior Manager Finance maker. Missing/inaccessible ids are nondisclosing.

## Audit Requirements
Atomically retain one immutable `disbursement.authorised` or `disbursement.rejected` action, audit,
workflow transition, and CFC-task completion with safe ids/statuses, amount, maker/checker role/team,
exact initiation/readiness digest, comments, request/network context, and outcome. Never include
borrower/source bank plaintext, PAN/Aadhaar, legal/security payloads, signed capabilities, or tokens.
Exact replay writes nothing; denied and concurrent losers create no success evidence.

## Validation Rules
- Require the exact current 009E row to remain `initiation_status: initiated`,
  `authorisation_status: pending`, and `bank_transfer_status: pending`, with coherent account,
  application, member, sanctioned amount, borrower/source bank, maker, and frozen readiness facts.
- Approval/rejection must not re-evaluate readiness into a different evidence set or accept caller-
  supplied amount/bank/readiness/maker/time. Replaced or incoherent initiation evidence conflicts.
- Enforce distinct maker/checker transactionally. A second CFC or simultaneous opposite decision
  has one winner; every loser returns the retained exact replay or a zero-write conflict.
- CFC approval authorises the instruction only. 009G owns bank transfer success, UTR/evidence,
  funded balances, account activation, and later advice/register effects.

## Test Cases
- Public approve and reject paths assert exact statuses, immutable checker evidence, closed CFC task,
  safe envelopes/ledgers, and zero transfer/account/balance/register/communication side effects.
- Reject missing/wrong role or permission, inactive/checker-maker actor, cross-object/missing id,
  malformed/unknown decision/comments, non-pending/stale initiation, replaced readiness/bank facts,
  and caller-supplied outcome fields without partial writes.
- Prove CFC readiness/read scope is absent before 009E initiation, present only for the exact pending
  assigned relation, and removed when that relation is terminal or incoherent.
- Exact replay is zero-write; changed/opposite replay conflicts. Twice-run PostgreSQL five-caller
  approval/rejection races retain one complete decision/evidence winner and no loser success facts.

## Visual Acceptance Criteria
None.

## Evidence Required
RED/GREEN logs, sanitized approve/reject/conflict examples, migration/check output, focused
service/API permission and maker-checker tests, twice-run PostgreSQL race evidence, and full gates.
No screenshot is required because this slice owns no screen.

## Risk Level
High

## Acceptance Criteria
- The exact source §31.3 CFC can approve or reject one pending 009E instruction with immutable,
  maker-checker-safe, replay/race-safe evidence and a completed CFC task.
- Approval/rejection cannot claim bank execution, UTR, funding, account activation, advice, register,
  or borrower truth; invalid, stale, forged, cross-object, or concurrent losing actions are zero-write.
- All configured gates pass.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested, if needed
- [ ] Audit events tested, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
