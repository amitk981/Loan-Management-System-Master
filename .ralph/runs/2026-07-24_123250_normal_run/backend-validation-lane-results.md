# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: periodic full-suite checkpoint at completed slice 344
- Enforcement policy: selective
- Slice risk: high
- Candidate completion ordinal: 344
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/approvals/management/commands/seed_approval_configuration.py`
- `sfpcl_credit/config/production_settings.py`
- `sfpcl_credit/config/settings.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/identity/management/commands/seed_demo_users.py`
- `sfpcl_credit/identity/management/commands/seed_e2e_users.py`
- `sfpcl_credit/identity/management/commands/seed_epic_009_e2e_fixture.py`
- `sfpcl_credit/identity/management/commands/seed_portal_e2e_fixture.py`
- `sfpcl_credit/identity/modules/auth_service.py`
- `sfpcl_credit/identity/modules/portal_auth_service.py`
- `sfpcl_credit/tests/test_production_demo_isolation.py`

Impacted test labels:
- `sfpcl_credit.tests.test_production_demo_isolation`
- `sfpcl_credit.tests.test_approval_case_routing_api`
- `sfpcl_credit.tests.test_approval_matrix`
- `sfpcl_credit.tests.test_archive_api`
- `sfpcl_credit.tests.test_audit_explorer_api`
- `sfpcl_credit.tests.test_audit_logs_api`
- `sfpcl_credit.tests.test_audit_observations_api`
- `sfpcl_credit.tests.test_auditor_epic_011_api`
- `sfpcl_credit.tests.test_closure_api`
- `sfpcl_credit.tests.test_credit_action_parity_matrix`
- `sfpcl_credit.tests.test_default_case_opening_api`
- `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance`
- `sfpcl_credit.tests.test_disbursement_initiation_api`
- `sfpcl_credit.tests.test_disbursement_readiness_api`
- `sfpcl_credit.tests.test_document_checklist_api`
- `sfpcl_credit.tests.test_final_documentation_approval_api`
- `sfpcl_credit.tests.test_global_search_compliance`
- `sfpcl_credit.tests.test_kyc_review_api`
- `sfpcl_credit.tests.test_loan_account_creation_api`
- `sfpcl_credit.tests.test_loan_account_reads_api`
- `sfpcl_credit.tests.test_loan_document_generation_api`
- `sfpcl_credit.tests.test_non_payment_note_workflow_api`
- `sfpcl_credit.tests.test_power_of_attorney_api`
- `sfpcl_credit.tests.test_recovery_decision_api`
- `sfpcl_credit.tests.test_report_api`
- `sfpcl_credit.tests.test_report_catalogue_api`
- `sfpcl_credit.tests.test_sanction_submission_api`
- `sfpcl_credit.tests.test_sap_customer_profile_request_api`
- `sfpcl_credit.tests.test_security_instrument_boundary`
- `sfpcl_credit.tests.test_seed_demo_users`
- `sfpcl_credit.tests.test_tri_party_agreement_api`
- `sfpcl_credit.tests.test_workflow_events_api`
- `sfpcl_credit.tests.test_approval_read_scope_migration`
