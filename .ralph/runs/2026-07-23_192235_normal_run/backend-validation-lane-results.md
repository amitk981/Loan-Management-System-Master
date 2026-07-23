# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: shared backend root changed: processes
- Enforcement policy: selective
- Slice risk: medium
- Candidate completion ordinal: 334
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/communications/services.py`
- `sfpcl_credit/compliance/modules/grievance_workflow.py`
- `sfpcl_credit/config/settings.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/members/portal_views.py`
- `sfpcl_credit/processes/portal_communications.py`
- `sfpcl_credit/tests/test_portal_communications_api.py`

Impacted test labels:
- `sfpcl_credit.tests.test_portal_communications_api`
- `sfpcl_credit.tests.test_approval_case_routing_api`
- `sfpcl_credit.tests.test_communication_advice_persistence`
- `sfpcl_credit.tests.test_communication_channel_contract`
- `sfpcl_credit.tests.test_communication_dispatcher_jobs`
- `sfpcl_credit.tests.test_communication_job_migration`
- `sfpcl_credit.tests.test_communication_receipt_owner_migration`
- `sfpcl_credit.tests.test_communication_worker_runtime`
- `sfpcl_credit.tests.test_communications_api`
- `sfpcl_credit.tests.test_compliance_postgresql_acceptance`
- `sfpcl_credit.tests.test_compliance_task_engine`
- `sfpcl_credit.tests.test_content_templates_api`
- `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance`
- `sfpcl_credit.tests.test_direct_repayment_posting_api`
- `sfpcl_credit.tests.test_disbursement_advice_api`
- `sfpcl_credit.tests.test_disbursement_authorisation_api`
- `sfpcl_credit.tests.test_disbursement_initiation_api`
- `sfpcl_credit.tests.test_disbursement_transfer_success_api`
- `sfpcl_credit.tests.test_epic010_terminal_owner_finalizer`
- `sfpcl_credit.tests.test_final_documentation_approval_api`
- `sfpcl_credit.tests.test_grievance_workflow`
- `sfpcl_credit.tests.test_interest_capitalisation_api`
- `sfpcl_credit.tests.test_interest_invoice_api`
- `sfpcl_credit.tests.test_interest_rate_config_api`
- `sfpcl_credit.tests.test_kyc_review_api`
- `sfpcl_credit.tests.test_kyc_review_tracker`
- `sfpcl_credit.tests.test_noc_api`
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
