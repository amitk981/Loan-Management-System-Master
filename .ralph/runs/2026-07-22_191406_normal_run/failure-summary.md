# Failure Summary

- Run: 2026-07-22_191406_normal_run
- Mode: normal_run
- Slice: 011G-closure-readiness
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=1)
```

## Last 50 lines: backend-coverage-results.md

```
.......................................................................................................................Catalogue seeded: 189 permissions, 20 roles, 8 teams, 235 role-permission links.
Catalogue seeded: 189 permissions, 20 roles, 8 teams, 235 role-permission links.
............................................................................................................................................................................................................................................................................................................................................................E
======================================================================
ERROR: test_early_paid_closed_foreign_and_unauthorised_assessments_are_rejected (sfpcl_credit.tests.test_default_grace_assessment_api.DefaultGraceAssessmentApiTests.test_early_paid_closed_foreign_and_unauthorised_assessments_are_rejected)
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
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_191406_normal_run/sfpcl_credit/tests/test_default_grace_assessment_api.py", line 451, in test_early_paid_closed_foreign_and_unauthorised_assessments_are_rejected
    type(self.account).objects.filter(pk=self.account.pk).update(
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_191406_normal_run/sfpcl_credit/loans/models.py", line 44, in update
    self._lock_and_reject_closed()
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_191406_normal_run/sfpcl_credit/loans/models.py", line 38, in _lock_and_reject_closed
    raise ValidationError(
    ^^^^^^^^^^^^^^^^^
django.core.exceptions.ValidationError: {'loan_account': ['Closed loan accounts are read-only.']}

----------------------------------------------------------------------
Ran 468 tests in 21.401s

FAILED (errors=1)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 66.728s
  Creating 'default' took 66.667s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.015s
Total database teardown took 0.002s
Total run took 88.972s

Duration milliseconds: 89578
Exit code: 1
```

## Changed files (git status)

```
.ralph/runs/2026-07-22_191406_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-22_191406_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-22_191406_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-22_191406_normal_run/changed-files.txt
.ralph/runs/2026-07-22_191406_normal_run/codex-settings.md
.ralph/runs/2026-07-22_191406_normal_run/diff-limits-results.md
.ralph/runs/2026-07-22_191406_normal_run/evidence/behavior-matrix.md
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/01-readiness-red.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/02-readiness-green.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/03-close-red.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/04-close-green.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/05-closure-focused.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/06-closure-focused-green.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/07-closed-mutation-red.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/08-closed-mutation-green.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/09-closure-and-postgres-label.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/10-postgresql-acceptance-first.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/11-postgresql-acceptance-green.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/12-postgresql-acceptance-second.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/13-django-check-migrations.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/14-focused-reverse-consumers.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/15-closure-post-review.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/16-closure-post-review-green.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/17-postgresql-post-review-first.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/18-postgresql-final-first.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/19-postgresql-final-second.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/20-final-focused-reverse-consumers.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/21-repaired-focused-consumers.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/22-final-static-checks.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/23-lock-safe-focused.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/24-lock-safe-postgresql-first.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/25-lock-safe-postgresql-second.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/26-final-static-checks.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-22_191406_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-22_191406_normal_run/execution-plan.md
.ralph/runs/2026-07-22_191406_normal_run/final-summary.md
.ralph/runs/2026-07-22_191406_normal_run/no-op-check-results.md
.ralph/runs/2026-07-22_191406_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-22_191406_normal_run/postgresql-acceptance-results.md
.ralph/runs/2026-07-22_191406_normal_run/preflight-results.md
.ralph/runs/2026-07-22_191406_normal_run/prompt.md
.ralph/runs/2026-07-22_191406_normal_run/protected-paths-check.md
.ralph/runs/2026-07-22_191406_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-22_191406_normal_run/review-packet.md
.ralph/runs/2026-07-22_191406_normal_run/risk-assessment.md
.ralph/runs/2026-07-22_191406_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-22_191406_normal_run/slice-status-transition-check.md
.ralph/runs/2026-07-22_191406_normal_run/test-results.md
docs/working/API_CONTRACTS.md
sfpcl_credit/closure/__init__.py
sfpcl_credit/closure/apps.py
sfpcl_credit/closure/migrations/0001_initial.py
sfpcl_credit/closure/migrations/__init__.py
sfpcl_credit/closure/models.py
sfpcl_credit/closure/modules/__init__.py
sfpcl_credit/closure/modules/loan_closure.py
sfpcl_credit/closure/views.py
sfpcl_credit/config/settings.py
sfpcl_credit/config/urls.py
sfpcl_credit/loans/models.py
sfpcl_credit/tests/test_closure_api.py
sfpcl_credit/tests/test_default_recovery_postgresql_acceptance.py
sfpcl_credit/tests/test_direct_repayment_posting_api.py
```
