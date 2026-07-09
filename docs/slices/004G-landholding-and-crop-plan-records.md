# Slice 004G: Landholding and Crop Plan Records

## Status
Not Started

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal
Deliver this narrow capability as a small, testable Ralph implementation slice.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 004F

## Source References
- docs/source/implementation-roadmap.md section 11
- docs/source/api-contracts.md sections 13-18
- docs/source/data-model.md member/KYC/shareholding tables
- docs/source/screen-spec.md member screens

## Prototype Reference
- sfpcl-lms/src/pages/members/*
- sfpcl-lms/src/data/mockData.ts

## Screens Involved
Member Profile — Land & Crop tab.

## Frontend Scope
If the backend land/crop APIs land in this slice, replace the current backend-shell Land & Crop tab
with API-backed list/create behavior using only existing Member Profile card, empty panel, alert,
and form patterns. Do not restore `mockData` land/crop rows or introduce new styling. Do not show
loan-limit amounts unless a source-backed calculation endpoint exists.

## Backend/API Scope
Implement `GET` and `POST /api/v1/members/{member_id}/land-holdings/` from `api-contracts.md`
§17.1 and `GET`/`POST /api/v1/members/{member_id}/crop-plans/` from §17.2. Include
detail/update endpoints only if they stay within one small slice; otherwise split them.

## Database/Model Impact
Add non-destructive model/migration changes for `land_holdings` from `data-model.md` §11.7:
member FK, document type, survey number, village, taluka, district, state, `area_acres`,
`document_id`, verification status, verifier/timestamp fields, and created timestamp. Add
`crop_plans` from §11.8: member FK, nullable `loan_application_id`, crop type, season,
`planned_area_acres`, optional estimated cost amount, loan-purpose alignment, optional document ID,
verification status, verifier/timestamp fields.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Source permission catalogue does not define land/crop-specific permission codes. Follow
`DECISION_POLICY.md`: use the narrowest source-compatible existing member permission only with an
ASSUMPTIONS entry, or split a permission-catalogue slice first if validation rejects that default.
Do not invent new permission codes in this slice.

## Audit Requirements
Audit successful land-holding and crop-plan creates with metadata only. Do not write workflow events
for simple read/list access.

## Validation Rules
Reject negative or zero `area_acres` and `planned_area_acres`; reject malformed document UUIDs.
Require `document_id` for land holdings because `data-model.md` §11.7 marks it non-null and 7/12
extract is required for loan applications. Do not invent land-based loan-limit calculations,
per-acre scale-of-finance rules, application blockers, or purpose-eligibility decisions in 004G.

## Test Cases
TDD: land list/create success, crop-plan list/create success, missing member, missing auth,
read/create permission separation per the recorded assumption, invalid acreage, missing land
document, malformed document UUIDs, audit metadata, and frontend loading/empty/error/validation/
success states when UI is touched.

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
