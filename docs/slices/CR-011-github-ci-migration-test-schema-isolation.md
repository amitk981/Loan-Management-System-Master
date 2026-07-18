# Slice CR-011: GitHub CI migration tests leak an older approvals schema

## Status
Not Started

## Origin
Change request (maintenance stage), accepted 2026-07-18 from docs/change-requests/accepted/CR-011-github-ci-migration-test-schema-isolation.md.

## Risk Level
High

## Change Request (verbatim)

# GitHub CI migration tests leak an older approvals schema

## Type
bug-backend

## Severity
High

## What Is Happening
The GitHub backend CI suite can fail with `django.db.utils.OperationalError: table approval_cases has no column named appraisal_review_decision_id`. `ApprovalReadScopeMigrationTests` migrates its worker database to `approvals.0010` and does not restore the current leaf migrations. If `GenericCommunicationJobMigrationTests` later runs on that worker, its current-model disbursement fixture expects the `appraisal_review_decision_id` column introduced by `approvals.0011` and fails before testing the communications migration. Local parallel runs can pass when the two classes land on different workers.

## Expected Behaviour
Every migration test must leave its worker database at the current leaf migration state. The communications migration test must start from an explicitly valid schema and produce the same result regardless of test order or worker count.

## Steps To Reproduce
1. Start from the `staging` branch at or after commit `7c577686`.
2. Run `ApprovalReadScopeMigrationTests` and then `GenericCommunicationJobMigrationTests` sequentially in the same test process.
3. Observe that the first class leaves `approval_cases` at migration `approvals.0010`.
4. Observe the communications fixture fail while inserting an `ApprovalCase` because `appraisal_review_decision_id` is absent.
5. Run the complete backend suite with four parallel workers and observe that the failure depends on worker assignment.

## Where It Appears
GitHub backend CI and the Django migration tests in `sfpcl_credit/tests/test_approval_read_scope_migration.py` and `sfpcl_credit/tests/test_communication_job_migration.py`.

## Source Document Reference
`docs/working/DECISION_POLICY.md` section 2 requires all backend tests and quality gates to be green. This is test isolation infrastructure and does not change a product business rule.

## Acceptance Criteria
- The two affected migration-test classes pass sequentially in the same process in the formerly failing order.
- Reversing their order also passes.
- The affected tests pass under four-worker execution matching GitHub CI.
- Every `TransactionTestCase` that changes migration state restores the current leaf migrations during cleanup.
- The full backend suite passes with four workers with the same test count, skips, and coverage requirements as the established gate.
- No production migration, model, endpoint, or business behavior is weakened or changed.

## Mandatory First Step: Impact Analysis
Before changing ANY code, write impact-analysis.md in the run folder covering:
- Affected backend models/endpoints/services, with grep evidence.
- Affected frontend screens/components/routes.
- Blast radius: every OTHER module that consumes the affected pieces.
- Existing tests covering the affected pieces, and the regression tests to add in EACH affected module.
- FRONTEND_DESIGN_RULES compliance note for any UI change.
Validation fails this run if impact-analysis.md is missing.

## Acceptance Criteria
- The change request's own acceptance criteria are met.
- Regression tests added for every module named in the impact analysis.
- All quality gates pass.
