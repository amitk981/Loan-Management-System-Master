# Risk Assessment

Risk level: High

- Selected slice: `006G-submit-to-sanction`
- Mode: `normal_run`
- Standing approval: active; no owner veto.
- Result: all configured quality gates passed.

## Material risks

- This action changes lending workflow state and creates the handoff record consumed by the future
  sanction committee. Incorrect state/history validation could admit an unreviewed pack.
- Duplicate concurrent submissions could create multiple pending cases or evidence sets if lock
  order or uniqueness fails.
- The new approval-case shell intentionally does not yet contain the source §15.3 approval-matrix
  rule or approver snapshots. A-059 assigns enrichment of this same unique row to 007A/007B; a
  later slice must not create a second case.
- Request remarks, review comments, risk notes, and appraisal summaries are sensitive business
  text. Copying them into generic audit/workflow evidence would expand exposure.
- The PostgreSQL-only competing-transaction test did not execute in this sandbox because the live
  Unix socket was denied with `Operation not permitted` before test-database creation. SQLite skip
  output is not concurrency proof.

## Controls applied

- Permission, active Credit Manager role, and object scope are independently enforced and tested.
- Submission requires reviewed status, verified/complete frozen prerequisites and risk facts, and
  an exact match between latest immutable review history and appraisal review projections.
- One transaction locks application, appraisal, history, then case namespace; one-to-one database
  constraints independently prevent duplicate application/appraisal cases.
- Rejected, missing, draft, returned, review-pending, inconsistent, repeated, denied, invalid, and
  forced case/audit failures are tested for no success side effects and atomic rollback.
- Audit/workflow evidence is metadata-only; the action reason remains only on the approval case.
- 372 backend tests passed at 93% coverage, plus every configured frontend and migration gate.

## Residual review

Independent host validation should execute
`SanctionSubmissionConcurrencyTests` with
`--settings=sfpcl_credit.config.postgres_test_settings` and zero skips. Epic 007 must review the
temporary shell-to-full-case migration described in A-059 before adding approval actions.
