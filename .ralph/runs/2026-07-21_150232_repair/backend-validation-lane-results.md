# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: high-risk slice
- Enforcement policy: selective
- Slice risk: high
- Candidate completion ordinal: 310
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/communications/modules/communication_dispatcher.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/configurations/migrations/0009_repaymentinstructionversion_and_more.py`
- `sfpcl_credit/configurations/models.py`
- `sfpcl_credit/loans/modules/direct_repayment_posting.py`
- `sfpcl_credit/loans/modules/dpd_source_decision.py`
- `sfpcl_credit/loans/views.py`
- `sfpcl_credit/monitoring/modules/quarterly_mis.py`
- `sfpcl_credit/monitoring/modules/reminder_engine.py`
- `sfpcl_credit/processes/communication_delivery.py`
- `sfpcl_credit/processes/direct_repayment_command.py`
- `sfpcl_credit/processes/loan_ledger_statements.py`
- `sfpcl_credit/processes/portal_loan_servicing.py`
- `sfpcl_credit/tests/servicing_builders.py`
- `sfpcl_credit/tests/test_epic010_terminal_owner_finalizer.py`
- `sfpcl_credit/tests/test_portal_loan_accounts_api.py`

Impacted test labels:
- `sfpcl_credit.tests.test_epic010_terminal_owner_finalizer`
- `sfpcl_credit.tests.test_portal_loan_accounts_api`
- `sfpcl_credit.tests.test_approval_case_routing_api`
- `sfpcl_credit.tests.test_communication_advice_persistence`
- `sfpcl_credit.tests.test_communication_channel_contract`
- `sfpcl_credit.tests.test_communication_dispatcher_jobs`
- `sfpcl_credit.tests.test_communication_job_migration`
- `sfpcl_credit.tests.test_communication_receipt_owner_migration`
- `sfpcl_credit.tests.test_communication_worker_runtime`
- `sfpcl_credit.tests.test_communications_api`
- `sfpcl_credit.tests.test_content_templates_api`
- `sfpcl_credit.tests.test_direct_repayment_posting_api`
- `sfpcl_credit.tests.test_disbursement_advice_api`
- `sfpcl_credit.tests.test_disbursement_authorisation_api`
- `sfpcl_credit.tests.test_disbursement_initiation_api`
- `sfpcl_credit.tests.test_disbursement_transfer_success_api`
- `sfpcl_credit.tests.test_final_documentation_approval_api`
- `sfpcl_credit.tests.test_interest_capitalisation_api`
- `sfpcl_credit.tests.test_interest_invoice_api`
- `sfpcl_credit.tests.test_interest_rate_config_api`
- `sfpcl_credit.tests.test_notifications_api`
- `sfpcl_credit.tests.test_portal_disbursement_status_api`
- `sfpcl_credit.tests.test_reminder_queue_api`
- `sfpcl_credit.tests.test_sap_customer_profile_repair`
- `sfpcl_credit.tests.test_sap_customer_profile_request_api`
- `sfpcl_credit.tests.test_scheduler_services`
- `sfpcl_credit.tests.test_seed_e2e_users`
- `sfpcl_credit.tests.test_servicing_as_of_owner_boundary`
- `sfpcl_credit.tests.test_servicing_postgresql_acceptance`
- `sfpcl_credit.tests.test_statement_evidence_owner_scope_closure`
