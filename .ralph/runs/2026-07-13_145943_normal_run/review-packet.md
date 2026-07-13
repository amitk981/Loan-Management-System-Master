# Review Packet: 2026-07-13_145943_normal_run

## Result

Local implementation and configured non-PostgreSQL gates pass. Run the declared trusted
PostgreSQL acceptance twice, then commit/merge only if it passes.

## Slice

`007D3-returned-approval-cycle-and-resubmission-closure`

## Standards Review

The independent standards reviewer found unfinished Ralph artifacts and missing approved/rejected
denial rows; both are closed in this packet/state/handoff and the six-row review-finding test log.
Database constraint tests were added for positive cycle/revision, application-cycle uniqueness,
one pending cycle, and later-cycle review identity. No protected-path, scope, diff-limit,
migration-limit, indexing, transaction-order, or quality-gate violations remain.

The reviewer noted a judgment-call module seam: sanction handoff calls the approval case engine's
fact serializer through the same sibling-module pattern already used for canonical case
serialization. It remains approval-owned and no credit module imports approvals, so no new public
cross-app dependency was introduced.

## Spec Review

The independent spec reviewer found four partial areas. Closure:

1. Concurrency: the slice now declares `postgresql-five-race-acceptance`; the real resubmission race
   asserts one cycle-2 shell/evidence set and unchanged cycle-1 ledgers. Local socket denial is
   retained; trusted orchestration runs it twice.
2. Lifecycle denials: pending, approved, rejected, uncorrected, and corrected-without-fresh-review
   attempts all assert exact no-write ledgers.
3. Read/projection scope: current/returned collection/detail/action projections assert cycle
   numbers for approvers, Company Secretary, Auditor, and permission-only denial; read-only roles
   never enter assigned queues.
4. Review/revision integrity: later cycles require a review FK at the database boundary;
   `appraisal_revision` advances by the number of attributable corrections, and the latest review
   must follow the latest correction. Migration conservatively leaves only unmatched legacy
   cycle-1 review ids nullable rather than inventing business history.

No scope creep was found.

## Traceability

- Data model application-to-many approval cardinality and §15.3-15.5 immutability -> ForeignKey
  case cycles, unique constraints, exact case/action linkage ->
  `test_return_correction_fresh_review_creates_immutable_second_cycle` and
  `ApprovalCycleMigrationTests`.
- Codebase design §13.1 says material re-approval creates a new cycle -> non-empty changed-field
  correction plus later immutable review -> no-op/no-fresh-review and full two-cycle tests.
- API §§24.4-25.8 and M05-FR-007/008 say reviewed submission, return reason, and immutable decisions
  -> existing action endpoint plus draft correction/review/resubmit boundary -> lifecycle denial
  matrix and canonical cycle projection tests.
- 007C3 object scope must survive history -> frozen case facts plus unchanged selector/reader grants
  -> Company Secretary/Auditor/current-assignee/permission-only cross-cycle assertions.

## Validation

- Frontend build/typecheck/lint and 208 tests: PASS.
- Backend Django check/migration sync: PASS.
- Backend full suite: 628 tests PASS, 19 expected PostgreSQL-only skips.
- Coverage: 93% (floor 85%).
- `git diff --check`: PASS.

## Recommended Next Action

Run trusted PostgreSQL acceptance twice; on pass, let Ralph commit and merge. Next slice: `007E`.
