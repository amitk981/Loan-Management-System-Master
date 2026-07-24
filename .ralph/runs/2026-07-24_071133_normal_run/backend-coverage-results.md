# backend-coverage Results

Command: "/Users/amitkallapa/LMS/scripts/ralph-parallel-backend-coverage.sh" "/Users/amitkallapa/LMS/.ralph/venv/bin/python" "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_071133_normal_run" "sfpcl_credit" "6" "85"

Creating test database for alias 'default'...
Found 1786 test(s).
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
System check identified no issues (0 silenced).
............................................................................................................................................................................................Catalogue seeded: 197 permissions, 20 roles, 8 teams, 272 role-permission links.
Catalogue seeded: 197 permissions, 20 roles, 8 teams, 272 role-permission links.
...............................................................................................................................................................................................................................................................................................................................................................................................................Catalogue seeded: 197 permissions, 20 roles, 8 teams, 272 role-permission links.
..................ssss....................ssssss.......................................................................................Catalogue seeded: 197 permissions, 20 roles, 8 teams, 272 role-permission links.
Catalogue seeded: 197 permissions, 20 roles, 8 teams, 272 role-permission links.
Catalogue seeded: 197 permissions, 20 roles, 8 teams, 272 role-permission links.
...Catalogue seeded: 197 permissions, 22 roles, 8 teams, 275 role-permission links.
Catalogue seeded: 197 permissions, 22 roles, 8 teams, 275 role-permission links.
Catalogue seeded: 197 permissions, 22 roles, 8 teams, 275 role-permission links.
.............................................................................................................................................................................................................................................................................................................................................................................................................................................................GLOBAL_SEARCH_INDEX_PLANS {'pan': '3 0 0 SEARCH members USING INDEX idx_members_pan_hash (pan_hash=?)', 'aadhaar': '3 0 0 SEARCH members USING INDEX idx_members_aadhaar_hash (aadhaar_hash=?)', 'aadhaar_last4': '3 0 0 SEARCH members USING INDEX members_aadhaar_last4_6253ff18 (aadhaar_last4=?)', 'share_count': '3 0 0 SEARCH members USING INDEX members_number_of_shares_4d7470ba (number_of_shares=?)', 'bank_last4': '3 0 0 SEARCH bank_accounts USING INDEX bank_accounts_account_number_last4_3bd9ef02 (account_number_last4=?)'}
Catalogue seeded: 197 permissions, 20 roles, 8 teams, 272 role-permission links.
............Catalogue seeded: 197 permissions, 20 roles, 8 teams, 272 role-permission links.
.Catalogue seeded: 197 permissions, 20 roles, 8 teams, 272 role-permission links.
...............................F
======================================================================
FAIL: test_request_status_authentication_validation_and_not_found_contracts (sfpcl_credit.tests.test_report_exports_api.ReportExportApiTests.test_request_status_authentication_validation_and_not_found_contracts)
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
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_071133_normal_run/sfpcl_credit/tests/test_report_exports_api.py", line 800, in test_request_status_authentication_validation_and_not_found_contracts
    self.assertIn("report_code", unsupported.json()["error"]["field_errors"])
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 1140, in assertIn
    self.fail(self._formatMessage(msg, standardMsg))
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 703, in fail
    raise self.failureException(msg)
    ^^^^^^^^^^^^^^^^^
AssertionError: 'report_code' not found in {'format': 'Must be one of csv, xlsx, pdf, json.'}

----------------------------------------------------------------------
Ran 1215 tests in 115.727s

FAILED (failures=1, skipped=10)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 80.061s
  Creating 'default' took 79.989s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.013s
  Cloning 'default' took 0.012s
  Cloning 'default' took 0.013s
  Cloning 'default' took 0.012s
Total database teardown took 0.022s
Total run took 196.432s

Duration milliseconds: 197177
Exit code: 1
