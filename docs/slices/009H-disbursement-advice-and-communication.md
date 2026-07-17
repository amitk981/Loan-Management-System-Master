# Slice 009H: Disbursement Advice and Communication

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Generate and send one replay-safe borrower disbursement advice only from the exact successful 009G
transfer, without changing financial, transfer, register, or checklist truth.

## User Value
The borrower receives a traceable advice for the funds actually transferred, while staff can prove
the message content, recipient, delivery attempt, and source UTR without exposing bank secrets.

## Depends On
- 009G

## Source References
- docs/source/implementation-roadmap.md section 14
- docs/source/api-contracts.md section 31.5
- docs/source/integrations.md sections 9.1-9.2 and 19.3
- docs/source/functional-spec.md BR-054/M08-FR-010

## Prototype Reference
- sfpcl-lms/src/pages/disbursement/*
- sfpcl-lms/src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.tsx

## Screens Involved
None directly.

## Frontend Scope
None.

## Backend/API Scope
1. Implement `disbursements.modules.disbursement_advice` behind one public send interface. Lock the
   actor, exact successful 009G disbursement/transfer/account/member, approved current advice
   template, canonical borrower contact, and any retained communication before acting.
2. Render one safe advice from server-owned application/account/amount/date/masked UTR facts and
   send through the established communication adapter. Persist the communication id on the
   disbursement only after adapter acceptance; retries never send twice.
3. Do not change transfer/CFC status, balances, loan status, terms, schedule, Loan Register,
   checklist approvals, or create a second transfer/advice.

## Database/Model Impact
Use the existing protected nullable `disbursement_advice_communication` relation and communication/
template evidence. Add no financial table or migration unless one immutable advice-action identity
cannot be retained by existing owners; at most one migration.

## API Contracts
- Implement `POST /api/v1/disbursements/{disbursement_id}/send-advice/` with exactly `channel` and
  `recipient_email` as source §31.5. MVP accepts only `email`, and the supplied email must normalize
  to the member's current canonical address; caller text never overrides borrower identity.
- Return only `disbursement_id`, `disbursement_advice_communication_id`, safe delivery status, and
  sent/accepted timestamp in the standard envelope. Reject unknown fields/query parameters.
- Exact retry returns the retained projection without a second adapter invocation; changed channel/
  recipient or a second retained communication conflicts.

## Permissions
Require an active persisted Senior Manager Finance or CFC with the source communication/send grant
and exact successful-disbursement scope. Missing/inaccessible ids are nondisclosing; role,
permission, intake assignment, or borrower contact alone never grants access.

## Audit Requirements
Atomically retain one `disbursement.advice_sent` action/audit/workflow plus the communication's
template/version, safe recipient identity, channel, related disbursement/account ids, amount,
masked UTR, request/network context, adapter outcome, and timestamp. Do not log full bank details,
PAN/Aadhaar, document URLs/tokens, or unrelated evidence. Replay writes nothing.

## Validation Rules
- Require exact current 009G successful transfer, unique retained UTR/evidence, active funded loan,
  coherent member/application/account, and no existing advice.
- Require one approved effective template whose declared variables exactly cover the advice data.
  Fail closed on missing/ambiguous template, absent canonical borrower email, stale transfer/account
  evidence, adapter rejection, or changed replay.
- Advice may describe only the completed transfer and cannot claim Loan Register/checklist updates.
  Failed adapter attempts must not set the disbursement advice relation or a sent status.

## Test Cases
- Public success proves exact template merge, canonical recipient, one adapter call/communication,
  safe ledgers, retained link, and no financial/register/checklist side effects.
- Reject wrong/inactive role/grant/scope, missing/failed/stale transfer, inactive/unfunded loan,
  missing/ambiguous template, wrong channel/email, unknown fields, and adapter failure with no false
  sent/link evidence.
- Exact replay is zero-write/no-resend; changed replay conflicts; a concurrency test retains one
  accepted advice and no duplicate adapter/audit/workflow facts.

## Visual Acceptance Criteria
None.

## Evidence Required
RED/GREEN logs, sanitized advice/replay/failure examples, focused API/adapter/permission tests,
migration/check output if applicable, and full gates. No screenshot required.

## Risk Level
High

## Acceptance Criteria
- One advice is sent only for the exact successful transfer to the canonical borrower email through
  the governed adapter/template path, with replay-safe evidence and no financial side effects.
- Invalid, stale, forged, duplicate, or failed delivery attempts cannot create sent/advice truth.
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
