# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: periodic full-suite checkpoint at completed slice 336
- Enforcement policy: selective
- Slice risk: medium
- Candidate completion ordinal: 336
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/reports/__init__.py`
- `sfpcl_credit/reports/errors.py`
- `sfpcl_credit/reports/pagination.py`
- `sfpcl_credit/reports/query.py`
- `sfpcl_credit/reports/registry.py`
- `sfpcl_credit/reports/selectors/__init__.py`
- `sfpcl_credit/reports/selectors/application_pipeline.py`
- `sfpcl_credit/reports/selectors/compliance_dashboard.py`
- `sfpcl_credit/reports/selectors/disbursement_pending.py`
- `sfpcl_credit/reports/selectors/documentation_readiness.py`
- `sfpcl_credit/reports/selectors/dpd.py`
- `sfpcl_credit/reports/selectors/loan_portfolio.py`
- `sfpcl_credit/reports/views.py`
- `sfpcl_credit/tests/test_report_api.py`

Impacted test labels:
- `sfpcl_credit.tests.test_report_api`
