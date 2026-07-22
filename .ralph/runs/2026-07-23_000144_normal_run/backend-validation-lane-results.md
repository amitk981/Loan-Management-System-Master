# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: backend root closure has no valid owner/contract test mapping
- Enforcement policy: selective
- Slice risk: medium
- Candidate completion ordinal: 327
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/closure/migrations/0004_archive_record.py`
- `sfpcl_credit/closure/models.py`
- `sfpcl_credit/closure/modules/loan_closure.py`
- `sfpcl_credit/closure/views.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/identity/catalogue.py`
- `sfpcl_credit/tests/test_archive_api.py`
- `sfpcl_credit/tests/test_default_recovery_postgresql_acceptance.py`

Impacted test labels:
- `sfpcl_credit.tests.test_archive_api`
- `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance`
- `sfpcl_credit.tests.test_closure_api`
- `sfpcl_credit.tests.test_noc_api`
- `sfpcl_credit.tests.test_security_return_api`
