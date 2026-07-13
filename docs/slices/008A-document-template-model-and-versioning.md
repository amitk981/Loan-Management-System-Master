# Slice 008A: Document Template Model and Versioning

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Goal
Create the versioned Document Template catalogue and §26.3 API used by later generation slices,
without generating borrower documents or resolving conflicted Annexure lettering.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 007I

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
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
1. Add `GET/POST /api/v1/document-templates/` and
   `PATCH /api/v1/document-templates/{document_template_id}/` using the standard envelope and
   bounded pagination.
2. Persist source §16.2 fields: code, name, document type, nullable borrower type, version,
   nullable template-file reference, merge-field JSON, approval status, effective dates, and
   creation timestamp.
3. Treat PATCH as successor-version creation: retain history and prevent an effective template
   already referenced downstream from being silently overwritten.
4. Support the SOP catalogue A-I and L plus Board/Sanction Committee register template metadata;
   keep the conflicting J/K/L annexure label out of routing logic and record it as unresolved.
5. Accept Individual/FPO variants where required. Template-file references must use the existing
   document metadata/storage boundary; this slice does not generate a loan document.

## Database/Model Impact
Add one non-destructive `document_templates` migration following data-model §16.2, with unique
`template_code`, indexed document/borrower type and approval status, effective-date integrity, and
non-overlapping active/effective versions for the same template identity/borrower variant.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Use explicit document-template read/manage permissions. Only source-authorised configuration or
template managers may create successors; read permission never implies mutation or file download.

## Audit Requirements
Write attributable audit and version-history evidence for every real create/successor/status
change, including old/new version, actor, effective dates, and template-file identity. Exact replay
must not duplicate business evidence.

## Validation Rules
- `template_code`, name, document type, version, approval status, and effective-from are required.
- Approval status is bounded to draft/approved/retired; effective-to cannot precede effective-from.
- Borrower type is nullable or a supported Individual/FPO variant; merge fields are a list of
  nonblank unique field names.
- A referenced template file must exist, but its id grants no download authority.
- Do not encode a definitive Annexure J/K/L mapping while the digest's conflict remains open.

## Test Cases
- Create/list/filter/page template variants and retain an earlier version after successor creation.
- Reject duplicate code/version, overlapping effective versions, invalid dates/status/merge fields,
  and inaccessible or missing template-file references with zero writes.
- Prove reader/manager/unauthorised matrices, immutable historical references, audit/version-history
  content, exact replay, and one-winner concurrent successor creation on PostgreSQL.
- Prove the catalogue stores template metadata only and performs no generation/storage download.

## Run-Ahead Sharpening Review (007N completion, 2026-07-14)

- Section 26.3 provides no activate/retire action endpoint. Keep `approval_status` on the exact
  data-model §16.2 vocabulary (`draft`, `approved`, `retired`) and do not create an `/activate/`
  route merely because S72 labels its display state “active”. Record that vocabulary conflict and
  leave lifecycle refinement to a source-backed follow-up; 008B may select only an approved row
  whose effective dates include the generation date.
- `template_code` is source-unique and the §26.3 example includes a version suffix. A PATCH
  successor therefore needs a new unique code/version in its complete payload, retains the target
  row unchanged, and links old/new facts through attributable version-history evidence; do not add
  an uncited mutable “current template” pointer.
- List responses use the standard §6.2 envelope and §8 bounded pagination. Exact supported filters
  must be limited to source/model facts (`document_type`, nullable borrower variant,
  `approval_status`, page, page size); unknown query keys fail validation rather than widening the
  catalogue or returning download descriptors.
- S72's annexure field must stay descriptive metadata independent of `template_code`. A-087 and the
  Epic 008 digest prohibit routing, generation selection, or register authority from depending on
  disputed J/K/L lettering.

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
