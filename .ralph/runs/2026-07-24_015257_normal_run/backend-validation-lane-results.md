# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: multiple backend module roots changed: approvals, reports
- Enforcement policy: selective
- Slice risk: medium
- Candidate completion ordinal: 337
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/approvals/modules/sanction_register.py`
- `sfpcl_credit/reports/registry.py`
- `sfpcl_credit/reports/selectors/catalogue_permissions.py`
- `sfpcl_credit/reports/selectors/cfo_quarterly_mis.py`
- `sfpcl_credit/reports/selectors/credit_sanction.py`
- `sfpcl_credit/reports/selectors/disbursement.py`
- `sfpcl_credit/reports/selectors/exception.py`
- `sfpcl_credit/reports/selectors/interest_accrual.py`
- `sfpcl_credit/reports/selectors/interest_invoice.py`
- `sfpcl_credit/reports/selectors/repayment.py`
- `sfpcl_credit/reports/selectors/sap_pending.py`
- `sfpcl_credit/reports/selectors/security_custody.py`
- `sfpcl_credit/tests/test_report_catalogue_api.py`

Impacted test labels:
- `sfpcl_credit.tests.test_report_catalogue_api`
- `sfpcl_credit.tests.test_approval_case_routing_api`
- `sfpcl_credit.tests.test_approval_matrix`
- `sfpcl_credit.tests.test_archive_api`
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
- `sfpcl_credit.tests.test_sanction_submission_api`
- `sfpcl_credit.tests.test_sap_customer_profile_request_api`
- `sfpcl_credit.tests.test_security_instrument_boundary`
- `sfpcl_credit.tests.test_seed_demo_users`
- `sfpcl_credit.tests.test_tri_party_agreement_api`
- `sfpcl_credit.tests.test_approval_read_scope_migration`
