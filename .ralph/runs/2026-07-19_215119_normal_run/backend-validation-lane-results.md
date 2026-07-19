# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: shared schema or backend infrastructure changed: sfpcl_credit/config/urls.py
- Enforcement: full configured backend gates remain mandatory
- Slice risk: medium
- Candidate completion ordinal: 285
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/disbursements/modules/disbursement_transfer_success.py`
- `sfpcl_credit/disbursements/modules/post_transfer_evidence.py`
- `sfpcl_credit/loans/models.py`
- `sfpcl_credit/loans/views.py`
- `sfpcl_credit/loans/migrations/0002_repayment_schedule.py`
- `sfpcl_credit/processes/loan_servicing.py`
- `sfpcl_credit/tests/test_loan_schedule_ledger_api.py`

Impacted test labels:
- None
