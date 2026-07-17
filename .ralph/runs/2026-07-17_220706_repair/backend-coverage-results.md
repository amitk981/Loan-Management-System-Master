# backend-coverage Results

Command: "/Users/amitkallapa/LMS/scripts/ralph-parallel-backend-coverage.sh" "/Users/amitkallapa/LMS/.ralph/venv/bin/python" "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_215313_normal_run" "sfpcl_credit" "6" "85"

Creating test database for alias 'default'...
Found 1117 test(s).
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
System check identified no issues (0 silenced).
..............................................................................................................Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
multiprocessing.pool.RemoteTraceback: 
"""
Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 57, in testPartExecutor
    yield
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 623, in run
    self._callTestMethod(testMethod)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 579, in _callTestMethod
    if method() is not None:
       ^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_215313_normal_run/sfpcl_credit/tests/test_approval_case_routing_api.py", line 5331, in test_detail_is_unchanged_when_live_configuration_rows_change
    self.assertEqual(second, first)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 873, in assertEqual
    assertion_func(first, second, msg=msg)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 1172, in assertDictEqual
    self.fail(self._formatMessage(msg, standardMsg))
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 703, in fail
    raise self.failureException(msg)
AssertionError: {'app[5832 chars]ds': 2, 'display': '0m'}}, 'available_actions'[579 chars]e'}]} != {'app[5832 chars]ds': 1, 'display': '0m'}}, 'available_actions'[579 chars]e'}]}
Diff is 10676 characters long. Set self.maxDiff to None to see it.

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/multiprocessing/pool.py", line 125, in worker
    result = (True, func(*args, **kwds))
                    ^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/runner.py", line 454, in _run_subsuite
    result = runner.run(subsuite)
             ^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/runner.py", line 369, in run
    test(result)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/suite.py", line 84, in __call__
    return self.run(*args, **kwds)
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/suite.py", line 122, in run
    test(result)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/testcases.py", line 258, in __call__
    self._setup_and_call(result)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/testcases.py", line 293, in _setup_and_call
    super().__call__(result)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 678, in __call__
    return self.run(*args, **kwds)
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 622, in run
    with outcome.testPartExecutor(self):
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/contextlib.py", line 155, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 74, in testPartExecutor
    _addError(self.result, test_case, exc_info)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 97, in _addError
    result.addFailure(test, exc_info)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/runner.py", line 299, in addFailure
    self.check_picklable(test, err)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/runner.py", line 215, in check_picklable
    self._confirm_picklable(err)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/runner.py", line 185, in _confirm_picklable
    pickle.loads(pickle.dumps(obj))
                 ^^^^^^^^^^^^^^^^^
TypeError: cannot pickle 'traceback' object
"""

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_215313_normal_run/sfpcl_credit/manage.py", line 17, in <module>
    main()
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_215313_normal_run/sfpcl_credit/manage.py", line 13, in main
    execute_from_command_line(sys.argv)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/__init__.py", line 442, in execute_from_command_line
    utility.execute()
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/__init__.py", line 436, in execute
    self.fetch_command(subcommand).run_from_argv(self.argv)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/commands/test.py", line 24, in run_from_argv
    super().run_from_argv(argv)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/base.py", line 413, in run_from_argv
    self.execute(*args, **cmd_options)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/base.py", line 459, in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/commands/test.py", line 68, in handle
    failures = test_runner.run_tests(test_labels)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/runner.py", line 1068, in run_tests
    result = self.run_suite(suite)
             ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/runner.py", line 995, in run_suite
    return runner.run(suite)
           ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/runner.py", line 217, in run
    test(result)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/suite.py", line 84, in __call__
    return self.run(*args, **kwds)
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/runner.py", line 541, in run
    subsuite_index, events = test_results.next(timeout=0.1)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/multiprocessing/pool.py", line 873, in next
    raise value
TypeError: cannot pickle 'traceback' object

Duration milliseconds: 31117
Exit code: 1
