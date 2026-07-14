# Slice 008K: Final Documentation Approval Sequence

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Goal
Complete and approve the retained post-sanction document checklist through the source-defined
Company Secretary, Credit Manager, and Sanction Committee sequence, while exposing but honestly
blocking the Senior Manager Finance signature until real disbursement evidence exists.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 008J

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
None. DocumentationHub and the checklist UI remain owned by 008M; do not add mock approvals or
hidden actions.

## Backend/API Scope
1. Add exact §27.3 `POST /api/v1/checklist-items/{checklist_item_id}/complete/`, accepting only
   `loan_document_id` and bounded nullable `remarks`, and §27.4-§27.7 approval/signature routes,
   each accepting exactly bounded non-empty `comments`.
2. Retain immutable attributable checklist action/signature evidence for Company Secretary, Credit
   Manager, Sanction Committee, and Senior Manager Finance meanings. Return durable §6.3 action
   identities; exact replay is zero-write and changed repeat comments conflict.
3. Enforce the strict CS → Credit Manager → Sanction Committee order. Keep the Senior Manager
   Finance route present but zero-write blocked until an exact real disbursement/loan-account owner
   from Epic 009 can prove funds were disbursed; do not manufacture a tracer FK or mark pre-
   disbursement documentation ready.
4. Extend the existing legal checklist owner/lock and consume security/document facts only through
   their established selectors. Do not import security policy into `legal_documents`, recreate
   package rows, or make a second readiness aggregate.

## Database/Model Impact
Replace the 008C2 null-only checklist-signature placeholders with protected, immutable approval-
evidence links/rows owned by `legal_documents`, including signer user, canonical role/authority,
meaning, comments, signed time, request/workflow identity, and unique checklist+stage constraints.
Keep `loan_account_id` null-only until 009C and the Senior Manager signature null until a real
disbursement relation exists. Preserve checklist/item identities and completion-owned verifier,
time, remarks, linkage, and applicability facts.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Require `documents.checklist.update` plus Compliance or Company Secretary document authority for
item completion, `documents.checklist.approve_cs` plus active Company Secretary for CS approval,
`documents.checklist.approve_credit` plus active Credit Manager for the credit approval,
`documents.checklist.approve_sanction` plus an eligible active frozen-case Sanction Committee
signer for final approval, and `documents.checklist.sign_disbursement_complete` plus Senior Manager
Finance for the post-disbursement signature. Every route also requires canonical application/
latest-cycle Stage-4 scope. Other document, security, package, read, or management permissions
imply no checklist mutation or evidence-file access; unrelated ids remain nondisclosing.

## Audit Requirements
Every real item completion and approval writes attributable audit, version, workflow, and durable
action evidence containing checklist/application, item/document, stage meaning, signer immutable
identity, comments/remarks, consumed document/security facts, prior approvals, and request/network/
role/team context. Exact replay, denial, invalid order, and blocked post-disbursement signature write
no success evidence. Projection/approval conflicts roll back all writes.

## Validation Rules
- Item completion applies only to a current required/applicable pending item and an exact same-
  application current-renderer legal document of the item's canonical type. Inapplicable, already
  complete with changed facts, legacy renderer, cross-application, and wrong-type evidence fail
  closed. Preserve applicability and display order.
- Completion must consume the source-owned terminal evidence for the item: PoA active; tri-party
  verified when applicable; SH-4 held when physical; CDSL created/accepted when demat; blank cheque
  held and cancelled cheque canonically verified; required stamp/notary/signatures and resolved
  mismatch for their documents. Never infer completion from file/link existence alone.
- CS approval requires every required/applicable item complete and means “all documents verified
  and attached.” Credit Manager approval requires retained CS approval and canonical frozen limit
  review and means “loan limits reviewed and confirmed.” Sanction Committee approval requires both
  prior approvals and an eligible active committee signer and means “final approval per matrix.”
  Preserve the SOP rule that any one eligible director signs the checklist; do not invent a second
  Stage-3 sanction vote or rewrite the frozen sanction decision.
- Each stage signer must be active and distinct where maker-checker/role conflicts require it;
  later role changes never erase immutable signer identity. Approval is append-only and cannot be
  downgraded, replaced, or reopened through ordinary item completion.
- Senior Manager Finance means “loan disbursed” and therefore cannot succeed before the real Epic
  009 disbursement aggregate proves successful transfer. Checklist/package/security readiness must
  remain honest and no loan account, disbursement, payment, download, invocation, or release is
  created by this slice.

