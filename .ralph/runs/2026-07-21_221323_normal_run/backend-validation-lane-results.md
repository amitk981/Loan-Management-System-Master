# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: high-risk slice
- Enforcement policy: selective
- Slice risk: high
- Candidate completion ordinal: 315
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/applications/modules/search_facade.py`
- `sfpcl_credit/documents/search_facade.py`
- `sfpcl_credit/identity/modules/search_facade.py`
- `sfpcl_credit/loans/modules/search_facade.py`
- `sfpcl_credit/members/search_facade.py`
- `sfpcl_credit/processes/global_search.py`
- `sfpcl_credit/sap_workflow/modules/search_facade.py`
- `sfpcl_credit/security_instruments/search_facade.py`
- `sfpcl_credit/tests/test_global_search_api.py`

Impacted test labels:
- `sfpcl_credit.tests.test_global_search_api`
- `sfpcl_credit.tests.test_appraisal_api`
- `sfpcl_credit.tests.test_approval_case_routing_api`
- `sfpcl_credit.tests.test_approval_matrix`
- `sfpcl_credit.tests.test_blank_dated_cheque_api`
- `sfpcl_credit.tests.test_credit_modules`
- `sfpcl_credit.tests.test_disbursement_initiation_api`
- `sfpcl_credit.tests.test_disbursement_readiness_api`
- `sfpcl_credit.tests.test_document_checklist_api`
- `sfpcl_credit.tests.test_final_documentation_approval_api`
- `sfpcl_credit.tests.test_loan_account_creation_api`
- `sfpcl_credit.tests.test_loan_document_generation_api`
- `sfpcl_credit.tests.test_member_authority_action_matrix`
- `sfpcl_credit.tests.test_nominee_validation`
- `sfpcl_credit.tests.test_portal_deficiency_response_api`
- `sfpcl_credit.tests.test_portal_member_api`
- `sfpcl_credit.tests.test_power_of_attorney_api`
- `sfpcl_credit.tests.test_sanction_submission_api`
- `sfpcl_credit.tests.test_sap_customer_profile_request_api`
- `sfpcl_credit.tests.test_seed_e2e_users`
- `sfpcl_credit.tests.test_seed_portal_e2e_fixture`
- `sfpcl_credit.tests.test_sh4_api`
- `sfpcl_credit.tests.test_signature_mismatch_api`
- `sfpcl_credit.tests.test_stamp_notary_api`
- `sfpcl_credit.tests.test_statement_evidence_owner_scope_closure`
- `sfpcl_credit.tests.test_witness_api`
- `sfpcl_credit.tests.test_witness_evidence_migration`
- `sfpcl_credit.tests.test_loan_applications_api`
