# Review Packet: 2026-07-10_215124_normal_run

## Result

Success, pending independent orchestrator validation and commit.

## Slice

`006E4-legacy-appraisal-remediation-and-history-backfill` — High risk under standing approval.

## Implementation review

- Migration 0006 is data-only and forward-only. It scans only `legacy_unverified` notes, requires a
  complete latest decision projection, derives destination from the decision, skips an exact
  existing row, and creates one labelled `legacy_latest_only` history item. Reverse preserves
  immutable evidence; a second forward is idempotent.
- `AppraisalWorkflow.revalidate_prerequisites` remains the public deep-module seam. Draft and
  review-pending repair in place. Reviewed repair pins current facts, reopens to draft, and clears
  only mutable current review authority. Views only authenticate/parse/translate errors.
- Rejected/submitted rows are explicitly quarantined. Metadata evidence identifies prior/new state
  and whether authority was invalidated without copying recommendation, money, risk, comments, or
  other free text.

## Traceability

- Source API §3 says workflow is backend-enforced, sensitive actions use explicit endpoints,
  approvals are immutable, and decision inputs are snapshotted. Code keeps the explicit
  revalidation endpoint, pins current projections atomically, preserves append-only history, and
  invalidates a pre-remediation review. Verified by the draft/pending/reviewed/terminal API tests.
- Source API §24 and codebase-design §12.3 require appraisal review before sanction behind
  `AppraisalWorkflow`. Code reopens remediated reviewed notes and existing sanction guards reject
  them until maker resubmit plus fresh Credit Manager review. Verified end to end by
  `test_legacy_reviewed_revalidation_requires_fresh_review_before_sanction`.
- Data-model §34 and codebase-design §22 require atomic multi-record workflows. Forced audit and
  workflow failures restore state, projections, latest authority, immutable history, and evidence
  counts. Verified by `test_reviewed_revalidation_rolls_back_authority_clear_on_evidence_failure`.
- ADR-0004 requires only an explicitly labelled reconstructable latest legacy decision, never
  invented earlier cycles. Migration fixtures cover resubmitted/submitted states, existing rows,
  incomplete projections, prior cycles, reverse, and idempotency.

## Validation

- TDD RED/GREEN logs saved for missing migration, selective migration, review-pending remediation,
  reviewed authority invalidation, and malformed payload handling.
- 44 appraisal/migration tests collected: 42 passed and two PostgreSQL-only tests skipped in SQLite.
- Django check and migration synchronization passed.
- Full backend suite: 378 tests, five explicit PostgreSQL-only skips, 93% coverage (85% floor).
- Frontend: lint and typecheck passed; 126 tests passed; production build passed.
- `git diff --check` passed; one migration and no dependencies/frontend/protected/source changes.

## Recommended next action

Run `006F4-postgresql-credit-concurrency-acceptance`; execute its exact five-test PostgreSQL command
twice with zero skips. Default-suite skips are not acceptance evidence.
