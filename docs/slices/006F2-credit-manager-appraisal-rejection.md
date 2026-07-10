# Slice 006F2: Credit Manager Appraisal Rejection

## Status
Complete

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Complete functional requirement M04-FR-011 by adding a terminal Credit Manager appraisal
rejection and creating the existing source-backed rejection-note draft without sending it.

## Depends On
- 006F

## Prior Slice Handoff
- 006F persists `review_comments`, `last_review_decision`, `reviewed_by_user`, and `reviewed_at` on
  the existing `LoanAppraisalNote` through `AppraisalWorkflow.review(...)` under one row lock and
  atomic metadata-only audit/workflow evidence.
- Its accepted decisions are currently exactly `reviewed` and `returned`; add `rejected` without
  changing the `returned -> draft` revision/resubmission contract or the `reviewed` terminal state.
- Reuse 006F's `credit.appraisal.review`, Credit Manager credit-domain scope, maker-checker,
  `review_pending`, and `prerequisite_provenance = verified` guards. Do not invoke revalidation or
  query concrete eligibility/loan-limit models.

## Source / Review References
- `docs/source/functional-spec.md` M04-FR-011 and §9.8
- `docs/source/api-contracts.md` §24.4 and §21.3
- `docs/source/test-plan.md` MOD-APPRAISAL-004 through MOD-APPRAISAL-007
- `docs/slices/005H-rejection-note-shell.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-10_173305_architecture_review`

## Scope
- Extend `AppraisalWorkflow.review(...)` with `decision = rejected` from `review_pending`.
- Consume only 006E2's verified appraisal-owned prerequisite projections and preserve its
  `repayment_capacity_notes` and `submission_remarks`; never reread or navigate current
  eligibility/loan-limit models, even when their UUIDs match the stored provenance IDs.
- Require non-blank review comments and a source rejection reason/category compatible with the
  existing 005H rejection-note contract; unknown fields fail validation.
- Enforce the same `credit.appraisal.review`, Credit Manager object scope, and maker-checker rules
  as 006F. Review/create/update/submit permissions never imply rejection authority.
- Atomically persist reviewer/time/comments/decision, transition appraisal to terminal `rejected`,
  and create exactly one linked 005H rejection-note draft with `communication_status = not_sent`.
  Do not send a communication or create an approval/sanction case.
- Reuse a public rejection-note module/service seam; do not duplicate rejection-note validation,
  serialization, audit, or workflow rules in the credit view.
- Metadata-only appraisal evidence may record IDs/category/state but must not copy free-text review
  comments or detailed rejection reason. Failure rolls back appraisal, rejection note, audit, and
  workflow writes.

## Test Cases
- Credit Manager rejection creates one draft rejection note and terminal appraisal state.
- Blank/unknown reason, maker self-review, wrong state, missing permission, and out-of-scope paths
  create no success evidence.
- Repeated rejection is blocked and does not duplicate the note.
- Existing `reviewed` and `returned` decisions remain unchanged; rejected appraisal cannot submit
  to sanction.
- Forced rejection-note/audit/workflow failure rolls back the whole decision.

## Evidence Required
TDD red/green, API examples linking appraisal and rejection-note IDs, metadata redaction proof, and
all standard gates.

## Risk Level
High

## Acceptance Criteria
- M04-FR-011 is reachable through the Credit Manager review boundary.
- Rejection produces one auditable unsent note and cannot route to sanction.
- Existing review-return and rejection-note contracts are reused, not duplicated.

## Done Checklist
- [x] Execution plan written
- [x] Failing tests and red evidence saved first
- [x] Code implemented; no migration required
- [x] API contracts updated
- [x] Full gates passed
- [x] Risk assessment and handoff updated
- [x] State updated
- [ ] Commit delegated to orchestrator only after passing gates
