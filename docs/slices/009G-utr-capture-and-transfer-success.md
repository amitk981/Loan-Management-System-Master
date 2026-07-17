# Slice 009G: UTR Capture and Transfer Success

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Record one replay-safe successful manual RBL transfer with unique UTR/evidence only after exact CFC
approval, then fund and activate the linked loan account atomically.

## User Value
Authorised Finance records the bank-confirmed transfer once, and the platform activates the loan
only when the exact approved instruction, amount, beneficiary, source account, UTR, and evidence
remain coherent.

## Depends On
- 009F

## Runtime Capabilities

postgresql-five-race-acceptance

## Source References
- docs/source/implementation-roadmap.md section 14
- docs/source/api-contracts.md sections 31.4 and 45
- docs/source/integrations.md sections 9.2, 9.7, 9.10, and 21
- docs/source/data-model.md sections 18.1, 18.3, 19.3, 19.4, and 34
- docs/source/functional-spec.md BR-052/M08-FR-007-M08-FR-009
- docs/source/auth-permissions.md sections 15.6-15.7, 18, and 34.7

## Prototype Reference
- sfpcl-lms/src/pages/disbursement/*
- sfpcl-lms/src/pages/loan-accounts/LoanAccount360.tsx

## Screens Involved
None directly.

## Frontend Scope
None.

## Backend/API Scope
1. Implement `disbursements.modules.transfer_success` behind one public atomic interface. Lock the
   active actor, exact 009F approved disbursement/action, account/application/member, beneficiary/
   source bank, current retained evidence document, and any UTR/idempotency winner.
2. Require source Critical `finance.disbursement.mark_success` and exact pending-transfer scope for
   an active CFC or operationally assigned Senior Manager Finance. Bare role/permission or intake
   assignment never grants scope; missing/inaccessible ids remain nondisclosing.
3. On success create one `bank_transfers` row, set only the disbursement transfer status/reference/
   timestamp/evidence, fund the loan once, transition `sanctioned -> active`, and append one exact
   loan-status history. Preserve CFC approval and all 009E/009F frozen facts.
4. Do not call a bank API, infer success from initiation/approval, send advice, update the Loan
   Register, create repayment/schedule/interest truth, or sign the post-disbursement checklist.

## Database/Model Impact
- Extend the disbursement aggregate with the protected transfer-evidence link and immutable success
  action/audit/workflow identities; add source §19.4 `bank_transfers` with amount, manual method,
  source/destination, unique normalized bank reference, status, initiated/completed timestamps.
- Atomically set `LoanAccount.disbursed_amount`, `principal_outstanding`, and `total_outstanding` to
  the exact disbursement amount; interest/charges stay zero. Set status `active` and tenure start
  from the accepted transfer date without overwriting immutable terms.
- Use at most one migration. Database constraints must block duplicate UTR, over-sanction funding,
  success without approval, and duplicate successful transfer/account funding.

## API Contracts
- Implement `POST /api/v1/disbursements/{disbursement_id}/mark-transfer-successful/` with required
  `Idempotency-Key` and exactly `bank_reference_number`, timezone-aware `disbursed_at`, and
  `bank_transfer_evidence_document_id`.
- Return only `disbursement_id`, `bank_transfer_status: successful`, `loan_account_status: active`,
  and `disbursement_advice_communication_id: null` in the standard envelope. The null is honest
  until 009H performs source §31.5; 009G must not fabricate a sent/queued advice identity.
- Exact key/payload retry returns the retained projection without writes. Changed replay, duplicate
  normalized UTR, unknown fields/query parameters, or malformed JSON/header returns stable errors.

## Permissions
Require active persisted CFC or operationally scoped Senior Manager Finance with
`finance.disbursement.mark_success` and the exact approved disbursement relation. No actor may
alter the retained maker/checker identities or bypass 009F approval.

## Audit Requirements
Atomically retain one transfer-success action, safe audit, workflow event, bank-transfer identity,
and loan-status history with ids, amount, statuses, UTR digest/masked reference, evidence id/checksum,
actor role/team/request/network facts, and outcome. Never retain bank plaintext, PAN/Aadhaar, signed
URLs/capabilities, or legal/security payloads in ledgers. Replay and losers write nothing.

## Validation Rules
- Require exact current `initiated/approved/pending` 009E/009F state and reconcile the immutable
  initiation/authorisation/task/audit/workflow/readiness/bank evidence before success.
- Require a non-empty normalized globally unique UTR/reference, an application/account-scoped
  restricted evidence document with current checksum, and a timezone-aware transfer time that is
  not before authorisation or materially in the future.
- Transfer amount/source/destination come only from the approved disbursement. Account must remain
  sanctioned and entirely unfunded; amount must be positive and within the exact sanction.
- Exact replay is zero-write. Concurrent different UTR/idempotency attempts retain one full winner;
  every loser leaves no bank transfer, balance/status, history, audit, or workflow artifact.

## Test Cases
- Public success proves exact approved source, unique UTR/evidence, one bank transfer, funded active
  account/history, safe ledgers, and no advice/register/checklist/repayment side effects.
- Reject wrong/inactive role, grant, scope, maker/approval/evidence drift, non-approved/rejected
  instructions, malformed/duplicate UTR, missing/stale/cross-object evidence, bad time, already
  funded/active account, over-sanction amount, and forged outcome fields with zero writes.
- Exact replay is zero-write; changed replay conflicts. Twice-run PostgreSQL five-caller races retain
  one complete transfer/account/history/evidence winner and no loser success facts.

## Visual Acceptance Criteria
None.

## Evidence Required
RED/GREEN logs, sanitized success/replay/conflict examples, migration/check output, focused API/
permission/state tests, twice-run PostgreSQL race evidence, and full gates. No screenshot required.

## Risk Level
High

## Acceptance Criteria
- Transfer success cannot precede exact CFC approval or exist without unique UTR/current evidence.
- Funding and activation are atomic with one manual transfer; advice/register/borrower truth remains
  absent for later slices, and invalid/stale/concurrent losers are zero-write.
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
