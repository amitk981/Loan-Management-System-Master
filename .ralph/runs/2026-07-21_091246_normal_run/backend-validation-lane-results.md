# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: periodic full-suite checkpoint at completed slice 308
- Enforcement policy: selective
- Slice risk: high
- Candidate completion ordinal: 308
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/members/portal_views.py`
- `sfpcl_credit/processes/portal_loan_servicing.py`
- `sfpcl_credit/tests/test_portal_loan_accounts_api.py`

Impacted test labels:
- `sfpcl_credit.tests.test_portal_loan_accounts_api`
- `sfpcl_credit.tests.test_active_member_status_module`
- `sfpcl_credit.tests.test_appraisal_api`
- `sfpcl_credit.tests.test_approval_case_routing_api`
- `sfpcl_credit.tests.test_approval_matrix`
- `sfpcl_credit.tests.test_blank_dated_cheque_api`
- `sfpcl_credit.tests.test_cdsl_share_pledge_api`
- `sfpcl_credit.tests.test_credit_modules`
- `sfpcl_credit.tests.test_disbursement_authorisation_api`
- `sfpcl_credit.tests.test_disbursement_initiation_api`
- `sfpcl_credit.tests.test_disbursement_readiness_api`
- `sfpcl_credit.tests.test_document_checklist_api`
- `sfpcl_credit.tests.test_final_documentation_approval_api`
- `sfpcl_credit.tests.test_loan_account_creation_api`
- `sfpcl_credit.tests.test_loan_applications_api`
- `sfpcl_credit.tests.test_loan_document_generation_api`
- `sfpcl_credit.tests.test_member_authority_action_matrix`
- `sfpcl_credit.tests.test_member_bank_accounts_api`
- `sfpcl_credit.tests.test_member_directory_api`
- `sfpcl_credit.tests.test_member_governance_api`
- `sfpcl_credit.tests.test_member_kyc_api`
- `sfpcl_credit.tests.test_member_land_crop_api`
- `sfpcl_credit.tests.test_member_nominees_api`
- `sfpcl_credit.tests.test_member_profile_api`
- `sfpcl_credit.tests.test_member_scope_assignment_api`
- `sfpcl_credit.tests.test_member_shareholdings_api`
- `sfpcl_credit.tests.test_portal_auth_api`
- `sfpcl_credit.tests.test_portal_deficiency_response_api`
- `sfpcl_credit.tests.test_portal_disbursement_status_api`
- `sfpcl_credit.tests.test_portal_member_api`
- `sfpcl_credit.tests.test_power_of_attorney_api`
- `sfpcl_credit.tests.test_produce_supply_api`
- `sfpcl_credit.tests.test_reminder_queue_api`
- `sfpcl_credit.tests.test_sanction_submission_api`
- `sfpcl_credit.tests.test_sap_customer_profile_request_api`
- `sfpcl_credit.tests.test_seed_e2e_users`
- `sfpcl_credit.tests.test_sh4_api`
- `sfpcl_credit.tests.test_signature_mismatch_api`
- `sfpcl_credit.tests.test_stamp_notary_api`
- `sfpcl_credit.tests.test_statement_evidence_owner_scope_closure`
- `sfpcl_credit.tests.test_tri_party_agreement_api`
- `sfpcl_credit.tests.test_witness_api`
- `sfpcl_credit.tests.test_nominee_validation`
