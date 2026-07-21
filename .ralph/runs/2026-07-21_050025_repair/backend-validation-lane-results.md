# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: shared schema or backend infrastructure changed: sfpcl_credit/config/urls.py
- Enforcement: full configured backend gates remain mandatory
- Slice risk: medium
- Candidate completion ordinal: 305
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/identity/catalogue.py`
- `sfpcl_credit/monitoring/models.py`
- `sfpcl_credit/monitoring/views.py`
- `sfpcl_credit/tests/test_catalogue_seed.py`
- `sfpcl_credit/tests/test_disbursement_initiation_api.py`
- `sfpcl_credit/tests/test_servicing_postgresql_acceptance.py`
- `sfpcl_credit/monitoring/migrations/0004_quarterly_mis.py`
- `sfpcl_credit/monitoring/modules/mis_exports.py`
- `sfpcl_credit/monitoring/modules/quarterly_mis.py`
- `sfpcl_credit/tests/test_quarterly_mis_api.py`

Impacted test labels:
- None
