# Slice 006H: Eligibility Appraisal Frontend Integration

## Status
Complete

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Replace the appraisal prototype's eligibility, loan-limit, appraisal, Credit Manager review, and
sanction-submission mock facts with the completed Epic 006 APIs while preserving the approved
Appraisal Workbench visual structure.

## User Value
Deputy Manager Finance and Credit Manager users can see and perform the real source-backed credit
assessment workflow instead of acting on sample calculations or statuses.

## Depends On
- 006G

## Prior Slice Handoff
- 006G returns `approval_case_id`, application/appraisal IDs, `submission_status = pending`, frozen
  `exception_required_flag`, submitter summary, and timestamp. It moves both statuses to
  `submitted_to_sanction_committee`; repeated/stale calls return `409`.
- The UI must never infer a sanction case from appraisal review alone. Show the submitted state
  only from the 006G response or a subsequent server read, retain the case UUID for Epic 007
  navigation, and do not synthesize approvers or exception decisions.

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
- Appraisal Workbench.
- Application Detail credit-assessment stage summary/link into the workbench.

## Frontend Scope
- Reuse the existing `AppraisalWorkbench`, `EligibilityChecklist`, `LoanLimitCalculator`, cards,
  badges, tabs, alerts, modal, and table/detail patterns without new styling or layout.
- Load stored eligibility, loan-limit, appraisal, review-history, rejection-note summary, and
  sanction-submission state from `/api/v1`; remove the corresponding `mockData` reads and derived
  sample workflow facts.
- Wire the existing controls to eligibility run, loan-limit calculate, appraisal create/update,
  prerequisite revalidation, submit-for-review, Credit Manager review/return/reject, and
  submit-to-sanction actions. Render an action only when the current user's permission set and the
  loaded server state allow it; always surface the server's standard error when a stale action is
  rejected.
- Send the sanction action as exactly `{ remarks }`; on success replace local appraisal/application
  status with the returned server state and display the pending case ID using the existing success
  pattern. Never retry the POST automatically after a timeout or `409`.
- Render loading, missing-assessment/empty, validation blocker, unauthorized/object-denied, API
  error, and success/updated states with existing alert/empty/loading patterns. Preserve ordered
  immutable `review_history` reasons across return/resubmit cycles.

## Backend/API Scope
No new business logic or persistence. Add only thin read/action client functions or a response
adapter required to consume the completed Epic 006 endpoints; do not recalculate eligibility or
loan limits in TypeScript and do not synthesize review/sanction state.

## Database/Model Impact
None.

## API Contracts
Consume the existing eligibility (§22), loan-limit (§23), appraisal/review (§24.1-§24.4), and
submit-to-sanction (§24.5/006G) contracts and standard success/error envelopes. Keep decimal amounts
as API strings until display formatting; send exact source request fields and reject unknown client
form fields before dispatch where existing form helpers already do so.

## Permissions
Use `/auth/me` permissions for visibility only. Deputy Manager Finance actions require their
existing create/update/submit/risk permissions; Credit Manager review requires the existing review
permission and role-authority backend check; sanction submission requires its independent
permission. A hidden control is never a substitute for backend permission/object-scope enforcement.

## Audit Requirements
Frontend actions rely on the owning backend endpoints for metadata-only audit/workflow evidence.
Do not send appraisal/review/rejection free text in headers, analytics, logs, or client telemetry.

## Validation Rules
- Display the stored backend explanations, rule version, policy source, final eligible amount,
  boundary warning, prerequisite provenance, TAT status, appraisal status, and ordered review
  history without recomputing them.
- Disable/omit draft edits outside `draft`, review outside `review_pending`, and sanction submit
  outside `reviewed`, while still handling `409 INVALID_STATE_TRANSITION` after stale races.
- A rejected appraisal shows its unsent rejection-note summary and no sanction action; a returned
  appraisal permits source-backed draft revision and resubmission without losing prior history.

## Test Cases
- API-client contract tests for every consumed GET/action path and standard error envelope.
- Workbench render/action tests for eligible/ineligible/pending eligibility, below/equal/above loan
  limit, draft/review-pending/returned/reviewed/rejected appraisal states, and immutable multi-row
  review history.
- Permission tests proving Deputy Manager and Credit Manager controls differ and zero-permission or
  object-denied users see no sensitive action.
- Regression proving no Appraisal Workbench/application-detail Epic 006 facts are imported from
  `mockData` and no frontend loan-limit formula remains.

## Visual Acceptance Criteria
Match the existing prototype patterns and include loading, empty, error, unauthorized, validation, and success states where relevant.

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
