# Failure Summary

- Run: 2026-07-18_232234_normal_run
- Mode: normal_run
- Slice: 009H9C-communication-channel-interface-and-provider-evidence-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAIL: test_send_communication_creates_staff_notification_for_user_recipient (sfpcl_credit.tests.test_notifications_api.NotificationApiTests.test_send_communication_creates_staff_notification_for_user_recipient)
backend-coverage-results.md:FAILED (failures=1, skipped=80)
```

## Last 50 lines: backend-coverage-results.md

```
..Catalogue seeded: 184 permissions, 20 roles, 8 teams, 205 role-permission links.
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
..........................................................sssssss....................................ssssss.......................................................................................ssss.....ssssssssssss.......ssssss..sssssssssssssss.......ssssssss...............ssss........ssss.sssss..........................ssss.....sssss...................
======================================================================
FAIL: test_send_communication_creates_staff_notification_for_user_recipient (sfpcl_credit.tests.test_notifications_api.NotificationApiTests.test_send_communication_creates_staff_notification_for_user_recipient)
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
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_232234_normal_run/sfpcl_credit/tests/test_notifications_api.py", line 191, in test_send_communication_creates_staff_notification_for_user_recipient
    self.assertEqual(response.status_code, 200)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 873, in assertEqual
    assertion_func(first, second, msg=msg)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 866, in _baseAssertEqual
    raise self.failureException(msg)
    ^^^^^^^^^^^^^^^^^
AssertionError: 400 != 200

----------------------------------------------------------------------
Ran 1244 tests in 435.307s

FAILED (failures=1, skipped=80)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 30.825s
  Creating 'default' took 30.784s
  Cloning 'default' took 0.006s
  Cloning 'default' took 0.007s
  Cloning 'default' took 0.006s
  Cloning 'default' took 0.006s
  Cloning 'default' took 0.006s
  Cloning 'default' took 0.009s
Total database teardown took 0.011s
Total run took 466.732s

Duration milliseconds: 467291
Exit code: 1
```

## Changed files (git status)

```
docs/working/API_CONTRACTS.md
docs/working/digests/epic-009-sap-loan-account-disbursement.md
sfpcl_credit/communications/adapters.py
sfpcl_credit/communications/models.py
sfpcl_credit/communications/modules/communication_dispatcher.py
sfpcl_credit/communications/services.py
sfpcl_credit/config/settings.py
sfpcl_credit/processes/communication_delivery.py
sfpcl_credit/processes/disbursement_advice_delivery.py
sfpcl_credit/processes/tasks.py
sfpcl_credit/tests/test_communication_dispatcher_jobs.py
sfpcl_credit/tests/test_communication_job_migration.py
sfpcl_credit/tests/test_communication_worker_runtime.py
sfpcl_credit/tests/test_communications_api.py
sfpcl_credit/tests/test_disbursement_advice_api.py
.ralph/runs/2026-07-18_232234_normal_run/
sfpcl_credit/communications/migrations/0012_generic_provider_evidence.py
sfpcl_credit/tests/test_communication_channel_contract.py
```
