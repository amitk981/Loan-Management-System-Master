# Migration Plan Diagnosis

## Symptom

Independent complete-suite coverage failed
`CreditAssessmentModelOwnershipMigrationTests.test_forward_move_preserves_rows_relationships_and_evidence_references`
with `InvalidMigrationPlan`. Django reported one forwards operation
(`credit.0001_credit_assessment_model_ownership`) and one backwards operation
(`workflows.0002_workflow_tasks`) in the same plan.

## Reproduction

The exact named test reproduced the failure before the repair:

```text
/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py test sfpcl_credit.tests.test_credit_model_ownership_migration.CreditAssessmentModelOwnershipMigrationTests.test_forward_move_preserves_rows_relationships_and_evidence_references -v 2
```

Captured output: `terminal-logs/credit-ownership-migration-red.log`.

## Root cause

The historical ownership-migration fixture set `credit` to its pre-move state but did not pin
`workflows`. Before 012EA, `workflows.0001` was already the leaf, so the omission was harmless.
After 012EA added `workflows.0002`, test database setup left that new leaf applied. The test's next
executor call therefore requested `credit.0001` forwards and `workflows.0002` backwards together,
which Django intentionally rejects.

`workflows.0002` has no dependency on `credit.0001`; the product migration graph is valid. The
defect was historical migration-test isolation, not task schema or task-engine behavior.

## Repair

The fixture's `migrate_from` targets now include
`workflows.0001_canonical_workflow_event`. Setup reverses both historical targets together, and
the test then applies only `credit.0001` forwards. No production model, migration, route, or task
behavior changed.

## Verification

- Exact previously failing test: 1 passed.
- Owning migration-test module: 2 passed, including forward and reverse row/relationship/evidence
  preservation.
- Django system check: no issues.
- Migration consistency: no changes detected.
- `git diff --check`: passed.

Captured GREEN output:

- `terminal-logs/credit-ownership-migration-green.log`
- `terminal-logs/credit-ownership-migration-module-green.log`
- `terminal-logs/backend-schema-checks-green.log`
