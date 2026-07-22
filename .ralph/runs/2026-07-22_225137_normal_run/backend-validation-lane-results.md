# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: high-risk slice
- Enforcement policy: selective
- Slice risk: high
- Candidate completion ordinal: 326
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/closure/migrations/0003_security_return_tracking.py`
- `sfpcl_credit/closure/models.py`
- `sfpcl_credit/closure/modules/security_return.py`
- `sfpcl_credit/closure/views.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/security_instruments/modules/release_tracking.py`
- `sfpcl_credit/tests/test_default_recovery_postgresql_acceptance.py`
- `sfpcl_credit/tests/test_security_return_api.py`

Impacted test labels:
- `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance`
- `sfpcl_credit.tests.test_security_return_api`
- `sfpcl_credit.tests.test_closure_api`
- `sfpcl_credit.tests.test_noc_api`
