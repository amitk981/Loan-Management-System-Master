# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 267
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/communications/adapters.py`
- `sfpcl_credit/communications/models.py`
- `sfpcl_credit/communications/modules/communication_dispatcher.py`
- `sfpcl_credit/communications/services.py`
- `sfpcl_credit/communications/views.py`
- `sfpcl_credit/disbursements/modules/disbursement_advice.py`
- `sfpcl_credit/disbursements/modules/disbursement_workflow.py`
- `sfpcl_credit/disbursements/views.py`
- `sfpcl_credit/processes/disbursement_advice_delivery.py`
- `sfpcl_credit/processes/tasks.py`
- `sfpcl_credit/tests/test_communication_advice_persistence.py`
- `sfpcl_credit/tests/test_communication_dispatcher_jobs.py`
- `sfpcl_credit/tests/test_communications_api.py`
- `sfpcl_credit/tests/test_disbursement_advice_api.py`
- `sfpcl_credit/tests/test_notifications_api.py`
- `sfpcl_credit/communications/migrations/0009_generic_delivery_job_identity.py`
- `sfpcl_credit/processes/communication_delivery.py`
- `sfpcl_credit/tests/test_communication_job_migration.py`

Impacted test labels:
- None
