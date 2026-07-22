# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: high-risk slice
- Enforcement policy: selective
- Slice risk: high
- Candidate completion ordinal: 322
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/approvals/modules/approval_actions.py`
- `sfpcl_credit/approvals/modules/approval_case_engine.py`
- `sfpcl_credit/approvals/modules/recovery_handoff.py`
- `sfpcl_credit/config/settings.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/recovery/apps.py`
- `sfpcl_credit/recovery/migrations/0001_initial.py`
- `sfpcl_credit/recovery/migrations/__init__.py`
- `sfpcl_credit/recovery/models.py`
- `sfpcl_credit/recovery/modules/recovery_decision.py`
- `sfpcl_credit/recovery/views.py`
- `sfpcl_credit/tests/test_credit_model_ownership_migration.py`
- `sfpcl_credit/tests/test_default_recovery_postgresql_acceptance.py`
- `sfpcl_credit/tests/test_non_payment_note_workflow_api.py`
- `sfpcl_credit/tests/test_recovery_decision_api.py`
- `sfpcl_credit/tests/test_witness_evidence_migration.py`

Impacted test labels:
- `sfpcl_credit.tests.test_credit_model_ownership_migration`
- `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance`
- `sfpcl_credit.tests.test_non_payment_note_workflow_api`
- `sfpcl_credit.tests.test_recovery_decision_api`
- `sfpcl_credit.tests.test_witness_evidence_migration`
- `sfpcl_credit.tests.test_approval_case_routing_api`
- `sfpcl_credit.tests.test_approval_matrix`
- `sfpcl_credit.tests.test_credit_action_parity_matrix`
- `sfpcl_credit.tests.test_default_case_opening_api`
- `sfpcl_credit.tests.test_disbursement_initiation_api`
- `sfpcl_credit.tests.test_disbursement_readiness_api`
- `sfpcl_credit.tests.test_document_checklist_api`
- `sfpcl_credit.tests.test_final_documentation_approval_api`
- `sfpcl_credit.tests.test_loan_account_creation_api`
- `sfpcl_credit.tests.test_loan_account_reads_api`
- `sfpcl_credit.tests.test_loan_document_generation_api`
- `sfpcl_credit.tests.test_power_of_attorney_api`
- `sfpcl_credit.tests.test_sanction_submission_api`
- `sfpcl_credit.tests.test_sap_customer_profile_request_api`
- `sfpcl_credit.tests.test_security_instrument_boundary`
- `sfpcl_credit.tests.test_seed_demo_users`
- `sfpcl_credit.tests.test_tri_party_agreement_api`
- `sfpcl_credit.tests.test_approval_read_scope_migration`
