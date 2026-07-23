# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: high-risk slice
- Enforcement policy: selective
- Slice risk: high
- Candidate completion ordinal: 330
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/compliance/migrations/0003_kyc_review_tracker.py`
- `sfpcl_credit/compliance/models.py`
- `sfpcl_credit/compliance/modules/kyc_review_tracker.py`
- `sfpcl_credit/compliance/views.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/tests/test_compliance_postgresql_acceptance.py`
- `sfpcl_credit/tests/test_kyc_review_api.py`
- `sfpcl_credit/tests/test_kyc_review_tracker.py`

Impacted test labels:
- `sfpcl_credit.tests.test_compliance_postgresql_acceptance`
- `sfpcl_credit.tests.test_kyc_review_api`
- `sfpcl_credit.tests.test_kyc_review_tracker`
- `sfpcl_credit.tests.test_compliance_api`
- `sfpcl_credit.tests.test_compliance_task_engine`
- `sfpcl_credit.tests.test_statutory_trackers`
