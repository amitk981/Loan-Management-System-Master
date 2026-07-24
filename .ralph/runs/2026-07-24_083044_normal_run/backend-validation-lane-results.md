# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: high-risk slice
- Enforcement policy: selective
- Slice risk: high
- Candidate completion ordinal: 342
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/compliance/migrations/0005_auditobservation.py`
- `sfpcl_credit/compliance/models.py`
- `sfpcl_credit/compliance/modules/audit_observation.py`
- `sfpcl_credit/compliance/views.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/identity/catalogue.py`
- `sfpcl_credit/tests/test_audit_observations_api.py`
- `sfpcl_credit/tests/test_auditor_epic_011_api.py`

Impacted test labels:
- `sfpcl_credit.tests.test_audit_observations_api`
- `sfpcl_credit.tests.test_auditor_epic_011_api`
- `sfpcl_credit.tests.test_compliance_api`
- `sfpcl_credit.tests.test_compliance_postgresql_acceptance`
- `sfpcl_credit.tests.test_compliance_task_engine`
- `sfpcl_credit.tests.test_global_search_compliance`
- `sfpcl_credit.tests.test_grievance_workflow`
- `sfpcl_credit.tests.test_kyc_review_api`
- `sfpcl_credit.tests.test_kyc_review_tracker`
- `sfpcl_credit.tests.test_report_api`
- `sfpcl_credit.tests.test_report_catalogue_api`
- `sfpcl_credit.tests.test_statutory_trackers`
