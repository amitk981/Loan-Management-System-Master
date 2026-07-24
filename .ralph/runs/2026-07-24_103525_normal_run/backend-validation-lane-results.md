# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: backend root closure has no valid owner/contract test mapping
- Enforcement policy: selective
- Slice risk: medium
- Candidate completion ordinal: 343
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/closure/modules/loan_closure.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/dashboard/services.py`
- `sfpcl_credit/dashboard/views.py`
- `sfpcl_credit/tests/test_dashboard_api.py`

Impacted test labels:
- `sfpcl_credit.tests.test_dashboard_api`
- `sfpcl_credit.tests.test_archive_api`
- `sfpcl_credit.tests.test_auditor_epic_011_api`
- `sfpcl_credit.tests.test_closure_api`
- `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance`
- `sfpcl_credit.tests.test_noc_api`
- `sfpcl_credit.tests.test_security_return_api`
