# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: backend root reports has no valid owner/contract test mapping
- Enforcement policy: selective
- Slice risk: medium
- Candidate completion ordinal: 355
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/reports/query.py`
- `sfpcl_credit/reports/selectors/application_pipeline.py`
- `sfpcl_credit/reports/selectors/compliance_dashboard.py`
- `sfpcl_credit/reports/selectors/disbursement_pending.py`
- `sfpcl_credit/reports/selectors/documentation_readiness.py`
- `sfpcl_credit/reports/selectors/dpd.py`
- `sfpcl_credit/reports/selectors/loan_portfolio.py`
- `sfpcl_credit/tests/test_report_api.py`

Impacted test labels:
- `sfpcl_credit.tests.test_report_api`
- `sfpcl_credit.tests.test_audit_explorer_api`
- `sfpcl_credit.tests.test_report_catalogue_api`
- `sfpcl_credit.tests.test_report_export_postgresql_acceptance`
- `sfpcl_credit.tests.test_report_exports_api`
