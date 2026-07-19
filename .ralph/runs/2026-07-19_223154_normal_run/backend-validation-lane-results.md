# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 286
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/loans/models.py`
- `sfpcl_credit/loans/views.py`
- `sfpcl_credit/loans/migrations/0003_repayment_repaymentsappostingobligation_and_more.py`
- `sfpcl_credit/loans/modules/direct_repayment_posting.py`
- `sfpcl_credit/tests/test_direct_repayment_posting_api.py`
- `sfpcl_credit/tests/test_servicing_postgresql_acceptance.py`

Impacted test labels:
- None
