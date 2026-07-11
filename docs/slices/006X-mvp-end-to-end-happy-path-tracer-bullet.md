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
- 006H3

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
Drive the existing 006H controls with real Deputy Manager Finance and Credit Manager sessions.
Assert displayed IDs/statuses match API responses and save reviewed/pending-case screenshots; add
no production UI, mock credit facts, or client-side calculation.

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

## Sharpened Cross-Role Assertions

- The Deputy Manager Finance session must observe the server-advertised eligibility, calculation,
  create/update, and submit-review controls; the Credit Manager session must observe review and,
  only after `reviewed`, sanction submission. Zero-permission or missing-action sessions expose none.
- After sanction submission, reload through
  `GET /api/v1/loan-applications/{id}/sanction-case/` and assert the UI/API share the exact
  `approval_case_id`, application/appraisal statuses, submission status, review-decision UUID,
  workflow-event UUID, exception flag, actor, and timestamp.
- Capture the exact appraisal PATCH body and prove it contains only 006H2's writable appraisal/risk
  allowlist; the tracer must fail if response-only status, snapshot, history, reviewer, TAT, or case
  fields are sent.
- Consume only enabled resource `available_actions` from the 006H4 six-field projection. The E2E
  path must explicitly prove that a permission present in `/auth/me` does not expose a control when
  the selected resource omits or disables the matching action.

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

## Run-Ahead Sharpening Review (006H6, 2026-07-11)

- Treat disabled actions as first-class response facts: assert their exact reason, permission, and
  role before the cross-role happy path consumes the enabled counterpart.
- Each successful UI mutation must be followed by exactly the eligibility, loan-limit, appraisal,
  and sanction-case reads; stale `409` proof remains one mutation with no retry or refresh.

## Run-Ahead Sharpening Review (architecture review 2026-07-11_212738)

- Consume 006H7's predicate-parity projections: before each cross-role click, assert the action's
  exact `required_permission`, `required_role`, and disabled reason in a paired denied state, then
  prove the enabled counterpart succeeds through the same public boundary.
- This tracer may begin only after 006H3 preserves the mounted-container matrix through visual
  restoration. It must not weaken those focused assertions or use the happy path to stand in for
  maker-checker, object-denial, field-error, or stale-write coverage.
