# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 302
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/interest/models.py`
- `sfpcl_credit/interest/modules/as_of_accounting.py`
- `sfpcl_credit/interest/modules/interest_engine.py`
- `sfpcl_credit/tests/servicing_builders.py`
- `sfpcl_credit/tests/test_interest_accrual_api.py`
- `sfpcl_credit/tests/test_interest_capitalisation_api.py`
- `sfpcl_credit/tests/test_interest_invoice_api.py`
- `sfpcl_credit/tests/test_interest_rate_config_api.py`
- `sfpcl_credit/tests/test_servicing_postgresql_acceptance.py`
- `sfpcl_credit/interest/migrations/0005_interest_calculation_rounding_policy.py`
- `sfpcl_credit/shared/money.py`
- `sfpcl_credit/tests/test_interest_policy_integrity_closure.py`

Impacted test labels:
- None
