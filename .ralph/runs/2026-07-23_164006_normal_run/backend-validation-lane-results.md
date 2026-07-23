# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: backend root compliance has no valid owner/contract test mapping
- Enforcement policy: selective
- Slice risk: medium
- Candidate completion ordinal: 333
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/compliance/migrations/0004_grievance_grievancedocument_and_more.py`
- `sfpcl_credit/compliance/models.py`
- `sfpcl_credit/compliance/modules/compliance_task_engine.py`
- `sfpcl_credit/compliance/modules/grievance_workflow.py`
- `sfpcl_credit/compliance/views.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/identity/catalogue.py`
- `sfpcl_credit/tests/test_compliance_postgresql_acceptance.py`
- `sfpcl_credit/tests/test_grievance_workflow.py`

Impacted test labels:
- `sfpcl_credit.tests.test_compliance_postgresql_acceptance`
- `sfpcl_credit.tests.test_grievance_workflow`
- `sfpcl_credit.tests.test_compliance_api`
- `sfpcl_credit.tests.test_compliance_task_engine`
- `sfpcl_credit.tests.test_global_search_compliance`
- `sfpcl_credit.tests.test_kyc_review_api`
- `sfpcl_credit.tests.test_kyc_review_tracker`
- `sfpcl_credit.tests.test_statutory_trackers`
