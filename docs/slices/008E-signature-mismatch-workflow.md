# Slice 008E: Signature Mismatch Workflow

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Goal
Record legal-document signatures and resolve authoritative borrower-signature mismatches with the
source-approved bank-letter or stamped-declaration evidence, while keeping checklist completion and
final approval with their later owners.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 008D

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
None. DocumentationHub and borrower portal wiring remain owned by 008M/008L; do not add mock or
hidden UI actions.

## Backend/API Scope
1. Add `POST /api/v1/loan-documents/{loan_document_id}/signatures/` with the exact §26.7 signer
   party type/id/name snapshot, wet-ink/digital/scanned method, pending/signed/mismatch status,
   nullable signed time, and mismatch flag.
2. Add `POST /api/v1/signature-records/{signature_record_id}/resolve-mismatch/` accepting exactly
   `mismatch_resolution_type`, `mismatch_resolution_document_id`, and remarks from §26.8. Permit
   only `bank_verification_letter` or `borrower_declaration`.
3. Reconcile the 008C Bank Verification Letter conditional through the internal checklist module
   after a real mismatch fact changes. Do not add a public checklist refresh/update route.
4. Return evidence-file identity as metadata only. Do not expose storage keys, downloads, checklist
   approval, or disbursement readiness.

## Database/Model Impact
Add §16.6 `signature_records` in `legal_documents` with protected loan-document and verifier links,
bounded signer/method/status/resolution vocabularies, indexed status/document/signer joins, and
database consistency for mismatch/resolution/signed facts. Replace only the 008C signature-id
null-only transition needed for real owned links; do not populate checklist approval signatures.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Require `documents.signature.record` for capture and `documents.signature.resolve_mismatch` for
resolution, plus canonical access to the loan document's application. Compliance Team may record
signatures; Company Secretary owns mismatch resolution. Read/generate/file-download permissions do
not imply either mutation. Unrelated document/application scope is nondisclosing.

## Audit Requirements
Every real signature create/change and mismatch resolution writes attributable old/new audit plus
workflow/version evidence with application/document/signer/evidence ids and request metadata. Exact
replay and every denied/invalid attempt write no success evidence. Checklist projection and evidence
must roll back with the owner mutation.

## Validation Rules
- A signed status requires `signed_at` and cannot carry a mismatch flag; mismatch status requires
  `signature_mismatch_flag=true`. Pending carries neither a signed time nor resolution.
- Only a mismatch record can be resolved. Bank-letter resolution requires an accessible retained
  legal Bank Verification Letter; declaration resolution requires an accessible borrower
  declaration on non-judicial stamp evidence. The evidence id must pass documents-owned provenance
  and application-scope checks; file existence alone is not authority.
- Resolution clears the active checklist mismatch blocker but never marks the Bank Verification
  Letter or another checklist item complete. Missing required witness/borrower/nominee signatures
  remain blockers owned by later execution/checklist slices.
- Preserve signer name/party snapshots and prior mismatch evidence; never rewrite history when live
  member/user details change.

## Test Cases
- Pending/signed/mismatch signature creation, exact replay, changed facts, and invalid combinations.
- Bank-letter versus declaration resolution, inaccessible/cross-application/wrong-type evidence,
  already-resolved replay, and retained old mismatch evidence.
- Compliance recorder, Company Secretary resolver, read-only/unauthorised/unrelated matrices.
- 008C Bank Verification applicability before/after mismatch and resolution without premature item
  completion, checklist approval, file access, or disbursement readiness.
- Concurrent duplicate/change attempts retain one current outcome and complete attributable history.

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
