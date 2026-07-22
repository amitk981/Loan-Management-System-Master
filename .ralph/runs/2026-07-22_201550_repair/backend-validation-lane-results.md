# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: periodic full-suite checkpoint at completed slice 324
- Enforcement policy: selective
- Slice risk: medium
- Candidate completion ordinal: 324
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/closure/__init__.py`
- `sfpcl_credit/closure/apps.py`
- `sfpcl_credit/closure/migrations/0001_initial.py`
- `sfpcl_credit/closure/migrations/__init__.py`
- `sfpcl_credit/closure/models.py`
- `sfpcl_credit/closure/modules/__init__.py`
- `sfpcl_credit/closure/modules/loan_closure.py`
- `sfpcl_credit/closure/views.py`
- `sfpcl_credit/config/settings.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/loans/models.py`
- `sfpcl_credit/monitoring/modules/dpd_monitoring.py`
- `sfpcl_credit/tests/test_closure_api.py`
- `sfpcl_credit/tests/test_default_grace_assessment_api.py`
- `sfpcl_credit/tests/test_default_recovery_postgresql_acceptance.py`
- `sfpcl_credit/tests/test_direct_repayment_posting_api.py`

Impacted test labels:
- `sfpcl_credit.tests.test_closure_api`
- `sfpcl_credit.tests.test_default_grace_assessment_api`
- `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance`
- `sfpcl_credit.tests.test_direct_repayment_posting_api`
