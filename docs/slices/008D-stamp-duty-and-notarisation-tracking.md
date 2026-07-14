# Slice 008D: Stamp Duty and Notarisation Tracking

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Goal
Record and verify stamp-duty and notarisation facts for retained 008B loan documents through the
source §26.9-§26.10 endpoints, without implementing signatures or final checklist approval.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 008C2

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
None. DocumentationHub wiring remains 008M; do not add mock or hidden controls.

## Backend/API Scope
1. Add `POST /api/v1/loan-documents/{loan_document_id}/stamp-duty-record/` accepting exactly
   stamp amount, type, nullable number/purchase/executed dates, status, and remarks from §26.9.
2. Add `POST /api/v1/loan-documents/{loan_document_id}/notarisation-record/` accepting exactly
   nullable notary name/registration/date, bounded status, nullable evidence document id, and
   remarks from §26.10.
3. Exact replay is zero-write. A changed POST updates the one-to-one current record under a locked
   loan-document row while audit/version evidence retains the prior facts; do not mutate the
   generated template/file provenance owned by 008B.
4. Project stamp/notary status into the owning loan-document/checklist read models, but do not mark
   an item complete or approve a checklist in this slice.

## Database/Model Impact
Add §16.7 `stamp_duty_records` and §16.8 `notarisation_records`, each one-to-one with a protected
loan-document link. Use decimal money, indexed bounded statuses/numbers, protected evidence-file
metadata, and database date/amount integrity. Reuse 008B's loan-document status fields.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Require respectively `documents.stamp.record` or `documents.notary.record`, canonical access to the
loan document's application, and the Stage 4 role boundary. Compliance Team may prepare pending
facts; only Company Secretary authority may record adequate/completed verification. Credit/read
permissions never imply mutation or evidence-file download.

## Audit Requirements
Every real create/change writes attributable old/new stamp/notary audit plus version/workflow
evidence including actor, role, document/application ids, dates, status, amount, and evidence-file
identity. Exact replay and every denial write no success evidence; all owner projections roll back
with a failed mutation.

## Validation Rules
- Stamp amount must be a non-negative two-decimal string; type is physical/electronic; status is
  pending/adequate/insufficient. Adequate requires amount, executed date, and CS authority.
- Notary status is pending/completed/rejected. Completed requires name, registration number,
  notarised date, evidence file, and CS authority.
- PoA and Loan Agreement require both stamping and notarisation under BR-037/BR-043. Other document
  types may retain not-required/null owner statuses; do not invent mandatory stamping for them.
- A non-null evidence file must pass the existing documents-owned legal/application provenance and
  access check. Its id/name is metadata; the response grants no download.
- Do not hard-code ₹500 as the adequacy calculator while the digest's ₹500-versus-ad-valorem conflict
  remains unresolved. Persist the supplied amount and verification outcome; leave rate policy configurable.

## Test Cases
- Create, exact replay, changed update with retained audit history, and current read projection.
- Invalid money/type/status/date/completion requirements and missing/inaccessible/cross-application evidence.
- Compliance pending vs Company Secretary adequate/completed, read-only/unauthorised/unrelated matrices.
- PoA/Loan Agreement applicability without hard-coded adequacy calculation or premature checklist completion.
- Five concurrent changed submissions produce one current winner and a complete attributable ledger on PostgreSQL.

## Run-Ahead Sharpening Review (008A completion, 2026-07-14)

- API §26.9-§26.10 defines POST only and data-model §16.7-§16.8 defines one row per loan document.
  Use locked idempotent create/change semantics; do not invent PATCH/delete or parallel active rows.
- The SOP makes CS the stamping/notary verifier while Compliance prepares records. Keep that role
  distinction even though both operate within Stage 4.
- The unresolved stamp-rate conflict is configuration input, not a reason to omit tracking and not
  permission to encode either ₹500 or ad-valorem as the universal adequacy rule.
- Evidence metadata never grants document download, and stamp/notary completion alone never grants
  checklist approval or disbursement readiness.

## Run-Ahead Sharpening Review (008B completion, 2026-07-14)

- Resolve the target through a documents-owned loan-document authority interface that returns the
  retained application/type/current owner states. A generated-document id or list visibility is
  not stamp/notary mutation authority and must not expose the generated or template-source bytes.
- Lock the `LoanDocument` row before one-to-one stamp/notary replay/update decisions. Do not mutate
  008B's immutable application/template/generated-file/output-format linkage or reuse its generation
  replay identity for changed legal evidence.
- Project only stamp/notary owner states onto the existing nullable 008B fields. Preserve
  `execution_status=pending` and `verification_status=pending` until their owning slices produce
  separate source-required evidence.

## Architecture-Review Sharpening (2026-07-14)

- Implement stamp/notary records in the legal-documents owner established by 008B2 and consume its
  module-enforced loan-document authority. Do not reintroduce application/approval imports into the
  foundation storage app or rely on a view-only permission check.
- Treat 008B3's validated rendered output as document content, not execution evidence. Stamp/notary
  completion still requires the separate §26.9/§26.10 facts and cannot be inferred from generation.

## Run-Ahead Sharpening (008B3 completion, 2026-07-14)

- Resolve the target exclusively through the legal-documents authority interface. A structurally
  valid rendered DOCX/PDF, extracted text, page count, checksum, or renderer success is neither
  stamp adequacy nor notarisation evidence and must not prepopulate either record.
- Do not reopen generated bytes or template packages inside stamp/notary mutations. Evidence-file
  reference authority remains a separate documents-owned provenance decision, while renderer
  failures retain 008B3's zero-write guarantee and cannot create owner projections.

## Run-Ahead Sharpening (008C completion, 2026-07-14)

- Update only the linked checklist item's retained loan-document metadata projection; stamp/notary
  create/change must leave `completion_status=pending`, applicability facts, signature statuses, and
  checklist status unchanged. An inapplicable or blocked item does not become applicable through a
  stamp/notary record.
- Call any checklist projection refresh inside the same locked loan-document transaction. Exact
  stamp/notary replay must remain zero-write across the owner record, loan-document projection,
  checklist, audit, version, and workflow ledgers.

## Architecture-Review Sharpening (2026-07-14 12:50)

- Depend on 008C2's completion-preserving checklist boundary. Stamp/notary projection must call the
  narrow metadata/status update seam, never the applicability synchroniser that could reopen a
  completed item or emit a false applicability-change event.
- Accept only 008B4 current renderer-provenance loan documents as new stamp/notary targets. A legacy-
  unverified output requires explicit renderer remediation and cannot acquire legal-execution facts
  merely because its retained metadata says `generated`.

## Run-Ahead Sharpening (008B4 completion, 2026-07-14)

- Resolve stamp/notary targets through one legal-documents-owned selector using the exact 008B4
  current predicate: `legal-renderer-v1`, matching generated-file UUID, and matching SHA-256.
  Return `409 CONFLICT` for retained `legacy_unverified` or mismatched provenance before creating a
  stamp/notary row, audit, workflow event, or checklist projection.
- Treat renderer provenance fields as immutable input. Stamp/notary actions may update only their
  source-owned records and existing lifecycle projections; they must never backfill, replace, or
  reinterpret renderer contract/document/checksum snapshots.

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
