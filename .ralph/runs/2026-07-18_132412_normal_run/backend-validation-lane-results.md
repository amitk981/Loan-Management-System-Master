# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 263
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/communications/models.py`
- `sfpcl_credit/communications/modules/communication_dispatcher.py`
- `sfpcl_credit/communications/services.py`
- `sfpcl_credit/disbursements/modules/disbursement_advice.py`
- `sfpcl_credit/disbursements/modules/disbursement_authorisation.py`
- `sfpcl_credit/disbursements/modules/disbursement_initiation.py`
- `sfpcl_credit/disbursements/modules/disbursement_workflow.py`
- `sfpcl_credit/disbursements/views.py`
- `sfpcl_credit/requirements.txt`
- `sfpcl_credit/tests/test_communication_receipt_owner_migration.py`
- `sfpcl_credit/tests/test_disbursement_advice_api.py`
- `sfpcl_credit/communications/migrations/0006_communication_delivery_job.py`
- `sfpcl_credit/processes/disbursement_advice_delivery.py`
- `sfpcl_credit/processes/tasks.py`
- `sfpcl_credit/tests/test_communication_dispatcher_jobs.py`

Impacted test labels:
- None
