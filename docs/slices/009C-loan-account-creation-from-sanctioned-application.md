# Slice 009C: Loan Account Creation from Sanctioned Application

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Create one replay-safe pre-disbursement loan account and immutable terms package from the exact
current terminal sanction without claiming funded principal, readiness, or activation.

## User Value
Finance receives a governed account identity and terms snapshot that later readiness and payment
steps can reference without re-copying mutable application or sanction facts.

## Depends On
- 009B2

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
1. Implement the source-defined `loans.modules.loan_account_lifecycle` create interface accepting
   actor, application id, exact sanction-decision id, and normalized loan-account number. Lock
   application/member/latest approval case/sanction, the current code through 009B2's public SAP
   owner selector, and current legal term evidence before one atomic create; do not extend the SAP
   owner or make a generic `finance` module the loan-account policy owner.
2. Require the exact latest approved case and its positive `sanctioned` decision. The supplied
   decision id must match that source; rejected/returned/replaced/non-terminal applications and
   caller-supplied term facts are zero-write failures.
3. Create one account in initial source state `sanctioned`, with canonical member/application/code/
   sanction links, frozen amount/type/rate/repayment facts, zero disbursed and outstanding balances,
   and no active/readiness/disbursement side effects (A-122).
4. Create its one-to-one immutable `loan_terms` in the same transaction from source-owned safe
   borrower, nominee, shareholding, purpose, rate, tenure, repayment, penalty, charge, security,
   dispute, current Term Sheet, and current Loan Agreement facts. Do not copy PAN/Aadhaar/bank
   plaintext or invent missing governed sanction terms.
5. Replay only when application, sanction id, and normalized account number exactly match the
   retained account; changed repeats conflict. PostgreSQL concurrent first creates have one account,
   terms, status-history, audit, and workflow winner with zero loser evidence.

## 008M4 Boundary Sharpening

- Consume only 009B2's public SAP owner decision/selector. Dependency guards must reject imports of
  SAP models, manual-adapter internals, retained workbook storage, or SAP exception vocabulary.
- Keep any future account list projection page-bounded; account creation may lock only the one
  supplied application and its exact current owner-issued prerequisite facts.

## Database/Model Impact
- Add source §18.1 `loan_accounts` under the `loans` owner with unique application and account number, protected member,
  sanction, and nullable active SAP-code links; positive/non-negative balance constraints; indexed
  member/status/type/repayment fields; and initial `sanctioned` status.
- Add source §18.2 one-to-one `loan_terms` with the frozen JSON/detail fields and protected nullable
  current Term Sheet/Loan Agreement document links.
- Add append-only `loan_status_histories` with the initial null→sanctioned fact. Do not add repayment
  schedules, interest histories, disbursements, or status transitions beyond creation.

## API Contracts
- Implement `POST /api/v1/loan-applications/{loan_application_id}/create-loan-account/` accepting
  exactly `sanction_decision_id` and trimmed `loan_account_number` (maximum 80 characters).
- Return the account/application/member/sanction ids, nullable active SAP-code id, canonical account
  number, `loan_account_status: sanctioned`, amount/type/rate/repayment projection, and terms id in
  the standard envelope; return no sensitive member/security payloads.
- Document stable validation, permission/object nondisclosure, stale-state, duplicate-number,
  changed-replay, and exact replay responses in `docs/working/API_CONTRACTS.md`.

## Permissions
Enforce active persisted-user `finance.loan_account.create` plus canonical application object scope
inside the service. No canonical role currently owns this Critical permission (A-121), so do not
invent a Credit Manager/Senior Manager Finance grant; test an explicit persisted grant and preserve
the production zero-grant catalogue until governance names the role.

## Audit Requirements
Atomically record one safe `LoanAccountCreated` workflow event, one create audit, and one initial
append-only status-history fact with account/application/member/sanction/code/terms ids, actor,
status, replay provenance, and outcome. Do not retain identity, bank, signed URL, storage, or legal
evidence payloads in those ledgers; replay writes nothing.

## Validation Rules
- Account number is required, trimmed, bounded to 80 characters, and globally unique under a
  canonical case/whitespace normalization that prevents equivalent duplicates.
- Require current positive sanction amount/date, source loan type (`short_term`/`long_term`), rate
  type, purpose, security, repayment date, and every non-null §18.2 term needed for truthful
  creation. Known absent governed terms fail closed with field-specific validation (no defaults).
- A linked SAP code, when present, must be the one active code for the exact member; never select by
  borrower name/PAN/Aadhaar or reactivate an inactive code.
- Denied, invalid, stale, missing-source, duplicate-number, and race losers create no partial rows or
  evidence and disclose no inaccessible parent existence.

## Test Cases
- RED/GREEN public service/API success proves exact terminal source locks, canonical response,
  zero initial balances/status, immutable safe terms, optional same-member SAP link, and exact
  audit/workflow/status history.
- Reject wrong/missing/stale sanction, non-terminal status, missing terms, malformed/unknown payload,
  duplicate/case-space account number, inactive/cross-member code, inactive actor, absent grant,
  and cross-object access with zero partial artifacts.
- Exact sequential retry returns retained ids and ledgers; changed repeat conflicts.
- Twice-run PostgreSQL five-caller races prove one account/terms/history/audit/workflow winner and
  unchanged loser ledger. Secret scans cover responses, errors, evidence, and logs.

## Visual Acceptance Criteria
None.

## Evidence Required
RED/GREEN logs, focused API/service output, sanitized response/evidence examples, migration/check
output, full gates, and twice-run PostgreSQL five-caller race evidence. No screenshot is required.

## Risk Level
High

## Acceptance Criteria
- One exact current sanction creates one replay-safe `sanctioned` account, terms package, and safe
  immutable evidence with database-backed uniqueness and PostgreSQL race proof.
- Missing/stale/forged sources, absent authority, duplicates, and changed replay are zero-write.
- Creation does not fund or activate the account, create a schedule/disbursement/readiness pass, or
  expose sensitive member/legal/security evidence.
- The Critical permission remains ungranted until governance resolves A-121; all configured gates pass.

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
