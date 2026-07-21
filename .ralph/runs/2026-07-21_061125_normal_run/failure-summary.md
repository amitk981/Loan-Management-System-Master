# Failure Summary

- Run: 2026-07-21_061125_normal_run
- Mode: normal_run
- Slice: 010K3-servicing-as-of-owner-boundary-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAIL: test_bounded_active_portfolio_reports_each_outcome (sfpcl_credit.tests.test_dpd_monitoring_api.DpdMonitoringApiTests.test_bounded_active_portfolio_reports_each_outcome)
backend-coverage-results.md:FAILED (failures=1, skipped=153)
```

## Last 50 lines: backend-coverage-results.md

```
Catalogue seeded: 189 permissions, 20 roles, 8 teams, 225 role-permission links.
Catalogue seeded: 189 permissions, 20 roles, 8 teams, 225 role-permission links.
.......................sssssss.........................................ssssss....................ssss.....ssssssssssss.....ssssss....sssssssssssssss.......ssssssss.....sss......................ssss...........ssssssss.sssss............ssssssssssssssssssssssssssssssssssssssssssssssssssssssss.....sssss.ssss.........................
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
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_061125_normal_run/sfpcl_credit/tests/test_dpd_monitoring_api.py", line 179, in test_bounded_active_portfolio_reports_each_outcome
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
Ran 1530 tests in 1350.518s

FAILED (failures=1, skipped=153)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 59.007s
  Creating 'default' took 58.907s
  Cloning 'default' took 0.016s
  Cloning 'default' took 0.025s
  Cloning 'default' took 0.014s
  Cloning 'default' took 0.016s
  Cloning 'default' took 0.016s
  Cloning 'default' took 0.013s
Total database teardown took 0.031s
Total run took 1410.381s

Duration milliseconds: 1411705
Exit code: 1
```

## Changed files (git status)

```
docs/working/API_CONTRACTS.md
sfpcl_credit/communications/modules/communication_dispatcher.py
sfpcl_credit/loans/modules/dpd_source_decision.py
sfpcl_credit/monitoring/models.py
sfpcl_credit/monitoring/modules/dpd_monitoring.py
sfpcl_credit/monitoring/modules/quarterly_mis.py
sfpcl_credit/monitoring/modules/reminder_engine.py
sfpcl_credit/processes/communication_delivery.py
sfpcl_credit/tests/test_dpd_integrity_closure.py
sfpcl_credit/tests/test_servicing_postgresql_acceptance.py
.ralph/runs/2026-07-21_061125_normal_run/
sfpcl_credit/monitoring/migrations/0005_servicing_as_of_owner_boundary.py
sfpcl_credit/tests/test_servicing_as_of_owner_boundary.py
```
