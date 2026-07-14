# Slice 008L: Member Portal Documentation Actions

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Goal
Give an authenticated borrower a self-scoped, borrower-safe view of their post-sanction document
requirements and permit only source-defined borrower-side uploads/acknowledgements, without
granting internal verification, checklist completion, security custody, or sensitive reveal.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 008K3

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
- `MP07_DocumentChecklist`
- `MP13_DocumentationActions`

## Frontend Scope
1. Replace both screens' inline arrays with the authenticated portal documentation projection.
   Preserve the current cards, status badges, rows, upload modal, buttons, colours, typography,
   spacing, and responsive layout; add no new visual pattern.
2. Show loading, own-application empty, 401/session-expired, 403, validation, upload progress,
   success, and server-error states with existing portal/alert patterns. Refetch canonical data once
   after upload; never optimistically mark a row verified, signed, accepted, complete, or approved.
3. Permit upload/re-upload only when the server returns that action. Keep Term Sheet/Loan Agreement
   download/view actions limited to borrower-safe current outputs. Blank-dated cheque rows show only
   physical-submission/custody status and never a number, mask fragment, reveal, scan, or download.
4. Remove every inline business fixture from these two files and add a regression that neither file
   imports `mockData` nor retains the source arrays. Do not change DocumentationHub; 008M owns it.

## Backend/API Scope
1. Add self-scoped portal routes:
   - `GET /api/v1/portal/applications/{loan_application_id}/documentation-actions/`
   - `POST /api/v1/portal/applications/{loan_application_id}/documentation-actions/{action_code}/upload/`
     as `multipart/form-data` with exactly one `file` plus bounded nullable `notes`.
2. GET returns application id/reference/status and ordered actions with stable `action_code`, label,
   section, required/applicable flags, borrower-safe status, updated date, instruction/note,
   `upload_allowed`, `reupload_allowed`, and nullable borrower-safe download metadata. Derive every
   action from the 008C/008K checklist, legal-document, mismatch, and masked security ledgers; do not
   copy the prototype's counts/statuses or calculate internal readiness in the client.
3. Bound upload action codes to borrower-owned Stage-4 submissions already named by the SOP and
   prototype: cancelled-cheque copy, signed Term Sheet, signed Loan Agreement, signed PoA,
   signed/conditional tri-party agreement, signed physical SH-4, and conditional bank-verification
   letter or borrower declaration. CDSL remains status/instruction only; blank cheque remains
   physical-submission status only. 008L2 separately owns deficiency response/resubmission.
4. Store uploads through the existing document storage/provenance interface as exact-application
   legal evidence with checksum, size/type/sensitivity, portal account/member attribution, and an
   immutable upload ledger. Return metadata only. Upload never calls internal signature capture,
   mismatch resolution, item completion, checklist approval, custody, reveal, download, or
   disbursement readiness actions.
5. Expose downloads only for source-authorised borrower-safe generated documents through the
   existing secure descriptor/expiry seam and a separately audited portal action. Never expose
   template files, internal audit/version/workflow evidence, security scans, bank/KYC plaintext,
   approver comments, storage keys, or another member's documents.

## Database/Model Impact
Prefer no new aggregate. Reuse `DocumentFile` plus immutable upload provenance and existing
application/legal-document relations. If a relation is required for a portal submission, add one
protected application+action+current-file record with immutable uploader member/portal-account,
checksum/provenance, created time, and append-only successor history; do not overload checklist
completion or signature records and do not add a second document store.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Require an active portal session whose `PortalAccount.member_id` equals the application's member.
Derive scope exclusively from that portal account; ignore/reject caller member ids and make
cross-member/missing application ids nondisclosing. Borrowers may view their own borrower-safe
documents and upload only server-advertised own actions. They cannot hold any internal
`documents.*`, `security.*`, checklist approval/update, file-download, reveal, custody, or
disbursement permission by implication.

## Audit Requirements
Every accepted upload/re-upload and permitted download records portal account, member, application,
action code, document id/category/checksum, prior current document when replaced, request/network,
and outcome without file bytes or sensitive values. Denied cross-member/internal/security actions
write no success evidence. Exact repeated upload metadata must not fabricate verification or
workflow completion; retain every prior file/provenance row.

## Validation Rules
- Documentation actions exist only for the authenticated member's sanctioned application. Draft,
  rejected, wrong-stage, missing-checklist, and stale-cycle applications return an honest
  unavailable/blocked projection and accept no Stage-4 upload.
- Validate one non-empty bounded file using the existing upload MIME/extension/size/checksum rules;
  reject unknown fields/action codes, action/file-type mismatch, stale/non-applicable actions,
  cross-application references, and upload where the server advertises false.
