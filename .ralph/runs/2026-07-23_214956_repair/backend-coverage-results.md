# backend-coverage Results

Command: "/Users/amitkallapa/LMS/scripts/ralph-parallel-backend-coverage.sh" "/Users/amitkallapa/LMS/.ralph/venv/bin/python" "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_210407_normal_run" "sfpcl_credit" "6" "85"

Creating test database for alias 'default'...
Found 1728 test(s).
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
Cloning test database for alias 'default'...
System check identified no issues (0 silenced).
...................................................................................................................................................................................Catalogue seeded: 195 permissions, 20 roles, 8 teams, 272 role-permission links.
Catalogue seeded: 195 permissions, 20 roles, 8 teams, 272 role-permission links.
...............................................................................................................................................................................................................................................................................................................................................................................................................Catalogue seeded: 195 permissions, 20 roles, 8 teams, 272 role-permission links.
..................ssss....................ssssss...............................E
======================================================================
ERROR: test_compliance_cfo_cs_and_auditor_permission_matrix (sfpcl_credit.tests.test_global_search_compliance.GlobalSearchComplianceTests.test_compliance_cfo_cs_and_auditor_permission_matrix) [<object object at 0x107e4a650>] (role='internal_auditor')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 57, in testPartExecutor
    yield
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 538, in subTest
    yield
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_210407_normal_run/sfpcl_credit/tests/test_global_search_compliance.py", line 377, in test_compliance_cfo_cs_and_auditor_permission_matrix
    cards = search_compliance_records(
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_210407_normal_run/sfpcl_credit/compliance/search_facade.py", line 22, in search_compliance_records
    list(compliance_control_tracker.search_controls(actor=actor, search=search))
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_210407_normal_run/sfpcl_credit/compliance/modules/compliance_control_tracker.py", line 110, in search_controls
    require(actor, "compliance.control.read")
      ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_210407_normal_run/sfpcl_credit/compliance/modules/compliance_control_tracker.py", line 41, in require
    require_auditor_scope(actor)
      ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_210407_normal_run/sfpcl_credit/compliance/modules/compliance_control_tracker.py", line 52, in require_auditor_scope
    raise ComplianceDenied()
    ^^^^^^^^^^^^^^^^^
sfpcl_credit.compliance.modules.compliance_control_tracker.ComplianceDenied

----------------------------------------------------------------------
Ran 658 tests in 53.243s

FAILED (errors=1, skipped=10)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 79.165s
  Creating 'default' took 79.060s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.019s
  Cloning 'default' took 0.021s
  Cloning 'default' took 0.024s
  Cloning 'default' took 0.020s
Total database teardown took 0.002s
Total run took 133.193s

Duration milliseconds: 133945
Exit code: 1
