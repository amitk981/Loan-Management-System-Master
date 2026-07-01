# Epic 008-documentation-security-package: 008: Documentation, Legal Documents, and Security Package

This parent epic preserves the broad planning context from the earlier Ralph slice. Actual implementation work is broken into smaller child slices under `docs/slices/`.

## Source Broad Slice

# Slice 008: Documentation, Legal Documents, and Security Package

## Status
Not Started

## Goal
Implement document templates/generation, signatures, stamp duty, notarisation, mismatch resolution, checklist approvals, PoA, SH-4, CDSL pledge, cheque tracking, custody, and frontend documentation workspace.

## User Value
Disbursement can only proceed when the full legal/security package is complete, verified, and audited.

## Depends On
- Slice 007

## Source References
- `docs/source/implementation-roadmap.md` section 13
- `docs/source/api-contracts.md` sections 26 through 32
- `docs/source/data-model.md` document/checklist/security tables
- SOP PDFs under `docs/source/`
- `docs/source/screen-spec.md` documentation and security screens

## Screens Involved
- Documentation Workspace
- Template Management
- Document Generation
- Signature Panel
- Bank Verification
- Stamp Duty
- Notarisation
- Document Checklist
- PoA, Tri-party, SH-4, CDSL, Blank Cheque
- Final Documentation Approval
- Member portal documentation actions

## Prototype Reference
- `DocumentationHub.tsx`
- `DocumentChecklist.tsx`
- `DocumentPackModal.tsx`
- `MP07_DocumentChecklist.tsx`
- `MP13_DocumentationActions.tsx`

## Frontend Scope
- Wire documentation workspace/checklist/security panels to APIs.
- Add missing separate states/actions represented only as consolidated prototype cards.
- Add restricted access behavior for blank cheques/security documents.
- Add member portal documentation upload/action status.

## Backend/API Scope
- Template model/versioning, merge field engine, PDF generation service.
- Loan document lifecycle, signature records, stamp duty, notarisation.
- Checklist generation/refresh based on borrower/share mode.
- Checklist approvals by CS, Credit Manager, Sanction Committee, Finance where applicable.
- PoA, SH-4, CDSL pledge, blank/cancelled cheque, custody events.
- Signature mismatch resolution with bank letter/declaration.

## Database/Model Impact
- Document templates, loan documents, signature records, stamp duty records, notarisation records, document checklists/items/approvals, security packages, PoA, SH-4, CDSL, cheques, custody events.

## API Contracts
- Document APIs
- Document Template APIs
- Checklist APIs
- Security Package APIs

## Permissions
- CS/Compliance/Finance/Credit roles according to source docs.
- Restricted security documents require explicit permission and audit.

## Validation Rules
- Documentation starts only after approved sanction.
- PoA and loan agreement require stamp/notary completion where required.
- SH-4 required for physical shares; CDSL pledge required for demat shares.
- Blank-dated cheque and cancelled cheque tracked.
- Signature mismatch blocks checklist until resolved.
- Final approvals follow sequence and meaning in source docs.

## Test Cases
- Required document applicability.
- Template generation and merge fields.
- Stamp/notary/mismatch blockers.
- SH-4 vs CDSL applicability.
- Restricted cheque/security access.
- Checklist approval sequence.
- Audit/custody event tests.

## Visual Acceptance Criteria
- Documentation hub remains workflow-focused and blocker-driven.
- Restricted document UI does not expose sensitive values to unauthorized roles.

## Evidence Required
- API/service tests.
- Generated document sample or metadata evidence.
- Screenshots of checklist blockers, final approvals, and restricted state.

## Risk Level
High

## Acceptance Criteria
- Legal/security package is backend-owned, permissioned, and audited.
- Frontend documentation flows close prototype gaps and reflect real readiness state.
- Disbursement readiness can consume checklist/security outcomes.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates

