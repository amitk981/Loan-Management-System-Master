# Slice 006E: Appraisal Note Create Edit Submit

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Implement source §24 appraisal-note draft create/read/edit and submit-for-Credit-Manager-review,
including the linked risk assessment and two-day TAT facts.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 006D
- 005I3
- 005I4
- 006C2
- 006D2

## Prior Slice Handoff
- 006C calculates and atomically stores the source-backed loan-limit assessment only after 006B
  `overall_result = eligible`; 006D makes that stored snapshot readable without recalculation.
- 006C2 now guarantees the stored loan-limit snapshot used by appraisal comes only from verified
  selected land holdings, a verified crop plan linked to the same loan application, and agreed
  cultivated-acreage evidence. 006E must read the stored `land_area_acres`,
  `land_based_limit_amount`, `final_eligible_loan_amount`, and `exception_required_flag` from the
  snapshot; it must not re-run acreage comparison or fall back to current member land/crop/profile
  rows.
- 006E must require both stored assessments before appraisal creation and must consume their stored
  summaries/IDs rather than re-running eligibility or loan-limit formulas.
- Architecture review `2026-07-10_092630_architecture_review` queued 005I3/005I4 to complete the
  application nominee/detail contracts, 006C2 to block unresolved cultivated-acreage evidence, and
  006D2 to establish the deep `credit.modules.appraisal_workflow` seam. Do not start 006E until all
  four corrective slices are complete; implement appraisal through that credit seam rather than
  adding more behavior to `applications.services`.

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
- Implement appraisal behavior only through `sfpcl_credit.credit.modules.appraisal_workflow.AppraisalWorkflow`;
  application views may import that public module seam/result-error types but must not add appraisal
  behavior to `applications.services`.
- Use the `006D2` credit module snapshots for prerequisites:
  `EligibilityAssessmentModule.get(...)` for the stored eligibility result and
  `LoanLimitCalculator.get_assessment(...)` for the stored loan-limit result. Do not import private
  credit helpers, query current loan-policy rows, or recalculate loan-limit/acreage facts during
  appraisal create/read/update/submit.
- Implement `POST`, `GET`, and `PATCH
  /api/v1/loan-applications/{loan_application_id}/appraisal-note/` for one draft appraisal per loan
  application. PATCH is draft-only and updates only fields supplied.
- Implement `POST /api/v1/appraisal-notes/{loan_appraisal_note_id}/submit-for-review/` with required
  non-blank `remarks`; transition `draft -> review_pending` once.
- Persist one source §14.4 `LoanAppraisalNote` per application with `prepared_by_user`, nullable
  `reviewed_by_user`, `prepared_at`, nullable `reviewed_at`, `tat_due_at`, `tat_status`, required
  borrower/eligibility/loan-limit summaries, positive recommended amount, optional positive tenure,
  recommended interest type, required security summary, recommendation, and appraisal status.
- Persist the nested source §14.3 risk assessment with market, operational, borrower, and overall
  ratings plus mitigation notes, assessed user/time; link it from the appraisal note. Keep Credit
  Manager review fields nullable for 006F.
- Keep Credit Manager review decisions, sanction submission, exception approval creation,
  rejection-note generation, and frontend wiring out of scope.

## Database/Model Impact
Add non-destructive `risk_assessments` and `loan_appraisal_notes` models/migration matching
`data-model.md` §14.3-§14.4. Enforce one appraisal per application; index TAT status/due time,
recommendation, appraisal status, overall risk rating, and risk-assessment application ID as named
by the source.

## API Contracts
Request fields match `api-contracts.md` §24.1: required non-blank `borrower_summary`,
`eligibility_summary`, `loan_limit_summary`, `recommended_security_summary`; positive
`recommended_amount`; optional positive `recommended_tenure_months`;
`recommended_interest_type = floating` when supplied; nested `risk_assessment`; and
`recommendation = approve|reject|conditions`. Response includes the note/application IDs,
prepared-user summary/time, TAT due/status, recommendation, risk assessment, and appraisal status.

## Permissions
- Create requires `credit.appraisal.create`; PATCH requires `credit.appraisal.update`; submit
  requires `credit.appraisal.submit_review`; nested risk create/update also requires
  `credit.risk_assessment.manage`.
- GET permits the create/update/submit holder for its assigned/owned application and preserves the
  existing Credit Manager credit-domain object access for future 006F review. Do not invent the
  missing catalogue code `credit.appraisal.read` recorded in A-007.
- Every endpoint uses the existing application object-access boundary. Creation/preparation is for
  Deputy Manager Finance-style assigned/owned work; Credit Manager global credit-domain access does
  not grant create/update/submit-review permissions it does not hold.

## Audit Requirements
Successful create, draft update, and submit-for-review write metadata-only audit and workflow
evidence with no free-text summaries or mitigation notes copied into audit JSON. GET writes none.
Authentication, permission, object-scope, invalid-state, and validation failures write no
appraisal/risk rows or success evidence.

## Validation Rules
- Creation requires a stored `EligibilityAssessment.overall_result = eligible` and a stored 006D
  loan-limit snapshot. Missing/pending/ineligible prerequisites return invalid state.
- `recommended_amount` must be positive. It may exceed the stored final eligible amount only when
  the stored assessment already has `exception_required_flag = true`; 006E records the
  recommendation but does not create or approve an exception.
- Risk ratings accept only `low`, `medium`, or `high`; recommendation accepts only `approve`,
  `reject`, or `conditions`; unknown fields and blank required summaries fail validation.
- `tat_due_at = application.created_at + 2 days`; `tat_status` is `within_tat` when prepared/submitted
  no later than the due time and `breached` afterward. Do not reset the due time on PATCH or submit.
- PATCH is allowed only in `draft`. Submit requires a complete valid draft and transitions once to
  `review_pending`; later edits/repeated submit are blocked. 006F owns `reviewed`.

## Test Cases
- Static import-boundary regression proves 006E views/appraisal code use
  `credit.modules.appraisal_workflow` and do not reintroduce appraisal or credit-assessment helpers
  through `applications.services`.
- TDD red/green create through §24.1 response and stored linked risk assessment.
- GET returns the stored draft without side effects; PATCH updates supplied draft fields only.
- Missing/non-eligible eligibility or missing loan-limit snapshot blocks create without evidence.
- Required/enum/positive-value/nested-risk validation, including recommendation above a
  non-exception loan limit.
- Two-day TAT within/breached boundary and immutable due time across update/submit.
- Submit transitions draft to `review_pending`; repeated submit and PATCH after submit are blocked.
- Create/update/submit/risk permissions and application object scope are independently enforced;
  denial paths create no appraisal/risk/audit/workflow success evidence.

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
