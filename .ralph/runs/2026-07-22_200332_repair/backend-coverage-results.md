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
........................................................................................................................................................................................................................................................................................................................................................................................................................................................Catalogue seeded: 189 permissions, 20 roles, 8 teams, 235 role-permission links.
..............F
======================================================================
FAIL: test_bounded_active_portfolio_reports_each_outcome (sfpcl_credit.tests.test_dpd_monitoring_api.DpdMonitoringApiTests.test_bounded_active_portfolio_reports_each_outcome)
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
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_191406_normal_run/sfpcl_credit/tests/test_dpd_monitoring_api.py", line 220, in test_bounded_active_portfolio_reports_each_outcome
    self.assertLessEqual(len(queries), 20)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 1265, in assertLessEqual
    self.fail(self._formatMessage(msg, standardMsg))
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 703, in fail
    raise self.failureException(msg)
    ^^^^^^^^^^^^^^^^^
AssertionError: 23 not less than or equal to 20

----------------------------------------------------------------------
Ran 574 tests in 37.366s

FAILED (failures=1)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 64.522s
  Creating 'default' took 64.460s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.014s
Total database teardown took 0.002s
Total run took 102.414s

Duration milliseconds: 103036
Exit code: 1
