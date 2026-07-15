# Slice 008M: Documentation Hub Frontend Wiring

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Goal
Wire the staff documentation surface to the backend built in 008A-008K: Documentation Workspace (S26), Document Checklist (S27), and the workflow panels for PoA (S28), Tri-Party (S29), SH-4 (S30), CDSL pledge (S31), Term Sheet (S32), Loan Agreement (S33), Bank Verification / Signature Mismatch (S34), and Final Documentation Approval (S35), plus stamp duty/notarisation status display.

## User Value
Compliance and CS staff work the real legal/security package — blockers, checklist state, and approval sequence come from the backend, so disbursement readiness reflects the truth.

## Depends On
- 008L3

## Source References
- docs/source/screen-spec.md screens S26-S35 and section 9.5 (documentation rules)
- docs/source/api-contracts.md sections 26 (documents), 27 (checklists), 28 (security package)
- docs/source/Final SOP - Loan Disbursement V10 (1).pdf and SFPCL_Loan Sanction- Doc & Disbursement-SOP_WhatsLoan-25052026.pdf (documentation sequence)
- docs/source/user-flows.md (documentation flows)

## Prototype Reference
- sfpcl-lms/src/pages/documentation/DocumentationHub.tsx
- sfpcl-lms/src/components/loan/DocumentChecklist.tsx
- sfpcl-lms/src/components/loan/DocumentPackModal.tsx

## Concrete Requirements
1. Wire `DocumentationHub.tsx` and `DocumentChecklist` to the checklist/document APIs: per-loan checklist items, applicability (008C), verification state, and blocker display (signature mismatch, stamp/notary pending, SH-4/CDSL pending).
2. Each security workflow (PoA, tri-party, SH-4, CDSL, blank/cancelled cheque custody) gets its status and actions surfaced in the hub using existing card/panel patterns — the prototype's consolidated cards may need splitting into per-workflow states; compose only from existing components per FRONTEND_DESIGN_RULES.
3. Final documentation approval sequence (008K) rendered with role-correct action buttons; approvals immutable once given.
4. Restricted documents (blank cheques, security instruments) show restricted state for unauthorized roles; downloads go through the audited signed-download flow from 003D.
5. Generation actions (008B) wired: generate from template, show version, download evidence.
6. Loading, empty, error, unauthorized, and blocked states throughout.

## Owned Mock Removals
This slice is the final owner of these files' mock surface — after it, none of them may import `src/data/mockData.ts` or keep inline business fixtures:
- `src/pages/documentation/DocumentationHub.tsx`
- `src/components/loan/DocumentChecklist.tsx`
- `src/components/loan/DocumentPackModal.tsx`
- `src/components/loan/AuditTimeline.tsx` (ApplicationDetail usage was wired by 005I; this slice removes the remaining mock reads and the import itself)

## Test Cases
- Checklist blockers render from seeded mismatch/stamp-pending fixtures and clear when backend state resolves.
- Unauthorized role cannot see restricted document contents or actions (frontend + 403 backend assertion).
- Approval sequence buttons appear only for the role whose turn it is per the source sequence.
- Exact success stores the returned `checklist_action_id` only as canonical response state and
  refetches once; changed replay, out-of-order, incomplete-evidence, and disbursement-unavailable
  conflicts remain visible without optimistic status changes or retries.

## Architecture-Review Sharpening (2026-07-15 04:00)

- Render completion/approval state only from 008K3's action-backed canonical projection. Never infer
  success from a complete status, a linked file, local role, prototype count, or raw audit/version
  data; missing/stale terminal action identity renders the existing blocked pattern.
- Use 008K2's server-owned role/object projection for restricted states. Senior Manager Finance and
  CFC controls remain absent until documentation-approved/disbursement-ready scope respectively;
  the client must not widen access from a permission string or Stage-4 status.
- Add interaction assertions that synthetic/missing cheque truth and incomplete item-action evidence
  surface the canonical blocker without exposing cheque/BO suffixes, storage ids, signer evidence,
  or optimistic approval UI.

## Out of Scope
Member portal documentation actions (008L done), disbursement readiness consumption (009D), template admin CRUD beyond what 008A/008B expose.

## 008L Completion Sharpening (2026-07-15)
- Keep staff checklist reconciliation in `legal_documents.modules.checklist_actions`; do not consume
  portal submission rows as verification/completion truth or expose portal content URLs internally.

## 008L2 Completion Sharpening (2026-07-15)

- Treat `ApplicationDeficiencyResponse` and its linked pending `ApplicationDocument` version only as
  intake/completeness-review evidence. The documentation hub must not translate a portal deficiency
  response, its resolved deficiency row, or the application's canonical resubmission event into a
  Stage-4 checklist completion, approval, signature, custody, or documentation-ready state.
- If the hub displays the application timeline, label the portal event as an application
  resubmission for completeness review; do not present it as documentation-checklist success.

## Architecture Review Sharpening (2026-07-15 09:00)

- Consume 008K4's public staff projection only. Never render raw PoA/SH-4/CDSL/cheque terminal
  evidence, request/IP/user-agent context, role/team lists, internal signer snapshots, ciphertext,
  hashes, storage keys, or evidence action ids from ordinary security GET responses.
- Completion and approval controls must consume the current renderer/evidence projection that is
  locked against concurrent generation. A retained action/status whose current document, bank
  decision, audit, workflow, version, or terminal evidence no longer reconciles renders the existing
  blocked state and cannot be retried optimistically.
- Reuse 008L3's central signed-download client and safe object-URL lifecycle for staff-authorised
  published files. Portal submission rows, unsigned `expires_at` values, or internal file metadata
  never create a staff download action.

## Risk Level
Medium

## Acceptance Criteria
- S26-S35 surfaces run on backend data with blocker-driven workflow intact.
- No mock-data reads remain in the documentation screens.
- All gates pass; screenshots of checklist blockers, a security workflow panel, restricted state, and final approval saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
