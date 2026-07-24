# Failure Summary

- Run: 2026-07-24_151220_normal_run
- Mode: normal_run
- Slice: 012EA-workflow-task-engine-and-task-inbox-apis
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=1, skipped=172)
```

## Last 50 lines: backend-coverage-results.md

```
Catalogue seeded: 199 permissions, 20 roles, 8 teams, 274 role-permission links.
Catalogue seeded: 199 permissions, 20 roles, 8 teams, 274 role-permission links.
....Catalogue seeded: 199 permissions, 20 roles, 8 teams, 274 role-permission links.
.........ssssssss.....sssCatalogue seeded: 199 permissions, 20 roles, 8 teams, 274 role-permission links.
Catalogue seeded: 199 permissions, 20 roles, 8 teams, 274 role-permission links.
.........................ssss...........ssss.sssss.sssss............ssssssssssssssssssssssssssssssssssssssssssssssssssssssss.....sssssE
======================================================================
ERROR: test_forward_move_preserves_rows_relationships_and_evidence_references (sfpcl_credit.tests.test_credit_model_ownership_migration.CreditAssessmentModelOwnershipMigrationTests.test_forward_move_preserves_rows_relationships_and_evidence_references)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 57, in testPartExecutor
    yield
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 623, in run
    self._callTestMethod(testMethod)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 579, in _callTestMethod
    if method() is not None:
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_151220_normal_run/sfpcl_credit/tests/test_credit_model_ownership_migration.py", line 56, in test_forward_move_preserves_rows_relationships_and_evidence_references
    self.executor.migrate(self.migrate_to)
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/migrations/executor.py", line 125, in migrate
    raise InvalidMigrationPlan(
    ^^^^^^^^^^^^^^^^^
django.db.migrations.exceptions.InvalidMigrationPlan: ('Migration plans with both forwards and backwards migrations are not supported. Please split your migration process into separate plans of only forwards OR backwards migrations.', [(<Migration credit.0001_credit_assessment_model_ownership>, False), (<Migration workflows.0002_workflow_tasks>, True)])

----------------------------------------------------------------------
Ran 1793 tests in 1327.218s

FAILED (errors=1, skipped=172)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 89.106s
  Creating 'default' took 89.017s
  Cloning 'default' took 0.012s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.019s
  Cloning 'default' took 0.017s
  Cloning 'default' took 0.019s
Total database teardown took 0.065s
Total run took 1417.448s

Duration milliseconds: 1418541
Exit code: 1
```

## Changed files (git status)

```
.ralph/runs/2026-07-24_151220_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-24_151220_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-24_151220_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-24_151220_normal_run/changed-files.txt
.ralph/runs/2026-07-24_151220_normal_run/codex-settings.md
.ralph/runs/2026-07-24_151220_normal_run/diff-limits-results.md
.ralph/runs/2026-07-24_151220_normal_run/evidence/task-state-role-mapping.md
.ralph/runs/2026-07-24_151220_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-24_151220_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-24_151220_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-24_151220_normal_run/evidence/terminal-logs/workflow-task-actions-red.log
.ralph/runs/2026-07-24_151220_normal_run/evidence/terminal-logs/workflow-task-appraisal-green.log
.ralph/runs/2026-07-24_151220_normal_run/evidence/terminal-logs/workflow-task-appraisal-red.log
.ralph/runs/2026-07-24_151220_normal_run/evidence/terminal-logs/workflow-task-dashboard-red.log
.ralph/runs/2026-07-24_151220_normal_run/evidence/terminal-logs/workflow-task-eight-types-red.log
.ralph/runs/2026-07-24_151220_normal_run/evidence/terminal-logs/workflow-task-focused-green.log
.ralph/runs/2026-07-24_151220_normal_run/evidence/terminal-logs/workflow-task-list-red.log
.ralph/runs/2026-07-24_151220_normal_run/evidence/terminal-logs/workflow-task-reconciliation-red.log
.ralph/runs/2026-07-24_151220_normal_run/evidence/terminal-logs/workflow-task-scheduler-red.log
.ralph/runs/2026-07-24_151220_normal_run/evidence/terminal-logs/workflow-task-schema-green.log
.ralph/runs/2026-07-24_151220_normal_run/execution-plan.md
.ralph/runs/2026-07-24_151220_normal_run/final-summary.md
.ralph/runs/2026-07-24_151220_normal_run/no-op-check-results.md
.ralph/runs/2026-07-24_151220_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-24_151220_normal_run/preflight-results.md
.ralph/runs/2026-07-24_151220_normal_run/prompt.md
.ralph/runs/2026-07-24_151220_normal_run/protected-paths-check.md
.ralph/runs/2026-07-24_151220_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-24_151220_normal_run/review-packet.md
.ralph/runs/2026-07-24_151220_normal_run/risk-assessment.md
.ralph/runs/2026-07-24_151220_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-24_151220_normal_run/slice-status-transition-check.md
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
sfpcl_credit/config/urls.py
sfpcl_credit/dashboard/services.py
sfpcl_credit/disbursements/modules/disbursement_initiation.py
sfpcl_credit/loans/modules/direct_repayment_posting.py
sfpcl_credit/loans/modules/subsidiary_deduction_reconciliation.py
sfpcl_credit/scheduler/services.py
sfpcl_credit/tests/test_dashboard_api.py
sfpcl_credit/tests/test_workflow_tasks.py
sfpcl_credit/workflows/events.py
sfpcl_credit/workflows/migrations/0002_workflow_tasks.py
sfpcl_credit/workflows/models.py
sfpcl_credit/workflows/task_views.py
sfpcl_credit/workflows/tasks.py
```
