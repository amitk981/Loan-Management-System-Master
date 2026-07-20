# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 293
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/configurations/models.py`
- `sfpcl_credit/configurations/modules/interest_rate_configuration.py`
- `sfpcl_credit/loans/modules/bank_statement_matching.py`
- `sfpcl_credit/loans/modules/loan_account_lifecycle.py`
- `sfpcl_credit/loans/modules/loan_account_read.py`
- `sfpcl_credit/loans/modules/repayment_allocator.py`
- `sfpcl_credit/processes/loan_servicing.py`
- `sfpcl_credit/tests/test_interest_rate_config_api.py`
- `sfpcl_credit/tests/test_repayment_adjustment_api.py`
- `sfpcl_credit/tests/test_repayment_allocation_api.py`
- `sfpcl_credit/tests/test_statement_evidence_owner_scope_closure.py`
- `sfpcl_credit/tests/servicing_builders.py`
- `sfpcl_credit/tests/test_servicing_financial_owner_closure.py`

Impacted test labels:
- None
