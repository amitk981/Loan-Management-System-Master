# backend-coverage Results

Command: "/Users/amitkallapa/LMS/scripts/ralph-parallel-backend-coverage.sh" "/Users/amitkallapa/LMS/.ralph/venv/bin/python" "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_041849_normal_run" "sfpcl_credit" "6" "85"

Creating test database for alias 'default'...
Found 1770 test(s).
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
System check identified no issues (0 silenced).
............................................................F
======================================================================
FAIL: test_production_code_does_not_use_legacy_permission_denied_literal (sfpcl_credit.tests.test_api_contract_harness.ApiContractHarnessUnitTests.test_production_code_does_not_use_legacy_permission_denied_literal)
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
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_041849_normal_run/sfpcl_credit/tests/test_api_contract_harness.py", line 42, in test_production_code_does_not_use_legacy_permission_denied_literal
    self.assertEqual(offenders, [], f"legacy permission literals: {offenders}")
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 873, in assertEqual
    assertion_func(first, second, msg=msg)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 1079, in assertListEqual
    self.assertSequenceEqual(list1, list2, msg, seq_type=list)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 1061, in assertSequenceEqual
    self.fail(msg)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 703, in fail
    raise self.failureException(msg)
    ^^^^^^^^^^^^^^^^^
AssertionError: Lists differ: ['reports/modules/report_export.py'] != []

First list contains 1 additional elements.
First extra element 0:
'reports/modules/report_export.py'

- ['reports/modules/report_export.py']
+ [] : legacy permission literals: ['reports/modules/report_export.py']

----------------------------------------------------------------------
Ran 61 tests in 2.207s

FAILED (failures=1)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 79.236s
  Creating 'default' took 79.159s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.012s
  Cloning 'default' took 0.013s
  Cloning 'default' took 0.014s
  Cloning 'default' took 0.013s
  Cloning 'default' took 0.014s
Total database teardown took 0.002s
Total run took 82.321s

Duration milliseconds: 82997
Exit code: 1
