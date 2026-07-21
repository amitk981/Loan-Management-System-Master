# backend-coverage Results

Command: "/Users/amitkallapa/LMS/scripts/ralph-parallel-backend-coverage.sh" "/Users/amitkallapa/LMS/.ralph/venv/bin/python" "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_141242_normal_run" "sfpcl_credit" "6" "85"

Creating test database for alias 'default'...
Found 1550 test(s).
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
System check identified no issues (0 silenced).
.......................................................................................................................Catalogue seeded: 189 permissions, 20 roles, 8 teams, 225 role-permission links.
Catalogue seeded: 189 permissions, 20 roles, 8 teams, 225 role-permission links.
..............................................................................................................................................................................................................................................................................................................................................................................................................................Catalogue seeded: 189 permissions, 20 roles, 8 teams, 225 role-permission links.
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
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_141242_normal_run/sfpcl_credit/tests/test_dpd_monitoring_api.py", line 179, in test_bounded_active_portfolio_reports_each_outcome
    self.assertLessEqual(len(queries), 20)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 1265, in assertLessEqual
    self.fail(self._formatMessage(msg, standardMsg))
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 703, in fail
    raise self.failureException(msg)
    ^^^^^^^^^^^^^^^^^
AssertionError: 21 not less than or equal to 20

----------------------------------------------------------------------
Ran 548 tests in 38.056s

FAILED (failures=1)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 60.509s
  Creating 'default' took 60.428s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.012s
  Cloning 'default' took 0.014s
  Cloning 'default' took 0.014s
  Cloning 'default' took 0.017s
Total database teardown took 0.010s
Total run took 100.124s

Duration milliseconds: 100795
Exit code: 1
