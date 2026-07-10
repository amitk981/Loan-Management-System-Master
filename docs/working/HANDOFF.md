# Ralph Handoff

## Last Run
2026-07-10_193616_normal_run

## Current Status
Completed `006E3-appraisal-history-and-review-authority-hardening` under standing High-risk
approval.

- Every successful `reviewed`, `returned`, or `rejected` action now creates one immutable
  appraisal-owned `AppraisalReviewDecision` inside the existing `AppraisalWorkflow.review(...)`
  transaction. The appraisal's existing review fields remain the latest projection; API
  `review_history` retains all reasons, reviewers, times, and from/to states.
- Review requires both `credit.appraisal.review` and active `credit_manager` primary-role
  membership. An in-scope owner/receiver with only the permission receives `PERMISSION_DENIED` and
  writes nothing. A real Credit Manager retains domain-wide credit-assessment scope and the
  distinct `OBJECT_ACCESS_DENIED` result outside that domain.
- Migration 0005 keeps legacy provenance verified only with positive pre-preparation success audits
  for both exact same-application prerequisite UUIDs, safe source timestamps, and no later success
  audit. All other formerly verified rows become `legacy_unverified`; copied JSON, UUIDs, rejection
  notes, and latest decision facts are untouched.
- The migration backfills at most one complete latest legacy review decision with
  `legacy_latest_only` provenance. Reversing drops the derived history table without falsely
  upgrading unproven prerequisites.
- Generic audit/workflow evidence references the decision UUID and excludes review comments,
  detailed rejection reason, and frozen appraisal/risk free text.

## Validation
Three public-behavior TDD RED/GREEN cycles and the full 36-test appraisal suite passed. Django check
and migration sync passed. The full default backend suite ran 363 tests successfully with the two
pre-existing PostgreSQL-only skips; coverage is 95% (floor 85%). Frontend lint/typecheck, 107 tests,
and build passed. Evidence is in `.ralph/runs/2026-07-10_193616_normal_run/`.

## Next Run
Run `006F3-appraisal-lock-order-and-postgresql-concurrency-closure`. It must not complete or merge
without executing both the existing loan-limit and new appraisal concurrency suites on PostgreSQL
with zero skips. Then run sharpened `006G-submit-to-sanction`; it must require a latest immutable
history row consistent with the reviewed projection and preserve the entire history and rejected
notes unchanged.
