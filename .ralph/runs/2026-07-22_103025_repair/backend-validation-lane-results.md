# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: backend root defaults has no valid owner/contract test mapping
- Enforcement policy: selective
- Slice risk: medium
- Candidate completion ordinal: 318
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/settings.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/defaults/__init__.py`
- `sfpcl_credit/defaults/apps.py`
- `sfpcl_credit/defaults/migrations/0001_initial.py`
- `sfpcl_credit/defaults/migrations/__init__.py`
- `sfpcl_credit/defaults/models.py`
- `sfpcl_credit/defaults/modules/__init__.py`
- `sfpcl_credit/defaults/modules/default_workflow.py`
- `sfpcl_credit/defaults/views.py`
- `sfpcl_credit/identity/catalogue.py`
- `sfpcl_credit/tests/test_credit_model_ownership_migration.py`
- `sfpcl_credit/tests/test_default_case_opening_api.py`
- `sfpcl_credit/tests/test_default_recovery_postgresql_acceptance.py`
- `sfpcl_credit/tests/test_witness_evidence_migration.py`

Impacted test labels:
- `sfpcl_credit.tests.test_credit_model_ownership_migration`
- `sfpcl_credit.tests.test_default_case_opening_api`
- `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance`
- `sfpcl_credit.tests.test_witness_evidence_migration`
