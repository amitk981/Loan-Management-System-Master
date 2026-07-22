# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: backend root defaults has no valid owner/contract test mapping
- Enforcement policy: selective
- Slice risk: medium
- Candidate completion ordinal: 319
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/defaults/migrations/0002_grace_period_assessment.py`
- `sfpcl_credit/defaults/models.py`
- `sfpcl_credit/defaults/modules/default_workflow.py`
- `sfpcl_credit/defaults/views.py`
- `sfpcl_credit/identity/catalogue.py`
- `sfpcl_credit/processes/tasks.py`
- `sfpcl_credit/scheduler/services.py`
- `sfpcl_credit/tests/test_default_grace_assessment_api.py`
- `sfpcl_credit/tests/test_default_recovery_postgresql_acceptance.py`

Impacted test labels:
- `sfpcl_credit.tests.test_default_grace_assessment_api`
- `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance`
- `sfpcl_credit.tests.test_default_case_opening_api`