## Test Cases
- Complete/replay/change each applicable item through the public API, including strict shape,
  current-renderer/type/application provenance, terminal PoA/tri-party/SH-4/CDSL/cheque facts,
  stamp/notary/signature blockers, mismatch resolution, and completion history preservation.
- Physical versus demat, subsidiary, mismatch, and cancelled-cheque applicability matrices; missing,
  mixed, malformed, legacy, cross-application, wrong-type, stale, and inapplicable evidence.
- CS/Credit/Sanction ordered success and durable action replay; out-of-order, same-actor/role-change,
  changed-repeat, wrong committee member, inactive actor, read-only, missing-permission, and
  unrelated-object matrices.
- Senior Manager Finance endpoint returns the source-defined blocker with zero writes until real
  disbursement evidence exists. Package/PoA/SH-4/CDSL/cheque/share/file/loan/readiness facts remain
  unchanged throughout checklist approval.
- Five concurrent item completions and each approval stage retain one current item/approval and
  complete attributable winner/zero-success-loser evidence on PostgreSQL, run twice.

## Visual Acceptance Criteria
None.

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched.

## Run-Ahead Sharpening (008I completion, 2026-07-14)

- Reuse 008C2's canonical checklist read/scope and immutable applicability/linkage split. Consume
  008F2/008G2/008H/008I/008J through owner selectors or masked ledgers only; never query security
  tables from the checklist owner or make evidence existence equal completion.
- Bind approval meanings exactly to V10 §4.13/Deck p.8: CS verifies attachment/completeness, Credit
  Manager confirms limits, one eligible Sanction Committee director gives final documentation
  approval, and Senior Manager Finance signs only after actual disbursement.
- Epic 009 absence is an expected explicit blocker for §27.7, not permission to create a synthetic
  loan/disbursement fact. Preserve the null-only loan-account constraint and record the handoff to
  the first real disbursement owner.

## Architecture-Review Sharpening (2026-07-14 23:49)

- Consume PoA/SH-4/CDSL/cheque terminal facts only through the 008I3 corrected owner interfaces;
  `legal_documents` may depend on security metadata, while `security_instruments` must not be
  imported back into a legal callback that recreates either owner's policy.
- Checklist readers include the source §14.1/§19 Credit, finance-approver, and Auditor roles under
  canonical object scope. Read authority remains distinct from item completion and each ordered
  approval action.
- Race assertions must identify the sole material winner and prove every losing request produced no
  audit/version/workflow success evidence; do not count exact replay as a changed-payload winner.

## 008I4 Completion Sharpening (2026-07-15)

- Consume CDSL/cheque terminal readiness through masked owner facts issued by the top-level process;
  checklist completion must never call the sensitive reveal interface, receive ciphertext/hash,
  or make object existence/decryption equal terminal security truth.
- A pending CDSL row with null evidence remains valid metadata but cannot complete the checklist.
  Require the exact accepted/created terminal snapshot and its frozen current-renderer evidence;
  preserve null linkage until that terminal evidence exists.
- Checklist audit/version/workflow snapshots must remain recursively plaintext-free. Add a
  regression that the fake BO/cheque fixtures appear in neither checklist projections nor any
  success/denial evidence while preserving the central sensitive ledger as a separate owner.

## 008J Completion Sharpening (2026-07-15)

- Consume blank-cheque readiness only from the latest masked `blank_dated_cheque` version ledger:
  require `held`, one retained Compliance preparer, a distinct Company Secretary custodian, a
  custody workflow id, exact application/package/member/bank/cancelled-cheque ids, and the current
  application-owned verified bank/cancelled-cheque decision. Never receive the encrypted number,
  lookup hash, reveal callback, scan download, invocation, presentation, or return authority.
- The 008J checklist projection intentionally preserves the blank-cheque item's completion,
  verifier, remarks, and nullable loan-document link. §27.3 still accepts the source-defined
  `loan_document_id`; do not silently replace an existing link with the cheque scan's
  `DocumentFile` id or treat masked metadata as a legal `LoanDocument`.
- Approval/race evidence must preserve 008J's fixed `******` mask and canonical cancelled-cheque
  metadata, while leaving package status/readiness, bank truth, scan access, and the central
  sensitive reveal/denial ledger unchanged.

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
