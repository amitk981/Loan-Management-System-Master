# Slice 008C: Documentation Checklist Applicability

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Goal
Automatically create and expose the source §27.1 documentation-checklist index after an approved
sanction, with backend-owned applicability facts that later execution/security slices can complete.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 008B

## Runtime Capabilities

- `postgresql-five-race-acceptance`

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
None. `DocumentationHub` and `DocumentChecklist` remain owned by 008M; do not add mock or hidden UI.

## Backend/API Scope
1. Add `GET /api/v1/loan-applications/{loan_application_id}/document-checklist/` with the exact
   §27.1 standard envelope: checklist/application ids, checklist status, ordered item metadata, and
   the four-role signature-status projection. Do not add update/approve endpoints in this slice.
2. Add one idempotent checklist-applicability module and invoke it atomically when an approval case
   creates an approved sanction decision. Replays/races retain one checklist and one item per code.
3. Always index witness PAN/Aadhaar, cancelled cheque, blank-dated cheque, PoA, Term Sheet, Loan
   Agreement, and final checklist. Add Tri-party only for an authoritative subsidiary repayment
   route, SH-4 only for physical shares, CDSL pledge only for demat shares, and Bank Verification
   Letter only when an authoritative signature-mismatch flag exists.
4. Keep item applicability independent of completion. This slice creates pending/not-applicable
   facts only; 008D-008K own stamp, notary, signature, security, completion, and approvals.
5. Expose retained loan-document ids only when 008B has created them; ids are metadata and never
   become file actions or downloads.

## Database/Model Impact
Add the §16.4 `document_checklists` and §16.5 `checklist_items` tables. Enforce one checklist per
application, one item code per checklist, protected links, indexed statuses/application joins,
bounded status vocabularies, and consistent required/applicable/not-applicable combinations.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Require `documents.checklist.read` plus canonical application object scope. Compliance Team,
Company Secretary, Credit Manager, the attributable Sanction Committee cycle, and authorised audit
readers see only source-authorised applications. Permission alone must not disclose unrelated rows,
counts, loan-document metadata, or files. Automatic creation is a system-owned sanction side effect.

## Audit Requirements
One real creation writes attributable `document_checklist.created` audit and documentation workflow
evidence linked to the sanction/case/application. Exact replay, GET, and unchanged applicability
refresh write nothing. A real applicability change records old/new item facts and its source reason.

## Validation Rules
- Checklist creation requires the latest coherent terminal approval case and approved immutable
  sanction decision; pending/rejected/returned/conflict-blocked cases create none.
- `required_flag=true` items cannot be complete merely because they are applicable; creation starts
  applicable requirements as pending and inapplicable conditionals as not applicable.
- Physical and demat applicability comes only from retained shareholding-mode facts. If the source
  fact is absent or conflicting, do not guess: expose an applicability blocker for later resolution.
- Subsidiary and mismatch conditionals use authoritative persisted facts only; absence is not a
  client-computed inference.
- Checklist and item reads expose no download descriptor, storage key, enabled action, approval
  mutation, or disbursement-readiness decision.

## Test Cases
- Approved sanction creates one checklist with the always-required items; non-approved outcomes do not.
- Physical vs demat, subsidiary vs direct, mismatch vs no mismatch, and missing/conflicting source facts.
- Exact replay and five concurrent sanction completions/refreshes persist one checklist/item ledger.
- Reader/unauthorised/unrelated application matrices and metadata-only loan-document references.
- Invalid direct model states fail; audit/workflow evidence is attributable and rollback is atomic.

## Run-Ahead Sharpening Review (008A completion, 2026-07-14)

- API §27.1 defines only GET. Automatic creation is the M06-FR-001 sanction side effect; do not
  invent a public refresh/update/approve route. Later owners may call the same internal module.
- The source's Senior Manager signature is explicitly post-disbursement; project
  `not_applicable_until_disbursement` at creation and leave the action to 008K/009.
- NACH/ECS appears only in the borrower-obligations table and has no annexure/package rule. Keep it
  out of the generated MVP checklist pending the digest's recorded client clarification.
- Do not let the checklist compute or confer document-file access, final documentation approval, or
  disbursement readiness. Those remain separate permissioned owner modules.

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
