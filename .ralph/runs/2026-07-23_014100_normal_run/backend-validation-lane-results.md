# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: periodic full-suite checkpoint at completed slice 328
- Enforcement policy: selective
- Slice risk: medium
- Candidate completion ordinal: 328
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/closure/compliance_evidence_facade.py`
- `sfpcl_credit/compliance/__init__.py`
- `sfpcl_credit/compliance/apps.py`
- `sfpcl_credit/compliance/catalogue.py`
- `sfpcl_credit/compliance/migrations/0001_initial.py`
- `sfpcl_credit/compliance/migrations/__init__.py`
- `sfpcl_credit/compliance/models.py`
- `sfpcl_credit/compliance/modules/__init__.py`
- `sfpcl_credit/compliance/modules/compliance_control_tracker.py`
- `sfpcl_credit/compliance/modules/compliance_task_engine.py`
- `sfpcl_credit/compliance/views.py`
- `sfpcl_credit/config/settings.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/identity/catalogue.py`
- `sfpcl_credit/legal_documents/compliance_evidence_facade.py`
- `sfpcl_credit/recovery/compliance_evidence_facade.py`
- `sfpcl_credit/tests/test_compliance_api.py`
- `sfpcl_credit/tests/test_compliance_postgresql_acceptance.py`
- `sfpcl_credit/tests/test_compliance_task_engine.py`

Impacted test labels:
- `sfpcl_credit.tests.test_compliance_api`
- `sfpcl_credit.tests.test_compliance_postgresql_acceptance`
- `sfpcl_credit.tests.test_compliance_task_engine`
- `sfpcl_credit.tests.test_archive_api`
- `sfpcl_credit.tests.test_closure_api`
- `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance`
- `sfpcl_credit.tests.test_noc_api`
- `sfpcl_credit.tests.test_security_return_api`
