# Slice 006F: Credit Manager Review

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Implement source §24.4 Credit Manager review for a submitted appraisal, including maker-checker,
review-return, stored reviewer/comment facts, and metadata-only evidence. Sanction submission stays
in 006G.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 006E2

## Prior Slice Handoff
- 006E owns one `credit.models.LoanAppraisalNote` and linked `RiskAssessment` per application,
  draft editing, immutable two-day TAT facts, and `draft -> review_pending` submission through
  `AppraisalWorkflow`. The note stores prerequisite assessment UUID snapshots without concrete
  assessment-model FKs.
- Extend the existing `AppraisalWorkflow.review(...)` interface and existing thin application view
  pattern. Do not move review behavior into `applications.services` or query eligibility/loan-limit
  rows from the view.
- 006F must review that stored note without recalculating 006B eligibility or the 006D loan-limit
  snapshot. 006G separately owns `submit-to-sanction-committee` and approval-case creation.
- Credit assessment persistence is credit-owned after 006D3, but concrete eligibility/loan-limit
  models remain implementation details. Review must operate on 006E's appraisal interface/state
  and must not import or mutate either assessment model.
- 006E2 freezes the exact prerequisite projections, adds required repayment-capacity notes, and
  persists the submit-for-review reason. Review must require verified snapshot provenance and must
  not reread current assessment rows, even if they were rerun under the same UUID.

## Source References
- `docs/source/api-contracts.md` §3 and §24.4: compliance reason, snapshot decisions, and exact
  `decision` / `review_comments` request boundary.
- `docs/source/data-model.md` §14.2-§14.4 and §34: stored loan-limit/appraisal facts and atomic
  appraisal/audit/workflow coordination.
- `docs/source/codebase-design.md` §12.3 and §26.1-§26.3: review through `AppraisalWorkflow` and
  transactional interface tests rather than concrete assessment helpers.
- `docs/source/implementation-roadmap.md` §11, `docs/source/functional-spec.md` M04-FR-008 through
  M04-FR-010, and `docs/source/test-plan.md` MOD-APPRAISAL-005/MOD-APPRAISAL-007.

## Prototype Reference
- sfpcl-lms/src/pages/appraisal/AppraisalWorkbench.tsx
- sfpcl-lms/src/components/loan/EligibilityChecklist.tsx
- sfpcl-lms/src/components/loan/LoanLimitCalculator.tsx

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
- Implement `POST /api/v1/appraisal-notes/{loan_appraisal_note_id}/review/`.
- Accept source §24.4 `decision` and `review_comments`. Support `decision = reviewed` from the API
  example and `decision = returned` from test-plan MOD-APPRAISAL-005.
- `reviewed` transitions `review_pending -> reviewed`, stores reviewer/time/comments, and locks the
  appraisal against further preparation edits/review actions.
- `returned` requires a non-blank reason, stores the reviewer/time/comments and returns the note to
  `draft` so 006E's existing maker can revise and resubmit. The audit/workflow decision remains
  `returned`; do not lose the return reason by treating it as an unaudited edit.
- Keep sanction submission/approval cases, exception route creation, rejection-note generation,
  frontend wiring, and approval-matrix calculations out of scope.
- A terminal `rejected` appraisal plus rejection-note creation is explicitly owned by 006F2 so
  M04-FR-011 is not confused with 006F's returned-for-revision path.

## Database/Model Impact
Use 006E's nullable `reviewed_by_user`, `reviewed_at`, and appraisal status fields. Add only the
smallest non-destructive `review_comments` and `last_review_decision` fields (006E does not persist
them), with one migration; retain prior return history in audit/workflow evidence;
do not add sanction or approval tables in this slice.

## API Contracts
Request matches `api-contracts.md` §24.4: `decision` plus non-blank `review_comments`. Response
returns appraisal/application IDs, `appraisal_status`, `decision`, reviewer user summary,
`reviewed_at`, and stored review comments. Use the standard success/error envelopes.

## Permissions
- Require `credit.appraisal.review` and the Credit Manager credit-domain object-access boundary.
- Enforce maker-checker: the `prepared_by_user` cannot review their own appraisal even if they hold
  the review permission. Do not grant review through create/update/submit-review permissions.
- Missing global permission returns `403 PERMISSION_DENIED`; in-role but out-of-scope access returns
  `403 OBJECT_ACCESS_DENIED` using the existing application boundary.

## Audit Requirements
Successful reviewed/returned decisions write metadata-only `appraisal.reviewed` or
`appraisal.returned` audit and workflow evidence with appraisal/application IDs, state change,
decision, actor/time, and request ID. Do not copy borrower/eligibility/loan-limit/security/risk
summaries or free-text review comments into audit JSON. Denied/invalid/validation paths write no
review success evidence.

## Validation Rules
- Review requires `appraisal_status = review_pending`; draft, reviewed, returned-to-draft, and later
  submitted states return `409 INVALID_STATE_TRANSITION`.
- Only `reviewed` and `returned` decisions are accepted. `review_comments` is required and non-blank;
  unknown fields return `400 VALIDATION_ERROR`.
- The actor must differ from `prepared_by_user` (test-plan MOD-APPRAISAL-007).
- Returning for revision moves the note back to `draft`; a later maker resubmission is required
  before another review. A reviewed note is immutable until 006G consumes it.
- Review never changes or recomputes the stored eligibility, loan-limit, recommended amount, risk,
  or TAT snapshot facts.

## Test Cases
- TDD red/green reviewed decision from `review_pending`, with reviewer/time/comments persisted and
  metadata-only audit/workflow evidence.
- Returned decision requires a reason, moves back to draft, permits maker revision/resubmission,
  and then permits a later Credit Manager review.
- Draft/reviewed/repeated review paths are blocked without changing stored facts or evidence counts.
- Maker cannot review their own appraisal; create/update/submit-review permission alone cannot
  review; missing permission and object-scope denial create no success evidence.
- Review leaves the stored 006B eligibility, 006D loan-limit snapshot, risk assessment, TAT due
  time, repayment-capacity notes, submission reason, and recommendation unchanged. The test must
  rerun a current assessment under the same UUID and prove review still uses 006E2's frozen facts.
- Static boundary fixtures must still reject package/aliased concrete assessment imports and must
  positively find the public `AppraisalWorkflow` route; adding `review` must not restore an exact
  full-class method-set assertion.

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
