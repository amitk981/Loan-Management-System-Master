# Slice 009D: Disbursement Readiness Service

## Status
Complete

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Return one server-owned, replay-safe pre-initiation readiness decision with every source blocker
shown explicitly, without initiating payment or claiming downstream Finance/CFC actions.

## User Value
Senior Manager Finance can see exactly why a sanctioned loan account can or cannot proceed to
payment initiation, using current governed evidence rather than a manual checklist or client math.

## Depends On
- 009C

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
1. Implement the source-defined `disbursements.modules.disbursement_readiness` coordinator for one
   loan account. Resolve the canonical account through 009C's loan owner, SAP truth through 009B2's
   public owner selector, and exact current terminal sanction, verified bank, final documentation/
   checklist approvals, and security evidence through their owning read seams inside one consistent
   transaction; do not recreate those policies in a generic `finance` module.
2. Return deterministic checks in source order for: current sanction, sanctioned loan-account state,
   conditional exception/general-meeting approval, active KYC/appraisal, documentation checklist,
   Company Secretary/Credit Manager/Sanction Committee approvals, security package, PoA, Term Sheet,
   Loan Agreement, applicable SH-4/CDSL path, blank cheque, cancelled-cheque/verified bank account,
   signature-mismatch resolution, active bound SAP code, configured source bank account, and amount
   within sanction. Every check has stable code/label and `pass` or `fail`; no check is omitted.
3. `ready_for_disbursement` is true only when every pre-initiation check passes. Senior Manager
   Finance initiation/final verification and CFC authorisation are downstream 009E/009F actions,
   not synthetic readiness passes; do not create either here.
4. Keep the service read-only: no checklist refresh/completion, evidence repair, loan activation,
   payment/disbursement, balance, SAP posting, task, communication, or borrower-status side effects.

## 009B2 Owner Contract Sharpening

- Compare the account's nullable SAP link only with
  `SapCustomerProfileModule.get_customer_code_for_member(member_id)`. A missing decision, non-active
  status, or member/application/code mismatch fails the named SAP readiness check.
- Readiness must not import SAP/Finance models, request delivery capabilities, decrypt Annexure-I,
  call adapter status, or infer a pass from a masked/raw code. The owner decision is the complete
  SAP prerequisite boundary and the GET remains zero-write.

## Database/Model Impact
None expected. Consume source-owned current evidence and the 009C account/SAP links; do not add a
parallel readiness table, cached boolean, copied checklist/security status, or migration unless a
source-required immutable evidence identifier is genuinely absent.

## API Contracts
- Implement source §31.1 exactly:
  `GET /api/v1/loan-accounts/{loan_account_id}/disbursement-readiness/`.
- Return `loan_account_id`, `loan_application_id`, `ready_for_disbursement`, `evaluated_at`, and the
  complete ordered `checks[]` projection in the standard envelope. Each item contains only `code`,
  `label`, `status`, and a safe blocker reason when failed; never include identity/bank plaintext,
  document storage/capability values, cheque/BO values, or source evidence payloads.
- Missing/out-of-scope account ids are nondisclosing; stale/incoherent evidence is a failed check,
  not a fabricated pass or an unhandled exception. Reject unknown query parameters.

## Permissions
Require an active persisted actor with `finance.disbursement.readiness` and exact loan-account/
application object scope inside the service. Global permission or Finance/CFC role strings alone do
not grant object access; test permitted Senior Manager Finance/CFC contexts plus wrong-role,
missing-permission, cross-object, inactive-user, and inaccessible-id denials.

## Audit Requirements
Readiness evaluation is a read projection and writes no workflow/audit/business row. Later initiation
must freeze or reference the exact readiness evidence it consumes; ordinary GET retries stay zero-write.

## Validation Rules
- Require the account's exact application/member/sanction relationships and source state `sanctioned`;
  an active account or changed/rejected/returned sanction cannot be presented as pre-initiation ready.
- Require the active SAP code linked by 009C to be the same active code retained for the exact member;
  inactive, cross-member, missing, or superseded codes fail the SAP check.
- Documentation/security checks must use current source-owned terminal facts, including conditional
  applicability and exact completion/approval evidence; never trust copied JSON or status labels.
- Bank readiness uses the current verified cancelled-cheque/bank evidence and only safe last-four/IFSC
  internally. Source-bank configuration must be active/effective; if its governed owner is absent,
  return an honest failed `source_bank_account_configured` check and record the open owner rather than
  inventing an account.
- Readiness is fail-closed and deterministic under concurrent evidence changes; a mixed-version
  projection or inaccessible required evidence returns failed checks and no side effects.

## Test Cases
- Public success and all-fail examples assert the exact ordered check vocabulary and aggregate flag.
- Parameterized tests flip every source fact independently, including each conditional exception,
  general-meeting, SH-4/CDSL, signature, SAP, bank, checklist-approval, and configuration blocker.
- Permission/object/nondisclosure tests cover missing auth/grant, wrong role/object, inactive actor,
  missing id, and secret-free responses/errors/logs.
- Regression tests prove the coordinator calls source-owned seams, rejects stale/mixed relationships,
  is query-bounded, and creates no audit/workflow/account/payment/readiness/communication artifacts.

## Visual Acceptance Criteria
None.

## Evidence Required
RED/GREEN focused logs, sanitized ready/all-blocked API examples, per-check traceability, query/read-
seam proof, migration check, and full gates. No screenshot because this slice has no screen.

## Risk Level
High

## Acceptance Criteria
- The §31.1 route returns a complete, source-owned, deterministic readiness decision and all blockers.
- No missing, stale, conditional, cross-object, or inaccessible source evidence can become a pass.
- Readiness evaluation creates no payment, approval, account-state, balance, task, communication, or
  borrower truth, and all configured gates pass.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated, if needed
- [x] Database rules followed, if needed
- [x] Permissions tested, if needed
- [x] Audit events tested, if needed
- [x] Visual evidence saved, if frontend
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates
