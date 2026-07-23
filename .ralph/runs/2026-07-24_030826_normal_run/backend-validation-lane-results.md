# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: high-risk slice
- Enforcement policy: selective
- Slice risk: high
- Candidate completion ordinal: 338
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/reports/registry.py`
- `sfpcl_credit/reports/selectors/closure_noc.py`
- `sfpcl_credit/reports/selectors/default.py`
- `sfpcl_credit/reports/selectors/grievance.py`
- `sfpcl_credit/reports/selectors/kyc_rekyc.py`
- `sfpcl_credit/reports/selectors/money_lending.py`
- `sfpcl_credit/reports/selectors/recovery.py`
- `sfpcl_credit/reports/selectors/stamp_duty.py`
- `sfpcl_credit/reports/selectors/statutory.py`
- `sfpcl_credit/tests/test_report_catalogue_api.py`

Impacted test labels:
- `sfpcl_credit.tests.test_report_catalogue_api`
