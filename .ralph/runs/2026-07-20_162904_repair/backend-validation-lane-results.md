# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: shared schema or backend infrastructure changed: sfpcl_credit/config/settings.py
- Enforcement: full configured backend gates remain mandatory
- Slice risk: medium
- Candidate completion ordinal: 299
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/settings.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/identity/catalogue.py`
- `sfpcl_credit/tests/test_credit_model_ownership_migration.py`
- `sfpcl_credit/tests/test_servicing_postgresql_acceptance.py`
- `sfpcl_credit/tests/test_witness_evidence_migration.py`
- `sfpcl_credit/monitoring/__init__.py`
- `sfpcl_credit/monitoring/apps.py`
- `sfpcl_credit/monitoring/migrations/0001_initial.py`
- `sfpcl_credit/monitoring/migrations/__init__.py`
- `sfpcl_credit/monitoring/models.py`
- `sfpcl_credit/monitoring/modules/__init__.py`
- `sfpcl_credit/monitoring/modules/dpd_monitoring.py`
- `sfpcl_credit/monitoring/views.py`
- `sfpcl_credit/tests/test_dpd_monitoring_api.py`

Impacted test labels:
- None
