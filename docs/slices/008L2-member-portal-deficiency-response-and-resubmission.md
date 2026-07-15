# Slice 008L2: Member Portal Deficiency Response and Resubmission

## Status
Complete

## Parent Epic
Epic 005: Application Intake and Completeness (portal continuation)
Epic file: `docs/epics/005-application-intake-completeness.md`

Note: filename-scheduled inside Epic 008 next to 008L (portal documentation actions) so the portal document-upload plumbing lands once; the capability is Epic 005 scope debt explicitly deferred by 005G ("Deficiency response/upload/resubmission remains future scope").

## Goal
Let a borrower see raised deficiencies on their own application, upload replacement/additional documents, respond, and resubmit, moving the application out of returned-for-rectification through the real backend lifecycle.

## User Value
Borrowers rectify deficient applications from the portal instead of physically visiting the FPO office; the staff completeness queue receives real resubmissions.

## Depends On
- 008L

## Source References
- docs/source/screen-spec-member-portal.md deficiency/rectification screens (spec IDs authoritative; see PROTOTYPE_GAP_REPORT MP numbering row)
- docs/source/api-contracts.md section 26.1 (document upload), deficiency and portal application sections
- docs/source/functional-spec.md deficiency/rectification requirements
- docs/slices/005F-deficiency-creation-and-resolution.md and 005F2 (staff-side contract)
- docs/slices/005G-member-portal-application-start-status.md (portal application lifecycle and own-data scope)

## Prototype Reference
- sfpcl-lms/src/pages/borrower/portal/applications/MP10_ApplicationStatus.tsx and neighbouring MP screens

## Concrete Requirements
1. Portal deficiency read API: the borrower sees open deficiencies for their own applications only (PortalAccount scope, never query-param authority), with borrower-facing descriptions — no internal staff notes.
2. Document upload against a deficiency through the §26.1 multipart contract with portal scoping: category/sensitivity validated, size/type limits enforced, files linked to the deficiency and application.
3. Respond-and-resubmit action transitions the application from returned-for-rectification to resubmitted per the state machine (002H guards); resubmission without addressing mandatory deficiencies is rejected with a contract error.
4. Staff completeness queue (005E2) reflects the resubmission; deficiency status moves to responded/resolved per the 005F contract.
5. Audit and workflow events for view, upload, respond, and resubmit; portal session rules from 005G2 respected.
6. Portal UI states: list, detail, upload progress, validation failure, unauthorized, empty, error; mobile viewport per portal rules.

## Test Cases
- Own-scope enforcement: cross-member deficiency read/upload/resubmit attempts are blocked and audited.
- Upload validation negatives (type, size, missing category) and happy path linking file → deficiency.
- Resubmission blocked while mandatory deficiencies are unaddressed; allowed after; staff queue reflects it.
- State-machine negative: resubmit from a non-returned status is rejected.

## Out of Scope
Staff deficiency creation/resolution (005F), portal documentation-package actions (008L), portal KYC correction (011M2), notifications content (011NA).

## 008K3 Run-Ahead Sharpening (2026-07-15)

- Reuse 008L's portal upload/provenance boundary, but deficiency files remain intake evidence and
  can never be attached as a Stage-4 current-renderer document, terminal security fact, checklist
  completion action, approval action, or evidence digest merely because the application later
  enters documentation.
- Add a cross-boundary regression that deficiency upload/respond/resubmit writes no
  `checklist_item_completion` or `document_checklist_approval` version, no documentation-checklist
  workflow/audit success, and does not alter any K3 verifier, remarks, role, or checklist status.

## Risk Level
High

## 008L Completion Sharpening (2026-07-15)
- Reuse 008L's central upload/storage helper and immutable portal-account/member/application
  attribution, but create a deficiency-owned relation; never reuse `PortalDocumentationSubmission`.
- Deficiency content downloads must remain authenticated portal reads, not internal download URLs.

## Acceptance Criteria
- The full returned → rectified → resubmitted loop works end to end for a real borrower account.
- All gates pass; mobile portal screenshots of deficiency list, upload, and resubmission saved.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated
- [x] Permissions tested
- [x] Audit events tested
- [x] Visual evidence attempt recorded; localhost binds denied by the sandbox
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates
