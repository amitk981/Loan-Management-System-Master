# Slice 006A: Active Member Eligibility Service

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Implement the backend eligibility-assessment foundation and the active-member check for completed
loan applications.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 005I

## Source References
- docs/source/implementation-roadmap.md section 11
- docs/source/api-contracts.md sections 22-24
- docs/source/data-model.md eligibility/appraisal tables
- docs/source/functional-spec.md
- docs/source/test-plan.md
- docs/working/digests/epic-006-eligibility-loan-limit-appraisal.md

## Prototype Reference
- sfpcl-lms/src/pages/appraisal/AppraisalWorkbench.tsx
- sfpcl-lms/src/components/loan/EligibilityChecklist.tsx
- sfpcl-lms/src/components/loan/LoanLimitCalculator.tsx

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
- Add `eligibility_assessments` persistence if it does not already exist, matching
  `data-model.md` §14.1 for the fields needed by §22.1.
- Implement `POST /api/v1/loan-applications/{loan_application_id}/eligibility-assessment/run/`
  and `GET /api/v1/loan-applications/{loan_application_id}/eligibility-assessment/`.
- In this slice, compute only `member_active_check`; populate the other checks as explicit
  `pending`/not-yet-evaluated values that 006B will own.
- Only allow the run for applications with a formal `LO...` reference, `application_status =
  reference_generated`, `completeness_status = complete`, and `current_stage = credit_assessment`.
- Reuse the existing loan-application object-access boundary from 005C2 before returning or
  mutating assessment facts.

## Database/Model Impact
Non-destructive model/migration changes for this capability, if needed.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Run requires `credit.eligibility.run`. Read requires the same application read/object access used
by application detail unless a narrower source-backed read permission already exists in the code.
Do not implement override; `credit.eligibility.override` belongs to a later exception slice.

## Audit Requirements
Successful run writes metadata-only audit/workflow evidence for `eligibility.assessed` (or the
closest existing source-backed action name). Denied, invalid-state, and validation failures must
not write success audit/workflow events.

## Validation Rules
- Active-member source rules are BR-004 through BR-007.
- Use existing member/profile/produce/service facts where available.
- If source-required historical produce/service evidence is not yet modelled, return a
  source-explicit manual-evidence/relaxation result rather than inventing a calculation.
- Missing application returns `404`; missing global permission returns `403 PERMISSION_DENIED`;
  same-permission out-of-scope access returns `403 OBJECT_ACCESS_DENIED`; wrong application state
  returns `409 INVALID_STATE_TRANSITION`.

## Test Cases
- TDD red/green for missing run endpoint, then green active-member assessment response.
- Eligible/reference-generated application can run and read an assessment.
- Draft/submitted/incomplete-returned applications cannot run eligibility and create no assessment.
- Missing permission and object-scope denial paths create no assessment/audit/workflow evidence.
- Missing source history produces the chosen manual-evidence/relaxation result and records an
  assumption if the source data is not implemented yet.

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
