# Review Packet: 2026-07-10_181310_normal_run

## Result
Success

## Slice
006E2-appraisal-source-contract-and-snapshot-hardening

## Outcome

- `AppraisalWorkflow` remains the deep module seam. Create copies the exact canonical redacted
  eligibility and loan-limit public projections; GET/PATCH/submit consume appraisal-owned copies.
- Required `repayment_capacity_notes` and persisted `submission_remarks` close M04-FR-009 and API
  §24.3 omissions without inventing a repayment formula.
- The migration safely copies only chronologically proven legacy inputs. Ambiguous rows stay
  `legacy_unverified` and downstream-blocked until one-way, authorised, draft revalidation.
- Static fixtures positively require both public prerequisite imports and reject concrete model,
  policy, and private-helper access without freezing the full class method set.

## Traceability

- API §3 says decision inputs must be snapshotted and sensitive actions retain a reason; code
  freezes both public projections and stores submit remarks, verified by
  `test_same_uuid_prerequisite_replacement_cannot_change_frozen_appraisal` and
  `test_submit_transitions_draft_once_and_locks_later_edits`.
- Functional §9.8/M04-FR-009 requires `repayment_capacity_notes`; create/PATCH/submit expose and
  validate that exact field, verified by
  `test_create_requires_non_blank_repayment_capacity_notes_without_writes`.
- ADR-0003 requires conservative legacy provenance; migration safe/ambiguous paths and explicit
  repair are verified by `AppraisalSnapshotMigrationTests` and the two revalidation tests.
- Codebase-design §§12.3/42 require workflow locality, public-interface tests, atomic writes, and
  thin views; implementation stays in `AppraisalWorkflow`, and rollback/static tests cover the
  seam.

## TDD and Evidence

- Red/green create: `evidence/terminal-logs/tdd-red-create-snapshots.log` and
  `tdd-green-create-snapshots.log`.
- Red/green submit reason: `tdd-red-submit-reason.log` and `tdd-green-submit-reason.log`.
- Red/green legacy repair: `tdd-red-legacy-revalidation.log` and
  `tdd-green-legacy-revalidation.log`.
- Immutable API and migration examples: `evidence/immutable-api-and-migration-proof.md`.
- Boundary and rollback suite: `evidence/terminal-logs/final-focused-backend.log`.

## Validation

- Backend check: pass.
- Migration sync: pass; no changes detected.
- Focused appraisal/module suite: 45 tests ran successfully, including two PostgreSQL-only skips.
- Full backend: 353 tests ran successfully, including two PostgreSQL-only skips; 95% coverage >= 85%.
- Frontend lint/typecheck: pass.
- Frontend: 107 tests pass across 16 files.
- Frontend build: pass; existing non-blocking bundle-size warning only.
- `git diff --check` and Python compilation: pass.

## Preserved PostgreSQL Concurrency Gate

This slice changed appraisal imports and copied assessment projections but did not alter the
calculator's locking implementation. After provisioning PostgreSQL, run from `sfpcl_credit/`:

```bash
/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test sfpcl_credit.tests.test_credit_modules.LoanLimitConcurrencyTests --settings=sfpcl_credit.config.postgres_test_settings -v 2
```

Required result: both tests pass on `database_backend=postgresql`. The default suite's SQLite skips
are not concurrency evidence.

## Recommended Next Action
Let the orchestrator independently validate and commit. Then run 006F review using only verified
frozen appraisal projections, followed by 006F2 and 006G.
