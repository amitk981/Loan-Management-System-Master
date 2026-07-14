# Slice 008F: Power of Attorney Workflow

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Goal
Create and maintain the one source-defined Power of Attorney for a sanctioned application's
security package, binding borrower/nominee/Company Secretary authority to current generated,
adequately stamped, completed-notarisation evidence without invoking or releasing the instrument.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 008E2

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
None. DocumentationHub/security-package wiring remains owned by 008M; do not add mock or hidden UI
actions.

## Backend/API Scope
1. Add §28.1-§28.2 security-package GET/refresh only as the narrow owner/parent needed by PoA, with
   `poa_required_flag=true`; do not implement SH-4, CDSL, cheque, custody, or readiness outcomes.
2. Add §28.3 `POST/GET /api/v1/security-packages/{security_package_id}/power-of-attorney/` and
   `PATCH /api/v1/power-of-attorneys/{power_of_attorney_id}/` using exactly borrower member,
   nominee, attorney user, purpose, loan-document, stamp-record, notary-record, execution,
   effective-from, and status facts.
3. Keep one current PoA per package under a locked package row. Exact POST/PATCH replay is zero-write;
   real changes retain immutable prior facts. PATCH must not invoke or release the instrument.
4. Project PoA existence/execution metadata into the linked checklist/security reads without marking
   the PoA checklist item complete or making the security package/disbursement ready.

## Database/Model Impact
Add §17.1 `security_packages` with one protected application link and nullable-only loan-account
transition until 009C. Add §17.2 `power_of_attorneys` with one-to-one protected package, borrower,
nominee, attorney, current-renderer loan-document, 008D stamp/notary links, bounded indexed
execution/status fields, date integrity, and protected release facts. Do not populate invocation or
release state in this slice.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Require `security.package.read` for GET, `security.package.create` for first refresh, and
`security.poa.manage` for PoA mutation, plus canonical application/document scope. Compliance Team
may prepare a draft; Company Secretary verifies/activates and must be the retained attorney.
Credit/read/document-download permissions imply no mutation or evidence download. Unrelated scope
is nondisclosing.

## Audit Requirements
Every real package/PoA create or change writes attributable old/new audit, workflow, and version
evidence with application/package/borrower/nominee/attorney/document/stamp/notary ids and request
metadata. Exact replay and every denial write no success evidence. Checklist/security projections
roll back atomically with a failed mutation.

## Validation Rules
- PoA is always required; borrower and nominee must be the application's retained current parties,
  and attorney must be an active Company Secretary user. Do not infer identity from display names.
- Purpose must explicitly authorise the Company Secretary to initiate share sale on default; use
  retained text, not generated legal wording or a client-side constant.
- `active`/executed PoA requires the current 008B4 `power_of_attorney` loan document, its exact 008D
  `adequate` stamp record, its exact `completed` notarisation record, and effective-from. All three
  evidence owners must belong to the same loan document/application.
- Draft preparation may retain incomplete execution facts but cannot project execution/verification.
  PoA stamping/notarisation do not prove borrower and nominee signatures; 008E signature facts must
  exist before activation.
- Status is only draft/active in this slice. `invoked` requires later Sanction Committee/Board
  approval and `released` belongs to closure; reject both without writes.
- Never hard-code the unresolved stamp-rate amount, invoke share sale, expose evidence downloads,
  complete the checklist, or claim security/disbursement readiness.

## Test Cases
- Package create/read exact replay and one-PoA uniqueness.
- Draft preparation versus Company Secretary activation with borrower/nominee/attorney/signature,
  current renderer, adequate stamp, completed notary, effective-date, and same-application checks.
- POST/PATCH exact replay, retained change history, stale/wrong-id/cross-package/cross-application
  evidence, and forbidden invoked/released transitions.
- Compliance prepare, Company Secretary activate, read-only/unauthorised/unrelated role matrices.
- Checklist/security projections preserve completion, verifier, remarks, signatures, package status,
  file access, and disbursement readiness; projection conflict rolls back all writes.
- Concurrent create/change attempts retain one current PoA and complete attributable history on
  PostgreSQL.

## Run-Ahead Sharpening (008D completion, 2026-07-14)

- Consume 008D records only through protected same-loan-document relations and current status;
  do not recompute stamp adequacy, notarisation evidence provenance, or renderer provenance in PoA.
- Activation must require both borrower and nominee execution facts from 008E. Stamp/notary success
  alone cannot stand in for signatures or complete the checklist item.
- Preserve 008D's exact replay/current-row/history semantics. PoA changes must never rewrite stamp,
  notary, generated-file, template, renderer, or checklist completion evidence.

## Run-Ahead Sharpening (008E completion, 2026-07-14)

- Resolve borrower and nominee execution only from distinct current `signed` 008E rows on the exact
  PoA loan document. Match party ids to the frozen application parties and preserve each signer-name
  snapshot; a resolved signature mismatch is not itself proof that either party executed the PoA.
- Consume signature facts through a legal-documents-owned selector under the already locked package/
  loan-document transaction. Do not mutate signature rows, replay their evidence, or treat a
  metadata id as file/download authority.
- If either required signature is pending, mismatched, absent, duplicated/conflicting, or belongs to
  another current-renderer document/application, keep activation blocked with zero package/PoA/
  checklist success evidence. Checklist approval and completion remain owned by 008K.

## Architecture-Review Sharpening (2026-07-14 16:10)

- Depend on 008E2, not raw 008E rows. Consume its canonical signature selector and frozen
  application-party identity; do not query `SignatureRecord` directly or accept caller-supplied
  UUID/name pairs as borrower/nominee execution truth.
- An 008E unresolved mismatch that was later overwritten by capture is not valid historical
  execution evidence. Activation must use only the post-008E2 current lifecycle and must preserve
  maker/checker identities across Compliance preparation and Company Secretary activation.
- Add an end-to-end regression using a genuinely generated current-renderer PoA plus its real 008D2
  maker/checker stamp/notary and 008E2 borrower/nominee signatures. Metadata-only fixtures may still
  isolate unit rules but cannot be the sole tracer for activation.

## Run-Ahead Sharpening (008D2 completion, 2026-07-14)

- PoA activation may consume only stamp/notary rows with non-null, distinct retained
  `prepared_by_user_id` and `verified_by_user_id`, plus `adequate`/`completed` current outcomes on
  the exact PoA loan document. A-108 legacy rows with missing maker attribution are history, not new
  activation evidence.
- Resolve 008D2 evidence through a legal-documents-owned selector; do not query foundation upload
  ledgers, recompute category/application policy, or infer verification from `LoanDocument` status
  projections alone.
- Preserve Company Secretary checker identity separately from the PoA attorney identity even when
  the same canonical Company Secretary user legitimately fills both roles; Compliance preparation
  must still be a different user and every downstream audit must retain all identities.

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
