# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: multiple backend module roots changed: approvals, identity
- Enforcement policy: selective
- Slice risk: medium
- Candidate completion ordinal: 335
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/approvals/modules/read_scope.py`
- `sfpcl_credit/closure/modules/loan_closure.py`
- `sfpcl_credit/compliance/modules/auditor_epic_011.py`
- `sfpcl_credit/compliance/modules/compliance_control_tracker.py`
- `sfpcl_credit/compliance/modules/grievance_workflow.py`
- `sfpcl_credit/compliance/modules/kyc_review_tracker.py`
- `sfpcl_credit/compliance/modules/nbfc_principal_business_test.py`
- `sfpcl_credit/compliance/modules/section186_tracker.py`
- `sfpcl_credit/compliance/views.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/defaults/modules/default_workflow.py`
- `sfpcl_credit/identity/catalogue.py`
- `sfpcl_credit/tests/test_auditor_epic_011_api.py`
- `sfpcl_credit/tests/test_default_case_opening_api.py`
- `sfpcl_credit/tests/test_global_search_compliance.py`
- `sfpcl_credit/tests/test_kyc_review_api.py`
- `sfpcl_credit/tests/test_statutory_trackers.py`

Impacted test labels:
- `sfpcl_credit.tests.test_auditor_epic_011_api`
- `sfpcl_credit.tests.test_default_case_opening_api`
- `sfpcl_credit.tests.test_global_search_compliance`
- `sfpcl_credit.tests.test_kyc_review_api`
- `sfpcl_credit.tests.test_statutory_trackers`
- `sfpcl_credit.tests.test_approval_case_routing_api`
- `sfpcl_credit.tests.test_approval_matrix`
- `sfpcl_credit.tests.test_archive_api`
- `sfpcl_credit.tests.test_closure_api`
- `sfpcl_credit.tests.test_credit_action_parity_matrix`
- `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance`
- `sfpcl_credit.tests.test_disbursement_initiation_api`
- `sfpcl_credit.tests.test_disbursement_readiness_api`
- `sfpcl_credit.tests.test_document_checklist_api`
- `sfpcl_credit.tests.test_final_documentation_approval_api`
- `sfpcl_credit.tests.test_loan_account_creation_api`
- `sfpcl_credit.tests.test_loan_account_reads_api`
- `sfpcl_credit.tests.test_loan_document_generation_api`
- `sfpcl_credit.tests.test_non_payment_note_workflow_api`
- `sfpcl_credit.tests.test_power_of_attorney_api`
- `sfpcl_credit.tests.test_recovery_decision_api`
- `sfpcl_credit.tests.test_sanction_submission_api`
- `sfpcl_credit.tests.test_sap_customer_profile_request_api`
- `sfpcl_credit.tests.test_security_instrument_boundary`
- `sfpcl_credit.tests.test_seed_demo_users`
- `sfpcl_credit.tests.test_tri_party_agreement_api`
- `sfpcl_credit.tests.test_approval_read_scope_migration`
