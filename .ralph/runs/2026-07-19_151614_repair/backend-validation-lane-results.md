# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 281
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/disbursements/migrations/0010_enable_pgcrypto_for_exact_selector.py`
- `sfpcl_credit/disbursements/modules/current_disbursement_evidence.py`
- `sfpcl_credit/disbursements/modules/disbursement_initiation.py`
- `sfpcl_credit/identity/models.py`
- `sfpcl_credit/loans/modules/loan_account_lifecycle.py`
- `sfpcl_credit/loans/modules/loan_account_read.py`
- `sfpcl_credit/processes/loan_account_360.py`
- `sfpcl_credit/sap_workflow/modules/sap_customer_code.py`
- `sfpcl_credit/sap_workflow/modules/sap_customer_profile.py`
- `sfpcl_credit/tests/test_epic009_postgresql_acceptance.py`
- `sfpcl_credit/tests/test_loan_account_reads_api.py`
- `sfpcl_credit/tests/test_portal_disbursement_status_api.py`
- `sfpcl_credit/identity/migrations/0004_auditlog_selector_manifest_sha256.py`
- `sfpcl_credit/tests/test_epic009_exact_selector_postgresql.py`
- `sfpcl_credit/tests/test_epic009_owner_selector_equivalence.py`
- `sfpcl_credit/tests/test_pgcrypto_migration_ownership.py`

Impacted test labels:
- None
