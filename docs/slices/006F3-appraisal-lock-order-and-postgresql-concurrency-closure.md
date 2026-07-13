# Slice 006F3: Appraisal Lock Order and PostgreSQL Concurrency Closure

## Status
Complete

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Close architecture review `2026-07-10_190455_architecture_review` by removing the appraisal/
rejection lock-order inversion and obtaining the PostgreSQL concurrency evidence that 006D2C
required but did not produce before merge.

## Depends On
- 006E3

## Source / Review References
- `docs/source/codebase-design.md` §12.2-§12.3, §22.1-§22.3, §26.1-§26.4
- `docs/source/data-model.md` §14.2-§14.4 and §34
- `docs/source/api-contracts.md` §3 and §24.4
- `docs/slices/006D2C-loan-limit-concurrency-and-boundary-regression.md`
- `docs/slices/006F2-credit-manager-appraisal-rejection.md`
- `docs/working/ASSUMPTIONS.md` A-055
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-10_190455_architecture_review`

## Scope

- Establish and document one lock order for appraisal mutations: loan application, appraisal note,
  then rejection-note/history rows. `create_or_update`, submit, revalidation, review, and rejection
  must not acquire the same rows in the opposite order.
- Preserve the public `AppraisalWorkflow` interface and the existing rejection-note module seam.
  Do not move validation/evidence rules into views or expose concrete models.
- Add PostgreSQL `TransactionTestCase` outcomes through the public interfaces for concurrent
  rejected review versus stale draft PATCH and concurrent duplicate review/rejection. Prove no
  deadlock escapes as a server error, exactly one valid terminal decision wins, no duplicate note or
  review history appears, and loser paths add no success evidence.
- Lock the existing appraisal review-decision queryset only after application and appraisal locks;
  never update an existing history row. The winning transaction must persist one `native` history
  row whose UUID matches its appraisal audit/workflow evidence and whose from/to states match the
  terminal appraisal transition.
- Run the existing 006D2C `LoanLimitConcurrencyTests` unchanged on PostgreSQL in the same acceptance
  session. A missing driver/server, connection failure, SQLite skip, mocked lock assertion, or test
  collection without execution is a failed slice, not a deferral.
- Do not change formula, review/rejection payloads, permissions, appraisal states, rejection-note
  semantics, frozen snapshots, or sanction behavior.

## Test Cases

- Rejected review and a stale concurrent PATCH serialize in the documented order without deadlock;
  rejection wins and the invalid update writes nothing.
- Two concurrent review/rejection attempts yield one terminal decision and one complete matching
  history/audit/workflow set; the losing transaction leaves the pre-race history byte-for-byte
  unchanged and no duplicate rejection note is possible.
- Existing reviewed/returned/rejected state, maker-checker, role/permission, rollback, frozen-fact,
  and static import suites remain green.
- PostgreSQL valid/valid and valid/invalid loan-limit tests both execute and print their deterministic
  ordering with zero skips.

## Evidence Required

- PostgreSQL server/version and connection settings with secrets omitted.
- Exact 006D2C plus new appraisal concurrency command output showing all tests executed, zero skips,
  and deterministic ordering.
- TDD red/green lock-order output and all standard gates.

## Risk Level
High

## Acceptance Criteria

- Cross-domain appraisal/rejection transactions use one lock order and have competing-transaction
  outcome proof.
- The previously missing authoritative loan-limit concurrency proof is green on PostgreSQL.
- The slice must not be marked Complete or merged if either PostgreSQL suite is unavailable,
  skipped, or failing.

## Done Checklist
- [ ] Execution plan written
- [ ] Failing tests and red evidence saved first
- [ ] Lock order normalized through the public module
- [ ] PostgreSQL loan-limit and appraisal concurrency suites passed with zero skips
- [ ] Full gates passed
- [ ] Risk assessment and handoff updated
- [ ] State updated
- [ ] Commit delegated to orchestrator only after passing gates
