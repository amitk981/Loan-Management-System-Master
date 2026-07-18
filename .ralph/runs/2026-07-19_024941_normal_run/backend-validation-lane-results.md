# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 275
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/loans/modules/loan_account_lifecycle.py`
- `sfpcl_credit/loans/views.py`
- `sfpcl_credit/loans/modules/loan_account_read.py`
- `sfpcl_credit/processes/loan_account_360.py`
- `sfpcl_credit/tests/test_loan_account_reads_api.py`

Impacted test labels:
- None
