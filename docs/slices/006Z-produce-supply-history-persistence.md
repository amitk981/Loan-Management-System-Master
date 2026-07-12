# Slice 006Z: Produce Supply History Persistence and Eligibility Integration

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Persist source-backed produce/service supply history and make the active-member evaluation read it, closing the §6.3 "Produce/service history" gap. 005FB shipped the portal supply view as an empty shell "until the documented produce_supply_records model exists"; active-member rules currently lack persisted evidence.

## User Value
Eligibility decisions rest on recorded supply evidence instead of assumptions; borrowers and staff see the same supply history the calculation uses.

## Depends On
- 006Y2

## Source References
- docs/source/data-model.md produce/supply records table
- docs/source/functional-spec.md active-member and supply-evidence requirements (M04 eligibility inputs)
- docs/source/api-contracts.md supply/produce endpoints and portal produce-supply contract
- docs/slices/006A-active-member-eligibility-service.md (current evaluation seam)
- docs/slices/005FB-member-portal-dashboard-profile-and-supply-view.md (portal shell)
- docs/working/ASSUMPTIONS.md entries deferring supply evidence

## Prototype Reference
- sfpcl-lms/src/pages/borrower/portal/MP22_ProduceSupply.tsx (spec ID caution: see PROTOTYPE_GAP_REPORT MP numbering row — spec IDs are authoritative)
- sfpcl-lms/src/pages/members/Borrower360.tsx (supply panel)

## Concrete Requirements
1. Implement the documented `produce_supply_records` model with source fields, season/year linkage to the member, and a verification status; non-destructive migration.
2. Staff record/verify APIs with the narrowest source-backed permission codes; verification is separated from capture where the source requires maker-checker.
3. The 006A active-member evaluation reads persisted verified records through its existing module seam; remove the shell/assumption input and update the recorded assumption in ASSUMPTIONS.md.
4. Portal produce-supply view (005FB shell) renders the member's own records read-only; own-data scope derived from the PortalAccount, never from query params.
5. Staff Borrower 360 / member profile supply panel renders the same records with empty/error states.
6. Eligibility outputs that change because real evidence replaced the shell must be covered by updated tests, not silently re-baselined; note behaviour changes in the review packet.

## Test Cases
- Record + verify flow with permission and maker-checker negatives.
- Active-member evaluation flips correctly on verified vs unverified vs absent history.
- Portal view is own-scope only; cross-member access blocked.
- Regression: eligibility results derive from persisted rows (no shell constant remains).

## Out of Scope
Crop plan/landholding records (004G delivered), loan-limit formula changes (006C/006D own), bulk import of historical supply data (003L plan owns).

## Risk Level
High

## Acceptance Criteria
- Active-member eligibility is evidence-backed end to end; portal and staff read the same persisted truth.
- All gates pass; API examples and portal/staff screenshots saved.

## Run-Ahead Sharpening Review (006Y, 2026-07-12)

- Capture and verification must use optimistic resource versions and six-field resource actions;
  the record maker must receive a backend denial from verify even if global permissions allow it.
- Change/audit projections must contain member UUID, season/year, verification status, and actor
  IDs only. Portal responses derive member scope from PortalAccount and expose no staff mutation
  action or protected member identity value.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Database rules followed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
