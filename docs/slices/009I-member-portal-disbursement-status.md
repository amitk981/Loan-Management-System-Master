# Slice 009I: Member Portal Disbursement Status

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Replace MP14's hard-coded finance outcome with one borrower-safe, own-application projection of the
exact SAP/disbursement/advice workflow delivered by 009A-009H3.

## User Value
The signed-in borrower can see an honest processing/disbursed state, masked destination/reference,
amount/date, and their issued advice without internal bank, approver, or evidence leakage.

## Depends On
- 009G4
- 009H3

## Source References
- docs/source/implementation-roadmap.md section 14
- docs/source/api-contracts.md sections 29-31
- docs/source/integrations.md (SAP and bank adapter behaviour)
- docs/source/data-model.md finance/SAP/disbursement tables
- docs/source/functional-spec.md
- docs/source/screen-spec-member-portal.md MP14 and sections 8.5/9.1/10
- docs/source/auth-permissions.md section 40.1

## Prototype Reference
- sfpcl-lms/src/pages/disbursement/*
- sfpcl-lms/src/pages/loan-accounts/LoanAccount360.tsx
- sfpcl-lms/src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.tsx

## Screens Involved
- MP14 Disbursement Status inside the existing Borrower Portal shell.

## Frontend Scope
1. Replace every hard-coded stage/date/amount/SAP code/UTR/account/advice value in
   `MP14_DisbursementStatus.tsx` with the authenticated API projection. Do not expose raw SAP code,
   full UTR, full account number/IFSC, evidence ids, internal actors, comments, permissions, or
   statuses that the backend did not publish.
2. Preserve the exact existing MP14 header, completion card, three-fact grid, timeline, advice card,
   icons, `StatusBadge`, button, spacing, colours, typography, and responsive layout. Change only
   labels/data/visibility/action authority. Add loading, unavailable/empty, safe blocked/error,
   unauthorized/session-expired, processing, disbursed, and advice-download states using existing
   portal alert/empty/button patterns; never add styling/components or runtime fixtures.
3. Download advice only through the portal-owned short-lived capability/content boundary. Disable
   or omit the action until the projection says the exact 009H2 advice is available; never accept a
   document/communication id, URL, recipient, or capability from static/client-owned data.

## Backend/API Scope
1. Implement `GET /api/v1/portal/applications/{loan_application_id}/disbursement-status/` behind the
   existing active `PortalAccount.member_id` self-scope. Missing/cross-member application ids share
   nondisclosing `404 NOT_FOUND`; staff tokens are `403 FORBIDDEN`; expired/inactive portal sessions
   use the shared `401` contract. The read is zero-write.
2. Compose only current owner decisions: terminal sanction/amount; current SAP request/code setup;
   exact 009E initiation; exact 009F terminal decision; exact 009G3 transfer/account/register and
   pending-advice identity; and exact 009H3 communications-owned accepted delivery. Missing, stale,
   duplicate, cross-object, or incoherent evidence must project the last safely provable borrower stage or
   `disbursement_blocked`, never infer success from copied application/account labels or expose the
   internal register/checklist action identities.
3. Return only `loan_application_id`, nullable `loan_account_id`, one stable `status_code` plus the
   MP14 borrower label, `sanctioned_amount`, nullable `disbursement_amount`, masked destination last
   four, nullable `disbursed_at`, nullable masked bank-reference last four, `advice_available`, and
   an ordered borrower-safe timeline of `{code,label,status,completed_at}`. Timeline codes cover
   documentation complete, SAP setup, payment initiated, CFC authorisation, transfer completed, and
   advice issued; pending/blocked rows expose no internal reason or actor.
4. Implement an empty-body POST capability route and authenticated GET content route for the exact
   current 009H2 borrower advice if that owner does not already expose equivalent portal-safe seams.
   Bind capability to portal account/member/application/communication/file/checksum, expire it
   after a short duration, consume it once, and audit accepted/denied download without token/content
   leakage. Return the retained borrower advice bytes with attachment and `nosniff` headers.

## Database/Model Impact
None expected. Reuse the existing portal account, 009A-009H2 owner evidence, communication/advice
artifact, and central capability/audit patterns; at most one migration only if 009H2 lacks a truthful
protected advice-file identity.

## API Contracts
- Add the exact GET projection and advice capability/content routes to
  `docs/working/API_CONTRACTS.md`. Reject unknown query parameters or non-empty capability bodies.
- Money uses decimal strings, timestamps use UTC ISO-8601, masked values never include full bank/
  UTR/SAP data, and unavailable values are honest null/false rather than fabricated copy.

## Permissions
Require an active borrower portal session whose canonical portal member owns the exact application,
loan, disbursement, and advice chain. Portal self-scope grants no internal finance/readiness/audit/
document permission; internal roles or raw ids never widen portal access.

## Audit Requirements
The status GET is zero-write. Advice capability issuance/content access uses the existing single
portal document-download audit vocabulary with safe portal/member/application/advice/file identity,
request/network context, and outcome; never retain capability, bytes, full email, UTR, bank/SAP,
PAN/Aadhaar, storage key, or internal authoriser facts.

## Validation Rules
- `disbursed` requires the exact unique 009G3 successful transfer, funded active matching account,
  current evidence checksum, sanctioned-to-active history, and coherent protected register/advice-
  intent owner links. Advice is available only when the exact 009H3 accepted communication/artifact
  remains coherent for that transfer and member.
- Earlier states follow source order and cannot skip forward: documentation complete, SAP pending/
  complete, payment initiated, CFC pending/approved, transfer complete, advice issued. Rejection,
  failed/returned transfer, stale evidence, or mixed chains produce only the safe MP14 blocked copy
  after the owning internal workflow has established it.
- Loan Register update and Senior Finance post-disbursement checklist sign-off are not prerequisites
  for honestly reporting the already completed transfer; their absence must not be fabricated as
  complete or exposed as an internal blocker.

## Test Cases
- API tests for pre-loan, SAP pending, initiation pending, CFC pending/rejected, successful transfer,
  advice available, and stale/mixed evidence; assert exact fields/masking/order and zero writes.
- Permission matrix for own/cross-member/missing application, staff token, inactive portal account,
  and session expiry. Advice capability tests cover exact one-use download, replacement/expiry,
  tamper/cross-member/cross-advice denial, checksum drift, and safe accepted/denied audits.
- Frontend interaction tests prove API-backed loading/error/blocked/processing/disbursed states,
  exact timeline/amount/masked values, enabled advice download only when authorised, session expiry,
  and no hard-coded production fixture values or `mockData` import.

## Visual Acceptance Criteria
At the existing MP14 route and borrower viewport, processing, disbursed-with-advice, and safe error
states retain the prototype composition exactly. Save screenshots for all three with real
authenticated Django responses and no blanket route interception.

## Evidence Required
Focused API/permission/download tests, frontend component/typecheck/lint/build output, sanitized
processing/disbursed/error envelopes, proof that MP14 has no runtime fixtures, and the three real-
backend screenshots above.

## Risk Level
High

## Acceptance Criteria
- MP14 shows only current borrower-owned 009A-009H3 truth and can download only the exact issued
  advice through a one-use portal boundary.
- No full bank/UTR/SAP value, internal actor/comment/status, evidence id, storage/capability value, or
  cross-member existence leaks through the API, UI, audit, or errors.
- All configured gates and real-backend visual acceptance pass.

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
