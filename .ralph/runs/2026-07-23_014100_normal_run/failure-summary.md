# Failure Summary

- Run: 2026-07-23_014100_normal_run
- Mode: normal_run
- Slice: 011K-compliance-control-tracker-foundation
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=1, skipped=89)
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
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_014100_normal_run/sfpcl_credit/tests/test_credit_model_ownership_migration.py", line 45, in setUp
    self.identifiers = self._create_pre_move_rows(old_apps)
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_014100_normal_run/sfpcl_credit/tests/test_credit_model_ownership_migration.py", line 149, in _create_pre_move_rows
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
Ran 1536 tests in 905.232s

FAILED (errors=1, skipped=89)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 72.973s
  Creating 'default' took 72.896s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.012s
  Cloning 'default' took 0.013s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.015s
  Cloning 'default' took 0.015s
Total database teardown took 0.017s
Total run took 979.016s

Duration milliseconds: 979710
Exit code: 1
```

## Changed files (git status)

```
.ralph/runs/2026-07-23_014100_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-23_014100_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-23_014100_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-23_014100_normal_run/changed-files.txt
.ralph/runs/2026-07-23_014100_normal_run/codex-settings.md
.ralph/runs/2026-07-23_014100_normal_run/diff-limits-results.md
.ralph/runs/2026-07-23_014100_normal_run/evidence/terminal-logs/01-task-generation-red.txt
.ralph/runs/2026-07-23_014100_normal_run/evidence/terminal-logs/02-task-generation-green.txt
.ralph/runs/2026-07-23_014100_normal_run/evidence/terminal-logs/03-frequency-escalation-red-green.txt
.ralph/runs/2026-07-23_014100_normal_run/evidence/terminal-logs/04-evidence-api-red-green.txt
.ralph/runs/2026-07-23_014100_normal_run/evidence/terminal-logs/05-final-focused-gates.txt
.ralph/runs/2026-07-23_014100_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-23_014100_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-23_014100_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-23_014100_normal_run/execution-plan.md
.ralph/runs/2026-07-23_014100_normal_run/final-summary.md
.ralph/runs/2026-07-23_014100_normal_run/no-op-check-results.md
.ralph/runs/2026-07-23_014100_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-23_014100_normal_run/preflight-results.md
.ralph/runs/2026-07-23_014100_normal_run/prompt.md
.ralph/runs/2026-07-23_014100_normal_run/protected-paths-check.md
.ralph/runs/2026-07-23_014100_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-23_014100_normal_run/review-packet.md
.ralph/runs/2026-07-23_014100_normal_run/risk-assessment.md
.ralph/runs/2026-07-23_014100_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-23_014100_normal_run/slice-status-transition-check.md
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
sfpcl_credit/closure/compliance_evidence_facade.py
sfpcl_credit/compliance/__init__.py
sfpcl_credit/compliance/apps.py
sfpcl_credit/compliance/catalogue.py
sfpcl_credit/compliance/migrations/0001_initial.py
sfpcl_credit/compliance/migrations/__init__.py
sfpcl_credit/compliance/models.py
sfpcl_credit/compliance/modules/__init__.py
sfpcl_credit/compliance/modules/compliance_control_tracker.py
sfpcl_credit/compliance/modules/compliance_task_engine.py
sfpcl_credit/compliance/views.py
sfpcl_credit/config/settings.py
sfpcl_credit/config/urls.py
sfpcl_credit/identity/catalogue.py
sfpcl_credit/legal_documents/compliance_evidence_facade.py
sfpcl_credit/recovery/compliance_evidence_facade.py
sfpcl_credit/tests/test_compliance_api.py
sfpcl_credit/tests/test_compliance_postgresql_acceptance.py
sfpcl_credit/tests/test_compliance_task_engine.py
```
