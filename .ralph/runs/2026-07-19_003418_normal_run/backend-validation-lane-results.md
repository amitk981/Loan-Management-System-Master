# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 273
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/disbursements/modules/current_disbursement_evidence.py`
- `sfpcl_credit/disbursements/modules/post_transfer_evidence.py`
- `sfpcl_credit/legal_documents/modules/disbursement_readiness.py`
- `sfpcl_credit/loans/modules/loan_account_lifecycle.py`
- `sfpcl_credit/processes/portal_disbursement_status.py`
- `sfpcl_credit/sap_workflow/modules/sap_customer_profile.py`
- `sfpcl_credit/tests/test_portal_disbursement_status_api.py`

Impacted test labels:
- None
