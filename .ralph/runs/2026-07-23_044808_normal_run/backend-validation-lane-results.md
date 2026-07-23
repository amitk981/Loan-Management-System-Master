# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: backend root compliance has no valid owner/contract test mapping
- Enforcement policy: selective
- Slice risk: medium
- Candidate completion ordinal: 329
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/compliance/migrations/0002_statutory_trackers.py`
- `sfpcl_credit/compliance/models.py`
- `sfpcl_credit/compliance/modules/nbfc_principal_business_test.py`
- `sfpcl_credit/compliance/modules/section186_tracker.py`
- `sfpcl_credit/compliance/views.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/identity/catalogue.py`
- `sfpcl_credit/tests/test_catalogue_seed.py`
- `sfpcl_credit/tests/test_compliance_postgresql_acceptance.py`
- `sfpcl_credit/tests/test_statutory_trackers.py`

Impacted test labels:
- `sfpcl_credit.tests.test_catalogue_seed`
- `sfpcl_credit.tests.test_compliance_postgresql_acceptance`
- `sfpcl_credit.tests.test_statutory_trackers`
- `sfpcl_credit.tests.test_compliance_api`
- `sfpcl_credit.tests.test_compliance_task_engine`
