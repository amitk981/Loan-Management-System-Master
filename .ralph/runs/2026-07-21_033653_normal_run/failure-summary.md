# Failure Summary

- Run: 2026-07-21_033653_normal_run
- Mode: normal_run
- Slice: 010K-cfo-quarterly-mis
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAIL: test_source_bank_activation_retains_reviewable_reason_without_false_approval (sfpcl_credit.tests.test_disbursement_initiation_api.DisbursementInitiationApiTests.test_source_bank_activation_retains_reviewable_reason_without_false_approval)
backend-coverage-results.md:FAILED (failures=1, skipped=148)
```

## Last 50 lines: backend-coverage-results.md

```
...................sssssssCatalogue seeded: 189 permissions, 20 roles, 8 teams, 225 role-permission links.
Catalogue seeded: 189 permissions, 20 roles, 8 teams, 225 role-permission links.
....................................ssssss............................ssss.....ssssssssssss.....ssssss....sssssssssssssss.......ssssssss.....sss......................ssss...........ssssssss.sssss............sssssssssssssssssssssssssssssssssssssssssssssssssss.....sssss.ssss.........................
======================================================================
FAIL: test_source_bank_activation_retains_reviewable_reason_without_false_approval (sfpcl_credit.tests.test_disbursement_initiation_api.DisbursementInitiationApiTests.test_source_bank_activation_retains_reviewable_reason_without_false_approval)
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
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_033653_normal_run/sfpcl_credit/tests/test_disbursement_initiation_api.py", line 609, in test_source_bank_activation_retains_reviewable_reason_without_false_approval
    self.assertNotIn(forbidden, protected_surface)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 1147, in assertNotIn
    self.fail(self._formatMessage(msg, standardMsg))
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 703, in fail
    raise self.failureException(msg)
    ^^^^^^^^^^^^^^^^^
AssertionError: '2002' unexpectedly found in '{"activated_at": "2026-07-20T23:09:24.636253Z", "activated_by_user_id": "af601fe7-c339-42e2-88b4-a5c9ca4fb69f", "change_context": {"action": "config.changed", "actor_role_codes": ["senior_manager_finance"], "actor_team_codes": [], "actor_user_id": "af601fe7-c339-42e2-88b4-a5c9ca4fb69f", "change_kind": "activation", "ip_address": "192.0.2.44", "reason": "Move settlement routing to the verified operating account.", "reason_digest": "84cd92483b6a1b5fe7dd454b310827aff2d872b6511180183c6f80be3d0a2511", "request_id": "req-source-bank-reviewable", "user_agent": "governance-review/1.0"}, "change_context_digest": "d2737285a6b1e491c5348aef0268deacf0524155d777ae629056161ca25e703e", "governance_id": "919e16b1-1cd5-47cd-81c2-1da985f91915", "predecessor_governance_id": null, "reason_digest": "84cd92483b6a1b5fe7dd454b310827aff2d872b6511180183c6f80be3d0a2511", "request_id": "req-source-bank-reviewable", "source_bank_account_id": "3cec830a-7a85-498f-bfa5-27b8db03941f", "source_facts_digest": "a5e667c3fa05ec6d94dc2de234c3c3993391dcf1bc4a7f9270ffa0200237f0d1", "status": "active"}'

----------------------------------------------------------------------
Ran 1520 tests in 1276.524s

FAILED (failures=1, skipped=148)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 57.233s
  Creating 'default' took 57.171s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.010s
Total database teardown took 0.013s
Total run took 1334.495s

Duration milliseconds: 1335156
Exit code: 1
```

## Changed files (git status)

```
docs/working/API_CONTRACTS.md
docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md
sfpcl_credit/config/urls.py
sfpcl_credit/identity/catalogue.py
sfpcl_credit/monitoring/models.py
sfpcl_credit/monitoring/views.py
sfpcl_credit/tests/test_catalogue_seed.py
sfpcl_credit/tests/test_servicing_postgresql_acceptance.py
.ralph/runs/2026-07-21_033653_normal_run/
sfpcl_credit/monitoring/migrations/0004_quarterly_mis.py
sfpcl_credit/monitoring/modules/mis_exports.py
sfpcl_credit/monitoring/modules/quarterly_mis.py
sfpcl_credit/tests/test_quarterly_mis_api.py
```
