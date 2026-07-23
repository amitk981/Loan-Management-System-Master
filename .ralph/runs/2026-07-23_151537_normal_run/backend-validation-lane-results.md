# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: periodic full-suite checkpoint at completed slice 332
- Enforcement policy: selective
- Slice risk: high
- Candidate completion ordinal: 332
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/compliance/apps.py`
- `sfpcl_credit/compliance/modules/compliance_control_tracker.py`
- `sfpcl_credit/compliance/modules/kyc_review_tracker.py`
- `sfpcl_credit/compliance/modules/nbfc_principal_business_test.py`
- `sfpcl_credit/compliance/modules/section186_tracker.py`
- `sfpcl_credit/compliance/search_facade.py`
- `sfpcl_credit/identity/management/commands/seed_e2e_users.py`
- `sfpcl_credit/processes/global_search.py`
- `sfpcl_credit/tests/test_global_search_compliance.py`

Impacted test labels:
- `sfpcl_credit.tests.test_global_search_compliance`
- `sfpcl_credit.tests.test_compliance_api`
- `sfpcl_credit.tests.test_compliance_postgresql_acceptance`
- `sfpcl_credit.tests.test_compliance_task_engine`
- `sfpcl_credit.tests.test_kyc_review_api`
- `sfpcl_credit.tests.test_kyc_review_tracker`
- `sfpcl_credit.tests.test_statutory_trackers`
