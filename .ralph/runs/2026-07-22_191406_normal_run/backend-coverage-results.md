# backend-coverage Results

Command: "/Users/amitkallapa/LMS/scripts/ralph-parallel-backend-coverage.sh" "/Users/amitkallapa/LMS/.ralph/venv/bin/python" "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_191406_normal_run" "sfpcl_credit" "6" "85"

Creating test database for alias 'default'...
Found 1637 test(s).
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
System check identified no issues (0 silenced).
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
