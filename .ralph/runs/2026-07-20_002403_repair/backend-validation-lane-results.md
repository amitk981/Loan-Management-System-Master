# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 288
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/identity/catalogue.py`
- `sfpcl_credit/loans/models.py`
- `sfpcl_credit/loans/modules/direct_repayment_posting.py`
- `sfpcl_credit/loans/views.py`
- `sfpcl_credit/tests/test_servicing_postgresql_acceptance.py`
- `sfpcl_credit/loans/migrations/0005_bankstatementimport_bankstatementline_and_more.py`
- `sfpcl_credit/loans/modules/bank_statement_matching.py`
- `sfpcl_credit/tests/test_bank_statement_matching_api.py`

Impacted test labels:
- None