- Applicability is canonical: tri-party only for frozen subsidiary route, SH-4 only for physical,
  CDSL status only for demat, and mismatch resolution only while the retained mismatch requires it.
  Do not invent a client rule or infer applicability from file names.
- Borrower uploads are submissions for internal review, not proof of wet-ink execution, stamp,
  notary, signature match, bank attestation, security custody, or checklist completion. Only the
  existing internal owners can verify/consume them.
- Ordinary portal JSON and HTML must contain no blank-cheque number/ciphertext/hash, BO account,
  bank-account plaintext, storage key, internal audit/version/workflow JSON, or internal action URL.

## Test Cases
- Own approved application GET with physical/demat, subsidiary, and mismatch matrices; ordered
  action labels/statuses and borrower-safe download/upload flags; draft/rejected/blocked/empty states.
- Upload and re-upload each allowed action through portal auth, including exact application
  provenance, checksum/history/audit, canonical refetch, MIME/size/shape validation, and stale or
  inapplicable action rejection.
- Cross-member/missing/inactive/expired portal session matrices; internal user token on portal route;
  portal actor against internal checklist/security/reveal/download routes; all nondisclosing with no
  success evidence.
- Assert uploads do not change checklist completion/verifier/remarks/signatures, PoA/tri-party/
  SH-4/CDSL/cheque terminal truth, bank/cancelled-cheque truth, package status/readiness, loan account,
  or disbursement state. Assert blank cheque/BO/bank/KYC plaintext and storage keys never appear.
- Frontend interaction tests for loading/empty/error/unauthorised/validation/success, exact upload
  request, one canonical refetch, server-owned action visibility, and no mock/inline fixture fallback.

## Visual Acceptance Criteria
At desktop and narrow mobile widths, MP07 and MP13 remain visually identical to their existing
prototype composition except for real labels/data/action visibility. Save authenticated own-data,
blocked/empty, upload validation, upload success, and blank-cheque-restricted screenshots under the
slice's trusted browser contract if that slice declares browser runtime.

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched.

## Risk Level
High

## Run-Ahead Sharpening (008J completion, 2026-07-15)

- The portal projection may consume only 008J's fixed-mask/version-ledger metadata. It must not call
  `documents.modules.sensitive_data_access`, receive `cheque_number_encrypted`/`cheque_number_hash`,
  or expose the cheque scan/document id as borrower download authority.
- The cancelled-cheque upload is only a borrower submission. The applications/member owners retain
  bank matching and verification; a portal upload cannot flip the 008J package flags or replace the
  sanctioned application's retained bank/cancelled-cheque decision.
- Reuse the existing portal session/member-scope module and existing MP07/MP13 markup. Do not grant a
  portal account an internal role/permission or create a second authentication path.

## 008K Completion Sharpening (2026-07-15)

- Portal projections may show the retained checklist status and signer-stage statuses, but must not
  expose internal `checklist_action_id`, comments, signer identity, audit context, or any §27.3-§27.7
  mutation route. Borrower uploads never satisfy or replay an internal completion action.
- Preserve the explicit `not_applicable_until_disbursement` finance state; do not translate the 008K
  `DISBURSEMENT_EVIDENCE_UNAVAILABLE` blocker into a borrower action or a completed/ready label.

## Architecture-Review Sharpening (2026-07-15 04:00)

- Depend on 008K3 so borrower projections never inherit a status-only checklist approval or an
  unbound synthetic cheque ledger. Consume only the corrected current completion/action projection;
  never read raw `VersionHistory` JSON as portal business truth.
- Depend transitively on 008K2's opaque ciphertext and corrected object-scope contract. Portal
  responses and rendered HTML must not contain ciphertext metadata, suffixes, hashes, security ids,
  internal reader roles, or evidence-action identities; the blank-cheque display remains status plus
  physical instruction only.
- Add a regression that a portal upload, re-upload, or crafted payload cannot create/update a
  checklist action, supply a terminal security ledger, or make an internally incomplete item appear
  complete. Canonical refetch must preserve the server's blocked state.

## 008K2 Completion Sharpening (2026-07-15)

- Portal code receives no field-encryption or reveal adapter. CDSL may show only a borrower-safe
  pledge status/instruction (not the internal last-four projection); blank cheque remains physical
  status/instruction only with no number, suffix, ciphertext, lookup hash, scan id, or reveal URL.
- Portal GET/upload scope derives only from the active `PortalAccount.member_id`; K2's internal
  finance reader roles and `security.package.read` permission must never widen portal object scope.
- Add response/DOM plaintext scans covering full BO/cheque fixtures, suffixes, token prefixes,
  lookup hashes, storage keys, and internal evidence identities after load, upload, and refetch.

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
