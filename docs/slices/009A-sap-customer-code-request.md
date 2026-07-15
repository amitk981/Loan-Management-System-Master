# Slice 009A: SAP Customer Code Request

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Create the manual-first SAP customer-profile request boundary after a terminal sanction, freeze the
source-owned borrower/sanction facts, and generate the restricted Annexure-I Excel artifact needed
by Senior Manager Finance.

## User Value
The Credit Manager can hand Finance a complete, auditable SAP customer-master request without
copying sensitive borrower data into an ungoverned spreadsheet or creating duplicate active
requests.

## Depends On
- 008L

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
1. Add a finance/SAP-owned service that accepts the authenticated Credit Manager plus the exact
   loan-application id, locks the application/member/terminal sanction facts, and creates one active
   request only after a canonical sanctioned decision exists. Rejected, non-terminal, inaccessible,
   missing, or already-SAP-coded cases must not create a request or file.
2. Freeze the source-required request facts: application reference, borrower legal name/type,
   folio, conditionally required Aadhaar (individual only), PAN, full registered address, optional
   email/mobile, sanctioned amount/date, and only masked bank last-four plus IFSC when a current
   verified bank account exists. The caller must not be able to substitute these canonical values.
3. Resolve `assigned_to_user_id` to one active persisted Senior Manager Finance user. The actor is
   the frozen requester; assignment/display identity must come from persisted users, not client
   labels or role strings.
4. Generate a genuine `.xlsx` Annexure-I artifact containing the required outbound fields, retain
   it through the existing document/storage boundary as restricted SAP-request evidence, and link
   its file id to the request. Never place plaintext Aadhaar/PAN in audit, workflow, integration,
   error, or application logs; ordinary projections remain masked.
5. Make create replay-safe by the source identity `loan_application_id + active request`: a retry
   returns the existing draft projection and never creates a second request/file/event. Concurrent
   first requests must have one winner under PostgreSQL and leave no loser artifacts.
6. Record one immutable `SAPCustomerCodeRequested` workflow event and one audit event containing
   request/application/member/file ids, requester/assignee, status, request provenance, and outcome
   but no sensitive field values. Sending, return/correction, completion, code confirmation/reuse,
   and disbursement readiness remain owned by later Epic 009 slices.

## Database/Model Impact
- Add `sap_customer_profile_requests` with the source columns from data-model §19.1: UUID id,
  application/member FKs, indexed `request_status` (`draft` in this slice), requester/assignee FKs,
  frozen name/address/email/application-number facts, encrypted PAN and conditionally encrypted
  Aadhaar, linked Excel file, and nullable sent/completed timestamps.
- Add the source-defined `sap_customer_codes` shell (member/application links, unique code, optional
  vendor code/SAP timestamp/evidence, creator, and active/inactive status) so request creation can
  detect retained member-level codes. This slice only reads that table; 009B owns confirmation and
  all production writes.
- Add a database constraint preventing more than one active (`draft`/`sent`) request per loan
  application, plus indexes for application, member, status, and assignee queue reads.
- Keep request and code tables in one migration; do not implement completion, correction, or code
  activation in this slice.

## API Contracts
- Implement `POST /api/v1/loan-applications/{loan_application_id}/sap-customer-profile-request/`
  using the standard success/error envelope.
- Request accepts only `assigned_to_user_id`; every borrower, sanction, application, and bank value
  is server-derived. Response returns `sap_customer_profile_request_id`, `request_status: draft`,
  `excel_file_id`, and canonical assignee `{user_id, full_name}`. Sensitive fields are not returned.
- Preserve the source response fields while updating `docs/working/API_CONTRACTS.md` to document
  server-derived values, replay behavior, and stable validation/permission/conflict errors.

## Permissions
- Seed and enforce a narrow SAP-request create permission for active persisted Credit Managers.
- Require canonical application object access inside the SAP service, not only in the view.
- Senior Manager Finance assignment does not grant the actor create authority; unrelated actors and
  inaccessible application ids must follow the repository's nondisclosure contract.

## Audit Requirements
Creation writes the exact audit/workflow evidence in Backend requirement 6 atomically with the
request and file metadata. Replay returns the retained ids without duplicating evidence.

## Validation Rules
- Require a terminal sanctioned application and an immutable positive sanctioned amount/date.
- Require every applicable M07-FR-004/BR-049 field; Aadhaar is required only for an individual
  borrower, while PAN/address/application number/name are required for all borrower types.
- Reject an inactive/non-Senior-Manager assignee, missing canonical identity facts, or an existing
  active SAP customer code without creating partial rows/files/events.
- Store sensitive PAN/Aadhaar encrypted at rest and exclude full bank account values from the
  request snapshot and Excel unless a later governed SAP field contract explicitly requires them.

## Test Cases
- RED/GREEN service and API tests for exact terminal-sanction success, source-derived immutable
  fields, genuine readable `.xlsx` content, restricted file metadata, envelope, and audit/workflow
  evidence without secrets.
- Rejection/non-terminal, missing required source fact, wrong/inactive assignee, inactive actor,
  wrong role/permission, and cross-object denial each create no request/file/event.
- Sequential retry returns the same request/file ids and keeps one evidence ledger.
- Authoritative PostgreSQL two-caller race proves exactly one request/file/event winner and an
  unchanged loser ledger.
- Individual/FPC cases prove conditional Aadhaar handling; logs, errors, audit, workflow, and the
  ordinary API response never expose plaintext Aadhaar/PAN or full bank account values.

## Visual Acceptance Criteria
None.

## Evidence Required
RED/GREEN logs, focused API/service results, twice-run PostgreSQL request race, full gate logs, a
sanitized response example, and a programmatic workbook inspection showing required headings and
masked evidence. No screenshot is required because this slice has no screen.

## Risk Level
High

## Acceptance Criteria
- A Credit Manager can create one replay-safe SAP profile request only after terminal sanction.
- The request and genuine Excel artifact contain frozen canonical required facts, protect sensitive
  values at rest and in evidence, and are atomically audit/workflow logged.
- Permission, object scope, invalid-state, retry, and PostgreSQL race tests prove no partial or
  duplicate request/file/evidence writes.
- No SAP code is confirmed and no disbursement/readiness state is changed in this slice.

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
