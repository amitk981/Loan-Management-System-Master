# Slice 006: Eligibility, Loan Limit, Appraisal, and Credit Review

## Status
Not Started

## Goal
Implement eligibility assessment, active member checks, default check, loan limit calculation with rule snapshots, appraisal note, Credit Manager review, and submit-to-sanction flow.

## User Value
Credit decisions become explainable, testable, and tied to the source business rules instead of frontend mock calculations.

## Depends On
- Slice 005

## Source References
- `docs/source/implementation-roadmap.md` sections 11, 20.1, 20.2, 21.3, 22.1
- `docs/source/api-contracts.md` sections 22, 23, 24
- `docs/source/data-model.md` eligibility, loan limit, appraisal, risk assessment
- `docs/source/functional-spec.md`
- `docs/source/test-plan.md`

## Screens Involved
- Appraisal Workbench
- Eligibility Assessment
- Loan Limit Calculator
- Appraisal Note
- Credit Manager Review
- Application detail stage summary

## Prototype Reference
- `AppraisalWorkbench.tsx`
- `EligibilityChecklist.tsx`
- `LoanLimitCalculator.tsx`
- `ApplicationDetail.tsx`

## Frontend Scope
- Replace mock eligibility and calculator values with API-backed results.
- Show rule version, rule snapshot, pass/fail explanations, boundary warnings, and review status.
- Add loading/error/blocked states for incomplete applications.
- Preserve calculator and workbench visual structure.

## Backend/API Scope
- Active member service.
- Eligibility assessment run/get/override APIs.
- Loan limit calculate API and formula contract.
- Appraisal note create/get/submit APIs.
- Credit Manager review and submit-to-sanction API.
- Audit events for assessment, override, appraisal, review, and submission.

## Database/Model Impact
- Eligibility assessments, active member statuses, loan limit assessments, appraisal notes, risk assessments, borrowing histories where required.

## API Contracts
- Eligibility Assessment APIs
- Loan Limit APIs
- Loan Appraisal APIs

## Permissions
- Deputy Manager Finance and Credit Manager permissions; overrides require explicit permission and audit.

## Validation Rules
- Completeness must pass before appraisal.
- Active member/default/document/purpose/terms checks must be explainable.
- Loan limit stores full snapshot and rule version.
- Credit Manager review is required before sanction submission.

## Test Cases
- Eligibility pass/fail paths.
- Active member four-year/relaxation logic.
- Loan limit boundary tests.
- Override permission/audit tests.
- Appraisal submit and Credit Manager review.

## Visual Acceptance Criteria
- Calculator explanations and blockers are readable and match prototype density.
- Risk and review states are visible without extra instructional text.

## Evidence Required
- Unit/service tests for financial and eligibility rules.
- API tests.
- Screenshots of pass/fail eligibility and calculator result.

## Risk Level
High

## Acceptance Criteria
- Eligibility and loan limit are backend-owned and tested.
- Appraisal cannot skip required gates.
- Frontend reflects backend decision state and explanations.

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
