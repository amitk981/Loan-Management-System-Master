# Slice 008G: Tri-Party Agreement Workflow

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Goal
Verify execution of the conditional Declaration / Tri-party Agreement from current generated,
borrower-signed, nominee-signed evidence without inventing a subsidiary identity aggregate,
completing the checklist, or starting repayment deductions.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 008F

## Source References
- docs/source/implementation-roadmap.md section 13
- docs/source/api-contracts.md sections 26-28
- docs/source/data-model.md document/checklist/security tables
- docs/source/Final SOP - Loan Disbursement V10 (1).pdf
- docs/source/SFPCL_Loan Sanction- Doc & Disbursement-SOP_WhatsLoan-25052026.pdf

## Prototype Reference
- sfpcl-lms/src/pages/documentation/DocumentationHub.tsx
- sfpcl-lms/src/components/loan/DocumentChecklist.tsx
- sfpcl-lms/src/pages/borrower/portal/documents/*

## Screens Involved
None directly.

## Frontend Scope
None. DocumentationHub and member-portal wiring remain owned by 008M/008L; do not add mock or hidden
UI actions.

## Backend/API Scope
1. Implement §26.6 `POST /api/v1/loan-documents/{loan_document_id}/verify/` only for the
   `tri_party_agreement` document type in this slice, accepting exactly `verification_status` and
   `remarks`; only `verified` is a success transition here.
2. Resolve applicability from the canonical frozen subsidiary-repayment fact used by 008C2. A
   verified transition requires `subsidiary_route=true`; false is not applicable and missing/
   malformed/conflicting truth remains a configuration/data blocker.
3. Require distinct current 008E `signed` rows for the application's borrower and nominee on the
   exact current-renderer tri-party loan document. A mismatch resolution does not stand in for an
   execution signature.
4. Project verification metadata into existing loan-document/checklist reads only. Do not mark the
   checklist item complete, identify/start subsidiary deduction, grant download, or claim security/
   disbursement readiness.

## Database/Model Impact
Use the retained §16.3 loan-document verification fields and §16.6 signature records. Add only the
smallest attributable verification-history model if existing audit/version/workflow ledgers cannot
retain old/new verification facts; do not add an uncited tri-party or subsidiary-company table.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Require `documents.loan_document.verify`, canonical sanctioned Stage 4 application scope, and the
current renderer contract. Compliance Team may prepare/submit evidence; only Company Secretary may
record `verified`. Generate/read/download/signature permissions do not imply verification. Wrong
type, unrelated application, absent parent, and legacy output follow the established nondisclosing
008B4/008D authority ordering.

## Audit Requirements
Every real verification transition writes attributable old/new audit, workflow, and version
evidence containing application/document/borrower/nominee/signature ids and request/network/role/
team metadata. Exact replay and every denied/invalid attempt write no success evidence. Checklist
projection and evidence roll back with the owner mutation.

## Validation Rules
- The agreement is applicable only when the frozen subsidiary repayment route is unanimously true;
  do not infer a subsidiary entity or repayment account from the boolean.
- Borrower and nominee ids must match the application's frozen/current governed parties. Both
  signature records must be `signed`, have `signed_at`, carry no active mismatch, and belong to the
  exact tri-party loan document.
- Verification requires 008B4 current renderer provenance and retains existing generation,
  template, file, stamp/notary, custody, and execution facts. Do not fabricate a third-party
  subsidiary signature that the source schema/API does not model.
- Verification alone never completes the checklist item, approves documentation, creates a
  repayment mandate, invokes security, or makes the loan ready for disbursement.

## Test Cases
- Applicable verified transition, exact replay, retained change history, and strict request fields.
- False/missing/conflicting subsidiary route; absent/pending/mismatch/wrong-party/cross-document
  borrower or nominee signature; legacy renderer and wrong document type.
- Compliance preparer, Company Secretary verifier, read-only/unauthorised/unrelated matrices.
- Checklist projection preserves applicability, completion, verifier/time/remarks, approval
  signatures, checklist status, file access, and readiness; projection conflict rolls back.
- Concurrent duplicate verification retains one current outcome and complete attributable history.

## Architecture-Review Sharpening (2026-07-14 16:10)

- Consume only 008E2's canonical current-signature selector. The verifier must not rebuild the
  application-wide signature query, trust arbitrary party UUIDs/names, or treat a capture-overwritten
  unresolved mismatch as a signed borrower/nominee fact.
- Centralise Company Secretary verification authority at the legal-document action seam and enforce
  distinct preparation/checker identity under auth-permissions §18; direct and HTTP callers must
  cross the same decision.
- Prove one public tracer from a genuine current-renderer tri-party output through canonical
  borrower/nominee signatures to verification, while keeping the subsidiary route boolean-only and
  every repayment/checklist/readiness side effect absent.

## Run-Ahead Sharpening (008E2 completion, 2026-07-14)

- Reuse `legal_documents.selectors.signature_facts_for_application`, extending its projection for
  exact loan-document and frozen party facts instead of adding a second signature query.
- Verification requires current `signed` borrower and selected-nominee rows with `signed_at`,
  non-null immutable capture makers, no mismatch, and exact 008E2 frozen ids/names. A-109 legacy
  rows, resolved mismatches, and user/witness signatures cannot satisfy either required party.
- Keep §26.6 verification response/action history independent from §26.8 mismatch resolution:
  neither permission implies the other, and unknown/wrong-stage/unrelated ids retain the same
  authority-first nondisclosure contract.

## Visual Acceptance Criteria
None.

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched.

## Risk Level
Medium

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
