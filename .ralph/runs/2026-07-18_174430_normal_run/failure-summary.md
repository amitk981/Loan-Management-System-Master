# Failure Summary

- Run: 2026-07-18_174430_normal_run
- Mode: normal_run
- Slice: 009H7-communications-dispatcher-interface-and-idempotency-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAIL: test_send_communication_creates_staff_notification_for_user_recipient (sfpcl_credit.tests.test_notifications_api.NotificationApiTests.test_send_communication_creates_staff_notification_for_user_recipient)
backend-coverage-results.md:FAILED (failures=1, skipped=68)
risk-assessment.md:Failure could duplicate a borrower message, falsely mark an advice sent, strand a queued job, or
```

## Last 50 lines: backend-coverage-results.md

```
.........Portal E2E fixture seeded for e2e.portal@sfpcl.example: LO000008L4, LO000008L4-R.
Portal E2E fixture already exists.
...................................................sssssss....................................ssssss.......................................................................................ssss.....ssssss.......sssssssssssssss.......ssssssss..........................ssss........ssss.sssss............ssss.....sssss...................
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
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_174430_normal_run/sfpcl_credit/tests/test_notifications_api.py", line 188, in test_send_communication_creates_staff_notification_for_user_recipient
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
Ran 1191 tests in 435.101s

FAILED (failures=1, skipped=68)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 30.104s
  Creating 'default' took 30.056s
  Cloning 'default' took 0.006s
  Cloning 'default' took 0.006s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.009s
Total database teardown took 0.009s
Total run took 465.686s

Duration milliseconds: 466275
Exit code: 1
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/009H7-communications-dispatcher-interface-and-idempotency-closure.md
docs/working/API_CONTRACTS.md
docs/working/HANDOFF.md
docs/working/digests/epic-009-sap-loan-account-disbursement.md
sfpcl_credit/communications/adapters.py
sfpcl_credit/communications/models.py
sfpcl_credit/communications/modules/communication_dispatcher.py
sfpcl_credit/communications/services.py
sfpcl_credit/communications/views.py
sfpcl_credit/disbursements/modules/disbursement_advice.py
sfpcl_credit/disbursements/modules/disbursement_workflow.py
sfpcl_credit/disbursements/views.py
sfpcl_credit/processes/disbursement_advice_delivery.py
sfpcl_credit/processes/tasks.py
sfpcl_credit/tests/test_communication_advice_persistence.py
sfpcl_credit/tests/test_communication_dispatcher_jobs.py
sfpcl_credit/tests/test_communications_api.py
sfpcl_credit/tests/test_disbursement_advice_api.py
.ralph/runs/2026-07-18_174430_normal_run/
sfpcl_credit/communications/migrations/0009_generic_delivery_job_identity.py
sfpcl_credit/processes/communication_delivery.py
sfpcl_credit/tests/test_communication_job_migration.py
```
