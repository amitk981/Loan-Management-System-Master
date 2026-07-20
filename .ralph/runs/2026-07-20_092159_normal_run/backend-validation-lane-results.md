# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 296
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/identity/catalogue.py`
- `sfpcl_credit/interest/models.py`
- `sfpcl_credit/interest/modules/interest_engine.py`
- `sfpcl_credit/interest/views.py`
- `sfpcl_credit/loans/modules/loan_account_read.py`
- `sfpcl_credit/processes/loan_account_360.py`
- `sfpcl_credit/processes/loan_servicing.py`
- `sfpcl_credit/tests/test_servicing_postgresql_acceptance.py`
- `sfpcl_credit/interest/migrations/0003_interestcapitalisation_and_more.py`
- `sfpcl_credit/tests/test_interest_capitalisation_api.py`

Impacted test labels:
- None
