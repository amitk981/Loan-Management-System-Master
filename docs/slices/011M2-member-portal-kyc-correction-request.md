# Slice 011M2: Member Portal KYC Correction Request

## Status
Not Started

## Parent Epic
Epic 011: Default, Recovery, Closure, and Compliance (KYC compliance continuation)
Epic file: `docs/epics/011-default-recovery-closure-compliance.md`

## Goal
Own the portal KYC update/correction capability the member-portal specification requires but no slice owns (PRODUCTION_COMPLETION_BLUEPRINT.md §6.3): a borrower requests a correction with evidence, staff review it through the KYC/re-KYC machinery, and the member sees request status.

## Owner Decision Gate
If the owner records, before this slice runs, that portal KYC correction is out of MVP release scope (ASSUMPTIONS.md disposition plus HIGH_RISK_APPROVALS note), this slice degrades to: hide/disable every portal KYC-edit affordance, show the "contact the FPO office" guidance from the content spec, and record the deferral in PROTOTYPE_GAP_REPORT.md. Do not build half the flow.

## User Value
Borrowers correct stale KYC facts without an office visit, and re-KYC compliance (011M) consumes real correction requests instead of offline paper.

## Depends On
- 011M

## Source References
- docs/source/screen-spec-member-portal.md KYC view/update screens (spec IDs authoritative)
- docs/source/api-contracts.md portal profile/KYC sections and §26.1 upload
- docs/source/functional-spec.md KYC and re-KYC requirements
- docs/slices/004H-kyc-upload-and-verification.md (staff verification contract)
- docs/slices/006Y-member-create-update-and-identity-governance.md (identity locking/reverification rules)

## Prototype Reference
- sfpcl-lms/src/pages/borrower/portal/* profile/KYC screens

## Concrete Requirements
1. Portal correction-request API: borrower submits the field(s) to correct, reason, and evidence documents (§26.1 upload, portal-scoped); own-data scope from PortalAccount only.
2. Requests never mutate member records directly: they enter a staff review queue governed by the 004H verification and 006Y locking/reverification rules; approval applies the change through the governed path with history; rejection records a borrower-visible reason.
3. Status surface for the borrower: submitted / under review / approved / rejected with dates; no internal reviewer notes leak.
4. Audit and workflow events on submit, review, apply, reject; re-KYC tracker (011M) links to corrections where the source requires.
5. Portal UI: request form, evidence upload, status list/detail, validation, unauthorized, empty, error states; mobile viewport.

## Test Cases
- Own-scope negatives (cross-member submit/read blocked and audited).
- A correction to a KYC-locked field goes through reverification, never direct mutation.
- Approve and reject paths round-trip with history, audit, and borrower-visible status.
- Decision-gate path: with the deferral recorded, no portal KYC-edit affordance renders and the deferral is documented.

## Out of Scope
Staff KYC verification workflow changes (004H), re-KYC scheduling rules (011M), grievances (011N), member create/update contract (006Y).

## Risk Level
High

## Acceptance Criteria
- Either the full request → review → governed-apply loop works end to end, or the capability is explicitly and visibly deferred — no third state.
- All gates pass; portal and staff-review screenshots saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
