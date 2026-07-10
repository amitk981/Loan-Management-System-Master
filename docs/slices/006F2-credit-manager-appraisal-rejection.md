# Slice 006F2: Credit Manager Appraisal Rejection

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Complete functional requirement M04-FR-011 by adding a terminal Credit Manager appraisal
rejection and creating the existing source-backed rejection-note draft without sending it.

## Depends On
- 006F

## Source / Review References
- `docs/source/functional-spec.md` M04-FR-011 and §9.8
- `docs/source/api-contracts.md` §24.4 and §21.3
- `docs/source/test-plan.md` MOD-APPRAISAL-004 through MOD-APPRAISAL-007
- `docs/slices/005H-rejection-note-shell.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-10_173305_architecture_review`

## Scope
- Extend `AppraisalWorkflow.review(...)` with `decision = rejected` from `review_pending`.
- Require non-blank review comments and a source rejection reason/category compatible with the
  existing 005H rejection-note contract; unknown fields fail validation.
- Enforce the same `credit.appraisal.review`, Credit Manager object scope, and maker-checker rules
  as 006F. Review/create/update/submit permissions never imply rejection authority.
- Atomically persist reviewer/time/comments/decision, transition appraisal to terminal `rejected`,
  and create exactly one linked 005H rejection-note draft. Do not send a communication.
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
- [ ] Execution plan written
- [ ] Failing tests and red evidence saved first
- [ ] Code and additive migration (if required) implemented
- [ ] API contracts updated
- [ ] Full gates passed
- [ ] Risk assessment and handoff updated
- [ ] State updated
- [ ] Commit delegated to orchestrator only after passing gates
