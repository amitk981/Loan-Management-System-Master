# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 307
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/identity/modules/auth_service.py`
- `sfpcl_credit/identity/modules/portal_auth_service.py`
- `sfpcl_credit/loans/views.py`
- `sfpcl_credit/processes/loan_servicing.py`
- `sfpcl_credit/processes/loan_ledger_statements.py`
- `sfpcl_credit/tests/test_loan_ledger_statement_api.py`

Impacted test labels:
- None
