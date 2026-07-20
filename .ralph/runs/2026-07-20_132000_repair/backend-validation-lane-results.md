# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 297
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/configurations/models.py`
- `sfpcl_credit/configurations/modules/interest_rate_configuration.py`
- `sfpcl_credit/interest/modules/interest_engine.py`
- `sfpcl_credit/loans/modules/loan_account_lifecycle.py`
- `sfpcl_credit/loans/modules/loan_account_read.py`
- `sfpcl_credit/tests/servicing_builders.py`
- `sfpcl_credit/tests/test_interest_rate_config_api.py`
- `sfpcl_credit/tests/test_servicing_financial_owner_closure.py`
- `sfpcl_credit/configurations/migrations/0007_rate_status_approval_coherence.py`

Impacted test labels:
- None
