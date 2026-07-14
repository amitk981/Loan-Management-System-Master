# Slice 008H: SH-4 Physical Share Security Workflow

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Goal
Create and maintain the one source-defined SH-4 instrument for a physical-share security package,
binding the sanctioned borrower, validated shareholder witness, active physical shareholding,
current generated form, signatures, stamp verification, and custody metadata without invoking or
returning the instrument.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 008F2

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
1. Add §28.4 `POST/GET /api/v1/security-packages/{security_package_id}/sh4-share-transfer-form/`
   and `PATCH /api/v1/sh4-share-transfer-forms/{sh4_share_transfer_form_id}/`, accepting exactly
   member, witness, shareholding, nullable share count, loan document, form status, custody location,
   and signed date.
2. Refresh only the existing 008F package's physical-share requirement from 008C2's frozen share
   mode. `physical` requires SH-4; `demat` does not; missing or `mixed` remains the existing explicit
   applicability blocker and must not be guessed into an SH-4 record.
3. Keep one current SH-4 per package under the locked package row. Exact POST/PATCH replay is
   zero-write; real changes retain immutable old/new evidence. PATCH must not invoke or return the
   form.
4. Project SH-4 existence/signature/custody metadata into linked checklist/security reads without
   completing the checklist item or changing package/disbursement readiness.

## Database/Model Impact
Add §17.3 `sh4_share_transfer_forms` with one protected package, borrower member, validated witness,
active physical shareholding, current-renderer SH-4 loan document, bounded indexed form status,
nullable positive share count/signed date, required custody text when held, and protected nullable
invocation/return facts constrained to null until their later owners. Preserve 008F's nullable-only
loan-account transition and one-package-per-application integrity.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Require `security.package.read` for GET and `security.sh4.manage` for mutation plus canonical
sanctioned application/package/document scope. Compliance Team may prepare pending/signed facts;
Company Secretary records custody and must remain the retained custodian identity. Document read,
download, signature capture, PoA, or package-create permissions imply no SH-4 mutation or file
access. Unrelated scope is nondisclosing.

## Audit Requirements
Every real create/change writes attributable audit, workflow, and version evidence containing
application/package/member/witness/shareholding/document/stamp/signature/custodian ids plus request,
network, role, and team metadata. Exact replay and every denial write no success evidence. Checklist
and package projections roll back atomically with a failed mutation.

## Validation Rules
- SH-4 is applicable only to the frozen `physical` share mode. Member must be the application's
  retained borrower; witness must be that application's current verified existing-shareholder
  witness; shareholding must be active, physical, and owned by the borrower. Do not infer identity
  from names or folio text.
- Signed/custody status requires a current 008B4 `sh4` loan document plus distinct current 008E2
  signed borrower and witness rows on that exact document, canonical frozen ids/names, signed time,
  non-null capture makers, no mismatch, and the document's current 008D2 adequate maker/checker
  stamp record. Do not hard-code nominal stamp amount.
- Nullable share count, when supplied, must be a positive integer no greater than the retained active
  physical shareholding's available shares; the slice does not reserve, transfer, or decrement shares.
- Held-in-custody requires non-empty bounded custody location and Company Secretary authority.
  `invoked` requires later Sanction Committee/Board approval and `returned` belongs to closure;
  reject both with zero writes and keep invocation/return facts null.
- SH-4 execution/custody never proves checklist completion, document approval, security invocation,
  package completion, or disbursement readiness.

## Test Cases
- Physical-package create/read, exact replay, one-SH-4 uniqueness, retained changed history, and
  strict fields/status/date/share-count constraints.
- Borrower/witness/shareholding/current-renderer/signature/stamp same-application matrices,
  including A-108/A-109 null-maker legacy exclusion, wrong share mode, inactive/nonphysical
  shareholding, wrong witness, and cross-document evidence.
- Compliance preparation, Company Secretary custody, read-only/unauthorised/unrelated role matrices,
  and forbidden invoked/returned transitions.
- Checklist/security projections preserve PoA, completion, verifier, remarks, approval signatures,
  package status, file access, and readiness; projection conflict rolls back every write.
- Five concurrent create/change attempts retain one current SH-4 and complete attributable history
  on PostgreSQL.

## Run-Ahead Sharpening (008F completion, 2026-07-14)

- Extend the 008F security-package serializer and lock owner; do not create a second package module
  or let SH-4 refresh rewrite PoA, cheque, CDSL, status, loan-account, or readiness facts.
- Follow 008F's exact replay/history/nondisclosure order and use legal-owned selectors for exact
  document stamp/signature truth. Never query `SignatureRecord` directly or accept caller-supplied
  party snapshots as execution authority.
- A-110's physical flag is a deferred placeholder in 008F. 008H may set it only from 008C2's frozen
  source; missing/mixed mode remains visibly blocked rather than false-ready.

## Architecture-Review Sharpening (2026-07-14 19:20)

- Depend on 008F2 and add SH-4 only inside its `security_instruments` deep boundary. Do not append
  another security model/workflow to `legal_documents`; legal selectors may supply immutable
  document/stamp/signature facts without owning package or custody policy.
- Consume only canonical final-sanction package scope and 008G2 current-maker evidence. A maker who
  materially changes a signature or stamp cannot then record custody through another active role,
  and evidence consumed by a held SH-4 cannot be silently rewritten.
- The declared PostgreSQL gate must race both create and changed custody submissions twice, retain
  one current SH-4, and assert every winner/loser audit/version/workflow identity rather than merely
  counting the row.

## 008G2 Completion Sharpening (2026-07-14)

- The legal evidence selector must exclude `legacy_maker_attribution=true` rows and expose the
  current material stamp/signature maker used by SH-4 custody maker-checker checks. Exact replay may
  reuse retained facts but must never transfer maker identity.
- Once held-custody evidence consumes an exact signature or adequate stamp row, the SH-4 owner must
  provide the same upstream mutation protection now used by verified tri-party execution; a failed
  rewrite preserves custody, checklist/package projections, and every ledger atomically.
- Use the lower request-contract module behind thin HTTP serializers and return retained §6.3
  workflow identity for custody actions; do not import transport serializers into security modules.

## Visual Acceptance Criteria
None.

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched.

## Risk Level
High

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
