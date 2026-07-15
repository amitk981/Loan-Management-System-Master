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
Lock the application, member, terminal sanction, sent 009A request, and active SAP codes. Confirm one trimmed code (optional vendor code, SAP timestamp, restricted evidence), or reuse the active same-member code; mark the request completed and bind the application. Exact replay returns retained ids; changed facts/conflicting active code return `409` with no loser evidence. Do not create a loan account/readiness fact.

## Database/Model Impact
Complete 009A's `sap_customer_codes` shell with unique code, provenance/creator, optional vendor/timestamp/evidence, status, and one active code per member.

## API Contracts
`POST /api/v1/sap-customer-profile-requests/{request_id}/confirm/` accepts `sap_customer_code` plus optional `sap_vendor_code`, `sap_created_at`, `evidence_file_id`; returns request/code ids, completed status, and `reuse`.

## Permissions
Require active Senior Manager Finance, narrow confirm permission, and assigned-request/object scope; inaccessible ids are nondisclosing and other roles denied.

## Audit Requirements
Atomically record one confirmation/reuse workflow and audit event with request/code/member/application/actor/evidence/provenance/outcome, never identity/bank values.

## Validation Rules
Reject wrong request/application state, blank/oversize code, cross-object evidence, inactive conflicts, and evidence outside restricted scope.

## Test Cases
Test confirmation/reuse, replay/conflict, state/role/object denial, redaction, zero side effects, and PostgreSQL one-active-code/one-terminal-request winner ledgers.

## Visual Acceptance Criteria
None.

## Evidence Required
RED/GREEN logs, sanitized contract/audit examples, full gates, and twice-run PostgreSQL races; no screenshot because there is no screen.

## Risk Level
High

## Acceptance Criteria
- The named capability works through the intended backend/API/frontend path, where applicable.
- Source-doc business rules are enforced or documented as assumptions.
- Permissions and audit expectations are tested when applicable.
- The implementation stays within one small Ralph slice.

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
