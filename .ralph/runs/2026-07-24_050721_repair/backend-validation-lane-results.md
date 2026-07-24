# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: backend root reports has no valid owner/contract test mapping
- Enforcement policy: selective
- Slice risk: medium
- Candidate completion ordinal: 339
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/settings.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/processes/tasks.py`
- `sfpcl_credit/reports/apps.py`
- `sfpcl_credit/reports/migrations/0001_initial.py`
- `sfpcl_credit/reports/migrations/__init__.py`
- `sfpcl_credit/reports/models.py`
- `sfpcl_credit/reports/modules/__init__.py`
- `sfpcl_credit/reports/modules/report_export.py`
- `sfpcl_credit/reports/storage.py`
- `sfpcl_credit/reports/views.py`
- `sfpcl_credit/tests/test_report_export_postgresql_acceptance.py`
- `sfpcl_credit/tests/test_report_exports_api.py`

Impacted test labels:
- `sfpcl_credit.tests.test_report_export_postgresql_acceptance`
- `sfpcl_credit.tests.test_report_exports_api`
- `sfpcl_credit.tests.test_report_catalogue_api`
