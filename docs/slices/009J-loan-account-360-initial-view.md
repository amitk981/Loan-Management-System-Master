# Slice 009J: Loan Account 360 Initial View

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Replace the Loan Account 360 list, header, KPI row, and Summary tab's hard-coded account facts with
one scoped projection of exact 009C creation and 009G3 funding/activation/register truth.

## User Value
Staff can open a real loan account and see its canonical borrower, application, immutable terms,
funding status, balances, and dates without mistaking later repayment/interest fixtures for truth.

## Depends On
- 009I2

## Source References
- docs/source/implementation-roadmap.md section 14
- docs/source/api-contracts.md sections 30-31
- docs/source/data-model.md sections 18.1, 18.3, 19.3, and 19.4
- docs/source/functional-spec.md M08-FR-008
- docs/source/auth-permissions.md loan-account read roles/object scope

## Prototype Reference
- sfpcl-lms/src/pages/loan-accounts/LoanAccount360.tsx

## Screens Involved
- Loan Account 360 list and initial Summary view.

## Frontend Scope
1. Replace `loanAccounts`/`loanApplications` mock reads for the list, page header, KPI row, and
   Summary tab with authenticated list/detail APIs. Preserve the exact table, header, KPI cards,
   badges, tabs, spacing, colours, typography, and responsive layout; add only existing loading,
   empty, error, unauthorized, and success patterns.
2. Display only server fields. Remove client EMI/money/status/permission calculations from the
   wired initial view. Keep later tabs owned by 010M out of this slice and do not add or copy any
   fixture; do not imply repayment schedule, accrued interest, DPD, default, closure, or NOC truth
   when those owners are absent.
3. Route list selection to the existing detail composition and use the shared authenticated
   transport/session-expiry behavior. This is initial wiring only; `LoanAccount360.tsx` remains the
   010M final mock-removal owner under the binding frontend ratchet.

## Backend/API Scope
1. Add strict paginated `GET /api/v1/loan-accounts/` and
   `GET /api/v1/loan-accounts/{loan_account_id}/` reads behind the existing
   `finance.loan_account.read` and canonical loan-account scope module. Missing/inaccessible detail
   ids are nondisclosing; reject unknown filters/query parameters.
2. Compose exact 009C account/terms/status-history and, when applicable, exact 009G3 transfer,
   activation, and register evidence. Return safe account id/number, application id/reference,
   member id/display
   name, loan/facility/rate type, sanctioned/disbursed/principal/interest/charges/total amounts,
   status, tenure dates, repayment date/tenure, safe SAP setup display, and created/activated date.
3. Fail closed or return honest nullable values when creation, terms, SAP, transfer, balance, or
   activation ledgers are missing, duplicate, cross-object, or incoherent. Reads are zero-write.

## Database/Model Impact
None. Reuse 009C/009G2 protected account, terms, status history, SAP, disbursement, and transfer
evidence; no cached display/status table.

## API Contracts
Document both reads in `docs/working/API_CONTRACTS.md`. Use standard pagination/envelopes, decimal
strings, UTC timestamps, stable status vocabulary, and explicit nulls. Never return full bank/UTR,
evidence/checksum/storage ids, internal comments, idempotency/request/network facts, or sensitive
member identity.

## Permissions
Require an active persisted role/effective authority with `finance.loan_account.read` and the
existing source-defined portfolio/account scope. Role, permission, application intake assignment,
member contact, or a raw id alone never grants access; list and detail scope must be identical.

## Audit Requirements
These ordinary staff reads are zero-write and create no workflow event. Existing sensitive reveal/
download audits remain unchanged because the initial view exposes no sensitive value or file.

## Validation Rules
- A sanctioned account projects zero disbursed/outstanding balances and no activation date.
- An active account requires the exact singular 009G3 transfer, amount-equal funding, protected
  register owner relation, current transfer/register evidence, pending-or-sent advice identity,
  and sanctioned-to-active history;
  copied status or balance labels never pass. Do not expose internal register/advice identities.
- Immutable terms and member/application/SAP links must match the account's creation evidence.
- Pagination is deterministic and bounded; no client-side money/status calculation is authoritative.

## Test Cases
- API list/detail tests for sanctioned and exact active/funded accounts, decimal/timestamp/null
  serialization, strict pagination/query validation, and zero-write behavior.
- Fail-closed tests for missing/duplicate/changed creation history, terms, SAP link, transfer,
  activation history, cross-object relation, and balance/status drift.
- Permission parity for each authorised role/scope plus inactive, permission-only, role-only,
  intake-only, missing, and cross-object denial.
- Frontend interaction tests for loading/empty/error/unauthorized/list/detail states, navigation,
  exact server values, no initial-view client calculations, and no new runtime fixture/mock import.

## Visual Acceptance Criteria
At the existing staff route/viewport, save real-Django screenshots for account list, sanctioned
summary, active/funded summary, and safe error. Each must preserve the prototype table/header/KPI/
Summary composition exactly and use no blanket backend interception.

## Evidence Required
Focused API/permission/evidence and frontend interaction tests; backend check/migration sync; full
frontend typecheck/lint/test/build; sanitized list/detail envelopes; proof that the wired initial
view has no client-owned money/status calculation; and four real-backend screenshots.

## Risk Level
High

## Acceptance Criteria
- The account list/header/KPI/Summary initial view is driven only by scoped current 009C/009G3 truth.
- Stale, forged, duplicated, or cross-object evidence cannot project an active/funded account, and
  no sensitive bank/UTR/member/internal evidence leaks.
- Existing prototype composition and all configured gates/real-backend visuals pass.

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
- [ ] Ralph owns mechanical bookkeeping; record only substantive unresolved risks/decisions in `review-packet.md` and `HANDOFF` if needed
- [ ] Commit created only after passing gates
