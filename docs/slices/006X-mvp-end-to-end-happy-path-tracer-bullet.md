# Slice 006X: MVP End-to-End Happy Path Tracer Bullet

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Prove one real Epic 006 path from an already-complete application through eligibility, loan-limit
calculation, appraisal preparation/review, and one pending sanction case, using the real backend and
006H UI without bypassing any action boundary.

## User Value
Provides a reviewable cross-role proof that the credit-assessment feature works as one system before
Epic 007 adds committee decisions.

## Depends On
- 006H

## Source References
- docs/source/implementation-roadmap.md section 11
- docs/source/api-contracts.md sections 22-24
- docs/source/data-model.md eligibility/appraisal tables
- docs/source/functional-spec.md
- docs/source/test-plan.md

## Prototype Reference
- sfpcl-lms/src/pages/appraisal/AppraisalWorkbench.tsx
- sfpcl-lms/src/components/loan/EligibilityChecklist.tsx
- sfpcl-lms/src/components/loan/LoanLimitCalculator.tsx

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
Use only existing APIs to seed or create one complete reference-generated application, run eligible
assessment, calculate an in-limit loan limit, create and submit an appraisal, record an independent
Credit Manager `reviewed` decision, and submit once to the pending sanction case. Add no duplicate
workflow service and no sanction decision, documentation, account, disbursement, repayment, or
closure behavior owned by later epics.

## Database/Model Impact
Use only already-created MVP tables; add no broad new schema unless required by the tracer.

## API Contracts
Use existing APIs from prior slices and add only narrow missing glue contracts.

## Permissions
Use distinct Deputy Manager Finance and Credit Manager sessions. Assert the preparer cannot review,
review permission cannot submit sanction, and sanction permission cannot bypass reviewed state.

## Audit Requirements
Assert the existing eligibility, loan-limit, appraisal submit/review, and sanction-submission
metadata evidence forms one ID-linked chain and contains no appraisal/review/request free text.

## Validation Rules
Use an amount within the frozen limit (`exception_required_flag = false`) and exact source request
fields. Finish at one `pending` approval case and `submitted_to_sanction_committee`; committee
approval is explicitly not part of this tracer.

## Test Cases
- One backend integration test chaining the public module/API boundaries with the same application,
  assessment, appraisal, review-decision, and approval-case UUIDs.
- One Playwright path through the 006H workbench using the two real roles and no `mockData` credit
  facts; capture the reviewed and pending-sanction states.
- One repeat-submit regression proving the case/audit/workflow counts remain one.

## Visual Acceptance Criteria
None.

## Evidence Required
End-to-end log, API responses, and screenshots across the happy path.

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
