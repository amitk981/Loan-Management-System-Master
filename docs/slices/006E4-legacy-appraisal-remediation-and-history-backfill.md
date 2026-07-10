# Slice 006E4: Legacy Appraisal Remediation and History Backfill

## Status
Complete

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Close architecture review `2026-07-10_213352_architecture_review` by giving every non-terminal
appraisal downgraded to `legacy_unverified` a safe, explicit repair path and by retaining the latest
known returned decision even when the appraisal was resubmitted before migration.

## Depends On
- 006H

## Source / Review References
- `docs/source/api-contracts.md` §3 and §24
- `docs/source/data-model.md` §14.4 and §34
- `docs/source/codebase-design.md` §12.3, §22, §26, and §35
- `docs/adr/ADR-0003-freeze-appraisal-prerequisite-projections.md`
- `docs/adr/ADR-0004-append-only-appraisal-review-decisions.md`
- `docs/working/ASSUMPTIONS.md` A-061
- `docs/working/REVIEW_FINDINGS.md` entry for this review

## Scope

- Add a forward-only corrective data migration that backfills at most one missing latest-known
  legacy review decision whenever the latest projection is complete, even if a later submit moved
  the current appraisal from returned `draft` to `review_pending` or from reviewed to sanction.
  Derive the historical decision's destination from the decision itself; label it
  `legacy_latest_only`; never fabricate an earlier cycle or duplicate an existing history row.
- Extend the existing explicit prerequisite-revalidation action for `legacy_unverified`
  `review_pending` and `reviewed` appraisals. A repaired `review_pending` appraisal remains pending
  for an independent Credit Manager decision. A repaired `reviewed` appraisal must invalidate its
  latest projection, preserve immutable history, return to `draft`, and require maker resubmission
  and fresh review before sanction. Rejected/submitted terminal rows remain immutable and visibly
  quarantined for governed manual repair; do not silently bless them.
- Preserve all caller-authored recommendation, repayment, risk, TAT, and prior history facts.
  Store the new frozen projections atomically and emit metadata-only audit/workflow evidence that
  names the remediation and prior/new state without copying financial/risk/free-text facts.
- Keep the repair behind `AppraisalWorkflow`; views remain thin and concrete assessment/history
  models do not enter the interface.

## Test Cases

- Migration fixtures cover returned-then-resubmitted `review_pending`, reviewed-then-submitted,
  already-backfilled, incomplete latest projection, and multiple historical cycles; only one
  reconstructable latest-only row is added and the migration is idempotent.
- Draft, review-pending, reviewed, rejected, and submitted `legacy_unverified` rows each have an
  explicit tested outcome. No non-terminal row is permanently stranded and no terminal row is
  silently revalidated.
- Reviewed remediation preserves immutable history but clears current review authority, returns to
  draft, and cannot sanction until resubmit plus a fresh Credit Manager review.
- Permission/object denial, malformed payload, and forced audit/workflow failures write nothing.

## Evidence Required

TDD red/green output, migration forward/reverse/idempotency evidence, state-remediation examples,
and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Every downgraded non-terminal legacy appraisal has a safe reachable repair path.
- No old review is treated as approval of newly pinned prerequisites.
- The latest reconstructable legacy reason is retained without inventing history.
