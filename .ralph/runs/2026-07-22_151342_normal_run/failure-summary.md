# Failure Summary

- Run: 2026-07-22_151342_normal_run
- Mode: normal_run
- Slice: 011E-recovery-decision-approval
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=1, skipped=95)
```

## Last 50 lines: backend-coverage-results.md

```
    ^^^^^^^^^^^^^^^^^
KeyError: 'eligibilityassessment'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 57, in testPartExecutor
    yield
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 619, in run
    self._callSetUp()
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 576, in _callSetUp
    self.setUp()
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_151342_normal_run/sfpcl_credit/tests/test_credit_model_ownership_migration.py", line 43, in setUp
    self.identifiers = self._create_pre_move_rows(old_apps)
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_151342_normal_run/sfpcl_credit/tests/test_credit_model_ownership_migration.py", line 147, in _create_pre_move_rows
    EligibilityAssessment = old_apps.get_model("applications", "EligibilityAssessment")
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/apps/registry.py", line 213, in get_model
    return app_config.get_model(model_name, require_ready=require_ready)
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/apps/config.py", line 237, in get_model
    raise LookupError(
    ^^^^^^^^^^^^^^^^^
LookupError: App 'applications' doesn't have a 'EligibilityAssessment' model.

----------------------------------------------------------------------
Ran 1512 tests in 782.244s

FAILED (errors=1, skipped=95)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 63.034s
  Creating 'default' took 62.979s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.009s
Total database teardown took 0.009s
Total run took 846.034s

Duration milliseconds: 846733
Exit code: 1
```

## Changed files (git status)

```
.ralph/runs/2026-07-22_151342_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-22_151342_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-22_151342_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-22_151342_normal_run/changed-files.txt
.ralph/runs/2026-07-22_151342_normal_run/codex-settings.md
.ralph/runs/2026-07-22_151342_normal_run/diff-limits-results.md
.ralph/runs/2026-07-22_151342_normal_run/evidence/api-responses/recovery-decision-approved.json
.ralph/runs/2026-07-22_151342_normal_run/evidence/terminal-logs/06-postgresql-five-race-green.txt
.ralph/runs/2026-07-22_151342_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-22_151342_normal_run/evidence/terminal-logs/focused-validation.md
.ralph/runs/2026-07-22_151342_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-22_151342_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-22_151342_normal_run/evidence/terminal-logs/permissions-check.md
.ralph/runs/2026-07-22_151342_normal_run/evidence/terminal-logs/tdd-red-green.md
.ralph/runs/2026-07-22_151342_normal_run/execution-plan.md
.ralph/runs/2026-07-22_151342_normal_run/final-summary.md
.ralph/runs/2026-07-22_151342_normal_run/no-op-check-results.md
.ralph/runs/2026-07-22_151342_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-22_151342_normal_run/preflight-results.md
.ralph/runs/2026-07-22_151342_normal_run/prompt.md
.ralph/runs/2026-07-22_151342_normal_run/protected-paths-check.md
.ralph/runs/2026-07-22_151342_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-22_151342_normal_run/review-packet.md
.ralph/runs/2026-07-22_151342_normal_run/risk-assessment.md
.ralph/runs/2026-07-22_151342_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-22_151342_normal_run/slice-status-transition-check.md
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
sfpcl_credit/approvals/modules/approval_actions.py
sfpcl_credit/approvals/modules/approval_case_engine.py
sfpcl_credit/approvals/modules/recovery_handoff.py
sfpcl_credit/config/settings.py
sfpcl_credit/config/urls.py
sfpcl_credit/recovery/apps.py
sfpcl_credit/recovery/migrations/0001_initial.py
sfpcl_credit/recovery/migrations/__init__.py
sfpcl_credit/recovery/models.py
sfpcl_credit/recovery/modules/recovery_decision.py
sfpcl_credit/recovery/views.py
sfpcl_credit/tests/test_default_recovery_postgresql_acceptance.py
sfpcl_credit/tests/test_non_payment_note_workflow_api.py
sfpcl_credit/tests/test_recovery_decision_api.py
```
