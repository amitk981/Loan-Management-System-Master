# Failure Summary

- Run: 2026-07-19_115845_repair
- Mode: repair
- Slice: 009L4-epic-009-canonical-read-and-bounded-pagination-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAIL: test_sap_owner_has_no_executable_finance_dependency (sfpcl_credit.tests.test_sap_customer_profile_repair.SapCustomerProfileRepairTests.test_sap_owner_has_no_executable_finance_dependency)
backend-coverage-results.md:FAILED (failures=1, skipped=82)
```

## Last 50 lines: backend-coverage-results.md

```
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 579, in _callTestMethod
    if method() is not None:
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_110722_normal_run/sfpcl_credit/tests/test_sap_customer_profile_repair.py", line 638, in test_sap_owner_has_no_executable_finance_dependency
    self.assertEqual(cycles, [], graph)
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
AssertionError: Lists differ: ['loans->disbursements', 'disbursements->loans'] != []

First list contains 2 additional elements.
First extra element 0:
'loans->disbursements'

- ['loans->disbursements', 'disbursements->loans']
+ [] : {'finance': {'sap_workflow'}, 'loans': {'sap_workflow', 'disbursements'}, 'sap_workflow': set(), 'disbursements': {'loans', 'sap_workflow'}}

----------------------------------------------------------------------
Ran 1288 tests in 543.406s

FAILED (failures=1, skipped=82)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 34.048s
  Creating 'default' took 33.992s
  Cloning 'default' took 0.008s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.008s
  Cloning 'default' took 0.007s
  Cloning 'default' took 0.017s
  Cloning 'default' took 0.007s
Total database teardown took 0.005s
Total run took 578.088s

Duration milliseconds: 578788
Exit code: 1
```

## Changed files (git status)

```
docs/working/API_CONTRACTS.md
sfpcl-lms/src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx
sfpcl_credit/disbursements/modules/disbursement_advice.py
sfpcl_credit/disbursements/modules/disbursement_authorisation.py
sfpcl_credit/disbursements/modules/disbursement_transfer_success.py
sfpcl_credit/disbursements/modules/post_transfer_evidence.py
sfpcl_credit/loans/modules/loan_account_lifecycle.py
sfpcl_credit/loans/modules/loan_account_read.py
sfpcl_credit/processes/disbursement_workspace.py
sfpcl_credit/processes/loan_account_360.py
sfpcl_credit/sap_workflow/modules/sap_customer_profile.py
sfpcl_credit/tests/test_loan_account_reads_api.py
.ralph/runs/2026-07-19_110722_normal_run/
.ralph/runs/2026-07-19_115845_repair/
```
