# Slice 006G: Submit to Sanction

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Implement source §24.5 submission of a Credit-Manager-reviewed appraisal to the Sanction
Committee, creating the source-backed approval case once without implementing committee decisions.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 006F

## Prior Slice Handoff
- 006E persists one appraisal/risk package, prerequisite assessment UUID snapshots, recommendation,
  and immutable TAT facts through `credit.modules.appraisal_workflow.AppraisalWorkflow`.
- 006F owns `review_pending -> reviewed` and maker-checker review facts. 006G must consume the
  reviewed appraisal interface/state without importing concrete eligibility/loan-limit models or
  recalculating stored facts.
- Approval-matrix configuration and committee decision actions remain owned by Epic 007; 006G
  creates only the pending sanction submission/case shell required to hand off the reviewed pack.

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
- Implement `POST /api/v1/loan-applications/{loan_application_id}/submit-to-sanction-committee/`
  through `AppraisalWorkflow.submit_to_sanction(...)`; request accepts only required non-blank
  `remarks` from source §24.5.
- Require one stored appraisal with `appraisal_status = reviewed`, nullable review fields now
  populated, and a complete linked risk assessment. Do not rerun eligibility/loan limit or rewrite
  recommendation/TAT/review facts.
- Atomically create one pending approval-case/sanction-submission record linked to the application
  and appraisal, transition the appraisal/application to the source sanction-review state, and
  return the case/application/appraisal IDs and status. A repeated call must not create a second
  case.
- Keep approval-matrix evaluation, approver assignment/decisions, exception approval, meeting
  scheduling, rejection-note generation, documents, and frontend wiring out of scope.

## Database/Model Impact
Add the smallest non-destructive approval-case/sanction-submission persistence required by source
§24.5 and the codebase-design `ApprovalCase` return seam, with unique application/appraisal linkage
and pending status. Do not add committee action or sanction-decision tables owned by Epic 007.

## API Contracts
Use the standard envelope. Request is exactly `{ "remarks": "..." }`; response includes
`approval_case_id`, `loan_application_id`, `loan_appraisal_note_id`, submission status, submitting
user summary, and submitted timestamp. Unknown/blank fields return `400 VALIDATION_ERROR`.

## Permissions
Require `credit.appraisal.submit_sanction` and the existing Credit Manager credit-domain
object-access boundary. Create/update/submit-review/review permissions do not imply sanction
submission. Missing permission is `403 PERMISSION_DENIED`; out-of-scope is
`403 OBJECT_ACCESS_DENIED`.

## Audit Requirements
Successful submission writes metadata-only appraisal/sanction audit and workflow evidence with
IDs, state change, actor/time, and request ID. Never copy appraisal summaries, risk notes, review
comments, or request remarks into audit JSON. Denied/invalid/repeated paths write none.

## Validation Rules
- Only a `reviewed` appraisal can submit; missing, draft, review-pending, returned, or already
  submitted states return `409 INVALID_STATE_TRANSITION`.
- Credit Manager review facts are mandatory and the actor requires the separate sanction-submit
  permission. If the stored loan-limit snapshot requires an exception, flag the pending sanction
  package for later exception routing; do not create or approve the exception in 006G.
- Submission is atomic and idempotent by state/unique linkage: failures preserve appraisal,
  application, approval-case, audit, and workflow counts.

## Test Cases
- TDD red/green reviewed-appraisal submission creates one pending case and source response.
- Draft/review-pending/returned/missing/repeated submission paths are blocked without side effects.
- `credit.appraisal.submit_sanction` and object scope are independently enforced; review permission
  alone cannot submit.
- Stored eligibility/loan-limit IDs, recommendation, risk, TAT, reviewer, and comments remain
  unchanged; exception-required input is flagged without creating an exception decision.
- Forced audit/case failure rolls back every state/evidence write.

## Visual Acceptance Criteria
None.

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched.

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
