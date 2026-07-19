# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 284
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/disbursements/modules/current_disbursement_evidence.py`
- `sfpcl_credit/disbursements/modules/post_transfer_evidence.py`
- `sfpcl_credit/identity/epic009_e2e_fixture.py`
- `sfpcl_credit/identity/management/commands/seed_portal_e2e_fixture.py`
- `sfpcl_credit/processes/loan_account_360.py`
- `sfpcl_credit/sap_workflow/migrations/0002_sapcustomerprofilerequest_delivery_storage_checksum_sha256.py`
- `sfpcl_credit/tests/test_disbursement_workspace_api.py`
- `sfpcl_credit/tests/test_epic009_read_boundary_convergence.py`
- `sfpcl_credit/tests/test_epic009_read_boundary_postgresql.py`
- `sfpcl_credit/tests/test_seed_portal_e2e_fixture.py`
- `sfpcl_credit/identity/fixtures/epic009_browser_files/annexure-i.xlsx`
- `sfpcl_credit/identity/fixtures/epic009_browser_fixture.json.gz`

Impacted test labels:
- None
