# Failure Summary

- Run: 2026-07-18_095146_normal_run
- Mode: normal_run
- Slice: 009G4-legal-checklist-migration-ownership-anchor
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=2, skipped=62)
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
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_095146_normal_run/sfpcl_credit/tests/test_credit_model_ownership_migration.py", line 37, in setUp
    self.identifiers = self._create_pre_move_rows(old_apps)
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_095146_normal_run/sfpcl_credit/tests/test_credit_model_ownership_migration.py", line 141, in _create_pre_move_rows
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
Ran 1134 tests in 357.866s

FAILED (errors=2, skipped=62)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 27.591s
  Creating 'default' took 27.549s
  Cloning 'default' took 0.006s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.007s
  Cloning 'default' took 0.007s
  Cloning 'default' took 0.007s
  Cloning 'default' took 0.007s
Total database teardown took 0.005s
Total run took 386.011s

Duration milliseconds: 386509
Exit code: 1
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/009G4-legal-checklist-migration-ownership-anchor.md
docs/working/HANDOFF.md
docs/working/digests/epic-009-sap-loan-account-disbursement.md
sfpcl_credit/tests/test_legal_checklist_migration_anchor.py
.ralph/runs/2026-07-18_095146_normal_run/
sfpcl_credit/legal_documents/migrations/0015_checklist_constraint_state_owner_anchor.py
sfpcl_credit/shared/migration_state_guard.py
```
