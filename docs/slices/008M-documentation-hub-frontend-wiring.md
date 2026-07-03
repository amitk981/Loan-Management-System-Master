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
- 008L

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

## Test Cases
- Checklist blockers render from seeded mismatch/stamp-pending fixtures and clear when backend state resolves.
- Unauthorized role cannot see restricted document contents or actions (frontend + 403 backend assertion).
- Approval sequence buttons appear only for the role whose turn it is per the source sequence.

## Out of Scope
Member portal documentation actions (008L done), disbursement readiness consumption (009D), template admin CRUD beyond what 008A/008B expose.

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
