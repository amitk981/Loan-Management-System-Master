# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 279
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/disbursements/modules/disbursement_advice.py`
- `sfpcl_credit/disbursements/modules/disbursement_authorisation.py`
- `sfpcl_credit/disbursements/modules/disbursement_transfer_success.py`
- `sfpcl_credit/disbursements/modules/post_transfer_evidence.py`
- `sfpcl_credit/loans/modules/loan_account_lifecycle.py`
- `sfpcl_credit/loans/modules/loan_account_read.py`
- `sfpcl_credit/processes/disbursement_workspace.py`
- `sfpcl_credit/processes/loan_account_360.py`
- `sfpcl_credit/sap_workflow/modules/sap_customer_profile.py`
- `sfpcl_credit/tests/test_loan_account_reads_api.py`

Impacted test labels:
- None
