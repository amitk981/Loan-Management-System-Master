# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 301
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/configurations/models.py`
- `sfpcl_credit/configurations/modules/interest_rate_configuration.py`
- `sfpcl_credit/processes/loan_account_360.py`
- `sfpcl_credit/processes/tasks.py`
- `sfpcl_credit/tests/servicing_builders.py`
- `sfpcl_credit/tests/test_servicing_financial_owner_closure.py`
- `sfpcl_credit/configurations/migrations/0008_current_rate_projection_decision.py`
- `sfpcl_credit/loans/current_rate_projection.py`

Impacted test labels:
- None
