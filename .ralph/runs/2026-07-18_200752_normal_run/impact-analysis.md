# Impact Analysis

Slice: `CR-011-github-ci-migration-test-schema-isolation`

## Affected backend pieces

- `sfpcl_credit/tests/test_approval_read_scope_migration.py`: `ApprovalReadScopeMigrationTests`
  uses `MigrationExecutor` to move `approvals` from `0009` to `0010`, but unlike the other
  migration-changing `TransactionTestCase` classes it has no `tearDown` that migrates the worker
  database back to all leaf nodes. Grep/AST inspection found this was the only migration-changing
  transaction test without restoration.
- `sfpcl_credit/tests/test_communication_job_migration.py`:
  `GenericCommunicationJobMigrationTests` uses current application/disbursement/approval fixtures
  before migrating `communications` backwards and forwards. Its cleanup restores leaf migrations,
  but setup does not explicitly establish a current schema before those current-model fixtures run.
- Production models involved only as consumers of the leaked schema are
  `approvals.ApprovalCase` (including `appraisal_review_decision_id` from approvals migration
  `0011`) and `communications.CommunicationDeliveryJob`. No model, migration, endpoint, serializer,
  service, URL, or business rule will change.

## Affected frontend

No frontend screen, component, or route is affected. This slice changes backend test isolation only,
so `FRONTEND_DESIGN_RULES.md` requires and receives no UI work.

## Blast radius

- Approval migration tests can leak an old `approval_cases` table to any later test sharing the same
  Django worker database.
- Communications migration tests construct a real disbursement-advice fixture, which traverses
  applications, credit, approvals, legal-documentation/readiness, loans, disbursements, and
  communications test helpers. Those modules are consumers of the schema state but their production
  code is not changed.
- Parallel CI is affected nondeterministically when both classes are assigned to one worker; serial
  execution is deterministically affected in the formerly failing order.
- All other migration-changing `TransactionTestCase` classes were audited and already restore the
  current migration leaf nodes in cleanup.

## Existing coverage and regression coverage

- Approvals module: the existing `ApprovalReadScopeMigrationTests` validates the `0010` backfill.
  Regression change: add leaf-node restoration in `tearDown`, then execute it immediately before
  the communications migration class in one Django process.
- Communications module: the existing `GenericCommunicationJobMigrationTests` validates retained
  job identity/attempt history and worker-lease backfill. Regression change: explicitly migrate to
  current leaf nodes in `setUp`, then execute it both after and before the approvals migration class.
- Cross-module/order regression: run both affected class labels sequentially in the formerly failing
  order and in reverse order; run the same focused labels with four Django workers. These commands
  exercise the actual Django test runner/database lifecycle rather than a mocked schema assertion.

## Scope guard

No production migration, model, API, endpoint, frontend file, dependency, or configuration file is
in scope. If the fix requires any such change, stop and reassess rather than broadening this CR.
