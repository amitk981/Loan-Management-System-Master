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
.................................................................................................................................................................................................................................................................................................................................................F
======================================================================
FAIL: test_sap_posting_requires_permission_reference_and_records_safe_audit_truth (sfpcl_credit.tests.test_direct_repayment_posting_api.DirectRepaymentPostingApiTests.test_sap_posting_requires_permission_reference_and_records_safe_audit_truth)
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
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_141242_normal_run/sfpcl_credit/tests/test_direct_repayment_posting_api.py", line 167, in test_sap_posting_requires_permission_reference_and_records_safe_audit_truth
    self.assertEqual(repeated.status_code, 409, repeated.content)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 873, in assertEqual
    assertion_func(first, second, msg=msg)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 866, in _baseAssertEqual
    raise self.failureException(msg)
    ^^^^^^^^^^^^^^^^^
AssertionError: 200 != 409 : b'{"success": true, "data": {"repayment_id": "83adecaa-776b-4019-afed-e24f5d92d877", "loan_account_id": "c1f220c0-11bb-4846-8b56-35c37ceaeda7", "repayment_source": "direct_farmer", "amount_received": "100000.00", "received_date": "2026-12-04", "payment_method": "rtgs", "bank_reference_number": "UTR-DIRECT-VALIDATION-001", "bank_statement_line_id": null, "statement_match_status": "not_linked", "allocation_status": "pending", "sap_posting": {"status": "posted", "due_date": "2026-12-07", "sap_entry_reference": "SAP-RCPT-123", "posted_at": "2026-12-02T10:00:00Z"}}, "meta": {"request_id": "req-repayment-posting-001", "timestamp": "2026-07-21T09:46:41.460003Z", "api_version": "v1"}}'

----------------------------------------------------------------------
Ran 457 tests in 18.912s

FAILED (failures=1)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 58.760s
  Creating 'default' took 58.695s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.013s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.010s
Total database teardown took 0.002s
Total run took 78.190s

Duration milliseconds: 78832
Exit code: 1
