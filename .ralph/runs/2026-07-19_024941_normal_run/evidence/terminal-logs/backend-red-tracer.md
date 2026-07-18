# Backend RED — sanctioned Loan Account 360 reads

Command:

`/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test sfpcl_credit.tests.test_loan_account_reads_api.LoanAccountReadApiTests.test_sanctioned_list_and_detail_are_exact_paginated_zero_write_projections -v 2`

Result: **failed as expected** (exit 1; 1 test run).

Key output:

```text
System check identified no issues (0 silenced).
test_sanctioned_list_and_detail_are_exact_paginated_zero_write_projections ... FAIL
AssertionError: 404 != 200
Ran 1 test in 0.032s
FAILED (failures=1)
```

The new public contract failed because `GET /api/v1/loan-accounts/` had no route or implementation.
