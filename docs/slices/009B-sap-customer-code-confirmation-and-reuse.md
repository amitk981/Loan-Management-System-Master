# Slice 009B: SAP Customer Code Confirmation and Reuse

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Let Senior Manager Finance confirm or reuse one active member SAP customer code from a sent 009A request, with immutable evidence and replay.

## User Value
Finance can finish the manual SAP handoff once and reuse the governed member code without duplicate customer masters.

## Depends On
- 009A

## Runtime Capabilities

- `postgresql-five-race-acceptance`

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
1. Own the missing draft→sent boundary from API §29.2. Only the Credit Manager who owns the 009A
   request may send its exact retained Excel file to its frozen active Senior Manager Finance
   assignee through the communication/task adapter. Retain sent time, remarks, adapter message/task
   identity, workflow, and audit evidence atomically; exact replay is zero-write and changed repeat
   conflicts.
2. Lock the application, member, current terminal sanction, sent request, assignee, and active SAP
   code rows before completion. Only the frozen active Senior Manager Finance assignee may complete.
   A draft/returned/completed request, changed terminal cycle, wrong assignee, or inaccessible id is
   nondisclosing/zero-write.
3. Confirm one trimmed unique `sap_customer_code` (optional trimmed vendor code, SAP timestamp,
   restricted confirmation document, and notes) or reuse the one active same-member code. Bind the
   completed request and application to that retained member code; never create a second member code.
4. Existing active same-member code is the conservative reusable authority until an outstanding-loan
   owner exists; never infer reuse from name/PAN/Aadhaar or invent an outstanding-loan status. A code
   owned by another member always conflicts even when the request body otherwise matches.
5. Exact send/complete replay returns retained ids and evidence without duplication. Changed facts,
   conflicting active codes, concurrent confirms, or concurrent requests for the same member return
   `409` and leave no loser code/request/event/file/communication artifacts.
6. Do not create a loan account, SAP payment entry, readiness pass, disbursement, or borrower message.

## Database/Model Impact
Complete 009A's `sap_customer_codes` shell with unique code, provenance/creator, optional vendor/
timestamp/restricted confirmation evidence, status, and one active code per member. Complete the
request's sent/completed timestamps and immutable links without a second migration unless 009A's
schema genuinely lacks a source field. Database constraints enforce global code uniqueness, one
active member code, terminal request state, and evidence/application ownership where expressible.

## API Contracts
- `POST /api/v1/sap-customer-profile-requests/{request_id}/send/` accepts only `remarks` and returns
  request id, `sent` status, sent time, assignee, and retained communication/task id in §6 envelope.
- `POST /api/v1/sap-customer-profile-requests/{request_id}/complete/` follows source §29.3 and accepts
  `sap_customer_code`, optional `sap_vendor_code`, `created_at_sap`,
  `confirmation_document_id`, and `confirmation_notes`. It returns request/code/member/application
  ids, `completed` status, `reuse`, and safe evidence metadata; no identity/bank plaintext.
- Add `GET /api/v1/members/{member_id}/sap-customer-code/` only as the source §29.4 masked, scoped
  read boundary needed to prove retained member reuse; it never reveals request identity fields.

## Permissions
Seed separate narrow send and complete/read permissions. Send requires active owning Credit Manager;
complete requires the active frozen Senior Manager Finance assignee. Both enforce request/application/
member object scope inside the service; global permission or role strings are never sufficient.

## Audit Requirements
Atomically record one send workflow/audit/communication ledger and one completion-or-reuse workflow/
audit ledger with request/code/member/application/actor/assignee/evidence/provenance/outcome. Never
retain Aadhaar, PAN, address, bank values, or signed URLs in those ledgers.

## Validation Rules
- Require current terminal sanction and the exact sent 009A request/assignee.
- Trim codes/notes; reject blank or >120-character customer/vendor codes, malformed/future SAP time,
  unknown fields, and code case/whitespace variants that would evade uniqueness.
- Confirmation evidence, when supplied, must be one current restricted file the assignee can
  reference for this request/application; cross-object, portal, template, or ordinary public files
  are nondisclosing.
- Reject inactive/conflicting member codes and a code owned by another member. Do not silently
  reactivate or overwrite historical code rows.

## Test Cases
- Public send success/replay/change/state/owner/role/object matrices assert exactly one adapter task,
  workflow, audit, timestamp, and zero denied artifacts.
- Public completion covers new code, same-member reuse, other-member duplicate, optional fields,
  evidence provenance, masked GET, replay/change, and draft/returned/stale-cycle/assignee denial.
- Secret scans cover responses, errors, audit/workflow/communication payloads, and application logs.
- Twice-run PostgreSQL races cover two new-code confirmations and two sent requests for the same
  member; assert one active code, one terminal request, exact winner ids, and zero loser ledgers.

## Visual Acceptance Criteria
None.

## Evidence Required
RED/GREEN logs, sanitized send/complete/read and audit/communication examples, full gates, and both
twice-run PostgreSQL race families; no screenshot because this slice has no screen.

## Risk Level
High

## Acceptance Criteria
- Credit Manager can send the exact governed 009A request once; only its assigned Senior Manager
  Finance can complete it.
- A member receives or reuses exactly one active SAP customer code with immutable safe evidence.
- Replay, duplicate, wrong-state/role/object/evidence, and PostgreSQL races are zero-loser-write.
- No loan account, readiness, payment, or disbursement truth is created.
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
