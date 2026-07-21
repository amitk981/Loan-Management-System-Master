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
.........................................................................................F
======================================================================
FAIL: test_final_accepted_crash_closes_exception_without_redispatch (sfpcl_credit.tests.test_communication_worker_runtime.CommunicationWorkerQueueTests.test_final_accepted_crash_closes_exception_without_redispatch)
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
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_141242_normal_run/sfpcl_credit/tests/test_communication_worker_runtime.py", line 936, in test_final_accepted_crash_closes_exception_without_redispatch
    self.assertIsNotNone(job.provider_external_message_id)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 1289, in assertIsNotNone
    self.fail(self._formatMessage(msg, standardMsg))
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 703, in fail
    raise self.failureException(msg)
    ^^^^^^^^^^^^^^^^^
AssertionError: unexpectedly None

----------------------------------------------------------------------
Ran 209 tests in 8.587s

FAILED (failures=1)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 58.272s
  Creating 'default' took 58.202s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.014s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.014s
  Cloning 'default' took 0.013s
Total database teardown took 0.002s
Total run took 67.606s

Duration milliseconds: 68244
Exit code: 1
