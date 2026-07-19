# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: shared schema or backend infrastructure changed: sfpcl_credit/config/urls.py
- Enforcement: full configured backend gates remain mandatory
- Slice risk: medium
- Candidate completion ordinal: 291
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/loans/models.py`
- `sfpcl_credit/loans/modules/direct_repayment_posting.py`
- `sfpcl_credit/loans/modules/repayment_allocator.py`
- `sfpcl_credit/loans/views.py`
- `sfpcl_credit/tests/test_servicing_postgresql_acceptance.py`
- `sfpcl_credit/loans/migrations/0008_subsidiary_deduction_reconciliation.py`
- `sfpcl_credit/loans/modules/subsidiary_deduction_reconciliation.py`
- `sfpcl_credit/tests/test_subsidiary_deduction_reconciliation_api.py`

Impacted test labels:
- None
