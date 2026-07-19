# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 287
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/loans/models.py`
- `sfpcl_credit/loans/views.py`
- `sfpcl_credit/processes/loan_servicing.py`
- `sfpcl_credit/tests/test_servicing_postgresql_acceptance.py`
- `sfpcl_credit/loans/migrations/0004_principal_first_allocation.py`
- `sfpcl_credit/loans/modules/repayment_allocator.py`
- `sfpcl_credit/tests/test_repayment_allocation_api.py`

Impacted test labels:
- None
