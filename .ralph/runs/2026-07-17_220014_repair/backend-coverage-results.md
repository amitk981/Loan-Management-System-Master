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
..............................................................................................................Catalogue seeded: 184 permissions, 20 roles, 8 teams, 205 role-permission links.
Catalogue seeded: 184 permissions, 20 roles, 8 teams, 205 role-permission links.
...............................................................................................................................................................Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
multiprocessing.pool.RemoteTraceback: 
"""
Traceback (most recent call last):
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/backends/utils.py", line 105, in _execute
    return self.cursor.execute(sql, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/backends/sqlite3/base.py", line 329, in execute
    return super().execute(query, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sqlite3.OperationalError: no such column: disbursements.register_update_id

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 57, in testPartExecutor
    yield
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 623, in run
    self._callTestMethod(testMethod)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 579, in _callTestMethod
    if method() is not None:
       ^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_215313_normal_run/sfpcl_credit/tests/test_disbursement_initiation_api.py", line 370, in test_cfc_readiness_scope_rejects_initiation_without_real_bank_owner_manifest
    before = self.client.get(
             ^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/client.py", line 1049, in get
    response = super().get(path, data=data, secure=secure, headers=headers, **extra)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/client.py", line 465, in get
    return self.generic(
           ^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/client.py", line 617, in generic
    return self.request(**r)
           ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/client.py", line 1013, in request
    self.check_exception(response)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/client.py", line 743, in check_exception
    raise exc_value
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/handlers/exception.py", line 55, in inner
    response = get_response(request)
               ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/handlers/base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/views/decorators/http.py", line 64, in inner
    return func(request, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_215313_normal_run/sfpcl_credit/disbursements/views.py", line 34, in readiness
    data = evaluate(actor=actor, loan_account_id=loan_account_id)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_215313_normal_run/sfpcl_credit/disbursements/modules/disbursement_readiness.py", line 144, in evaluate
    result, _ = _evaluate(
                ^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_215313_normal_run/sfpcl_credit/disbursements/modules/disbursement_readiness.py", line 160, in _evaluate
    account = resolve_readiness_account(
              ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_215313_normal_run/sfpcl_credit/loans/modules/loan_account_lifecycle.py", line 242, in resolve_readiness_account
    and cfc_scope_resolver(actor_id=actor.pk, loan_account_id=account.pk)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_215313_normal_run/sfpcl_credit/disbursements/modules/disbursement_scope.py", line 10, in has_cfc_scope
    resolve_current_disbursement_evidence(loan_account_id=loan_account_id)
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_215313_normal_run/sfpcl_credit/disbursements/modules/current_disbursement_evidence.py", line 51, in resolve_current_disbursement_evidence
    rows = list(queryset.order_by("disbursement_id")[:2])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/models/query.py", line 400, in __iter__
    self._fetch_all()
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/models/query.py", line 1928, in _fetch_all
    self._result_cache = list(self._iterable_class(self))
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/models/query.py", line 91, in __iter__
    results = compiler.execute_sql(
              ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/models/sql/compiler.py", line 1562, in execute_sql
    cursor.execute(sql, params)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/backends/utils.py", line 79, in execute
    return self._execute_with_wrappers(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/backends/utils.py", line 92, in _execute_with_wrappers
    return executor(sql, params, many, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/backends/utils.py", line 100, in _execute
    with self.db.wrap_database_errors:
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/utils.py", line 91, in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/backends/utils.py", line 105, in _execute
    return self.cursor.execute(sql, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/backends/sqlite3/base.py", line 329, in execute
    return super().execute(query, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
django.db.utils.OperationalError: no such column: disbursements.register_update_id

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
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 99, in _addError
    result.addError(test, exc_info)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/runner.py", line 294, in addError
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

Duration milliseconds: 35283
Exit code: 1
