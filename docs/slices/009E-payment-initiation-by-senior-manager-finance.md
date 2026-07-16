# Slice 009E: Payment Initiation by Senior Manager Finance

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Create one replay-safe manual-bank disbursement initiation only after the exact current 009D
readiness decision passes, without claiming CFC authorisation, transfer, UTR, funding, or activation.

## User Value
Senior Manager Finance can record the verified RBL-portal payment instruction and place it in the
CFC queue while the platform preserves the exact beneficiary, amount, readiness, and maker facts.

## Depends On
- 009D2

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
1. Implement `disbursements.modules.disbursement_initiation` behind one public create interface.
   Lock actor, account/application/member, current 009D readiness decision and its exact evidence
   identities, current verified borrower bank account/cancelled cheque, and governed active source
   RBL account before one atomic create.
2. Require an active persisted Senior Manager Finance user with the canonical Critical permission;
   the actor must not supply borrower names/account text, readiness flags, sanction facts, account
   status, or CFC/transfer outcomes.
3. Create only source state `initiation_status: initiated`, `authorisation_status: pending`, and
   `bank_transfer_status: pending`, retaining maker/time/comments, exact loan/application/member,
   amount, borrower/source bank ids, manual payment method, and idempotency identity.
4. Produce one safe CFC task/action projection after persistence. Do not call a bank API, mark the
   bank portal transfer successful, create a UTR, alter loan balances/status, update the Loan
   Register, or notify the borrower.

## Database/Model Impact
- Add source §19.3 `disbursements` under the `disbursements` owner with protected loan/application/
  borrower-bank/source-bank/maker links, positive amount, bounded initial statuses, unique retained
  idempotency identity, nullable CFC/transfer/advice fields, and indexed account/status fields.
- Do not add a successful `bank_transfer`, UTR, disbursed timestamp, advice, schedule, or account-
  activation row in this slice. Preserve later 009F/009G fields as null/false.

## API Contracts
- Implement `POST /api/v1/loan-accounts/{loan_account_id}/disbursements/initiate/` with required
  `Idempotency-Key` and exactly `disbursement_amount`, `borrower_bank_account_id`,
  `source_bank_account_id`, and trimmed `final_verification_comments`.
- Return only `disbursement_id`, `initiation_status: initiated`,
  `authorisation_status: pending`, and `bank_transfer_status: pending` in the standard envelope.
- Stable errors cover malformed/unknown payload, missing/changed idempotency, authority/scope,
  stale/failed readiness, amount/bank mismatch, and duplicate active initiation.

## Permissions
Require active persisted `senior_manager_finance` plus `finance.disbursement.initiate` and canonical
loan-account/application scope inside the owner. CFC authorisation remains `009F`; maker and future
checker must be distinct. Missing/inaccessible account ids are nondisclosing.

## Audit Requirements
Atomically record one `disbursement.initiated` audit, one initiated workflow event, and one CFC task
with safe ids, amount, statuses, maker role/team/time, readiness identity/digest, idempotency digest,
request/network context, and outcome. Never retain bank plaintext, PAN/Aadhaar, signed URLs, tokens,
or legal/security evidence payloads in those ledgers. Replay writes nothing.

## Validation Rules
- Require the 009C account to remain `sanctioned`, unfunded, and linked coherently to the exact
  application/member/sanction; amount must be positive, no greater than sanctioned amount, and
  equal the amount re-evaluated by the current passing 009D readiness owner.
- The borrower bank id must be the current verified same-member/application account and cancelled-
  cheque decision consumed by readiness. The source bank id must be the governed active SFPCL RBL
  account consumed by readiness; caller-supplied account text is forbidden.
- Exact idempotency-key and canonical payload retry returns retained ids/statuses. Reusing a key with
  changed facts, a second active initiation, stale/failed readiness, wrong beneficiary/source bank,
  invalid amount, or any replaced evidence is zero-write.
- MVP mode records a manual bank-portal instruction only; bank APIs/file exchange/webhooks remain
  future adapters.

## Test Cases
- Public service/API success proves exact passing readiness and bank/source evidence, canonical
  initial statuses, safe ledgers/task, and zero account-balance/status/transfer side effects.
- Reject wrong role/grant/scope, inactive maker, missing/failed/stale readiness, changed account/
  sanction/SAP/legal/security/bank/source evidence, amount mismatch/overflow/zero, malformed or
  unknown payload/header, and maker-checker overlap with zero partial artifacts.
- Exact replay returns retained projection and creates no new task/audit/workflow; changed replay
  conflicts. Twice-run PostgreSQL races retain one complete initiation/evidence winner.

## Visual Acceptance Criteria
None.

## Evidence Required
RED/GREEN logs, sanitized request/response and ledger examples, migration/check output, focused
service/API tests, twice-run PostgreSQL race evidence, and full gates. No screenshot is required.

## Risk Level
High

## Acceptance Criteria
- One Senior Manager Finance initiation is possible only from current passing readiness and exact
  governed borrower/source-bank facts, with replay-safe durable maker evidence and a CFC task.
- Creation remains manual-bank MVP truth and does not authorise/execute transfer, record a UTR,
  fund/activate the account, update registers, or communicate with the borrower.
- Invalid, stale, forged, duplicate, or concurrent losing requests are zero-write; all configured
  gates pass.

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
