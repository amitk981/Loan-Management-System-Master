# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 272
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/communications/adapters.py`
- `sfpcl_credit/communications/models.py`
- `sfpcl_credit/communications/modules/communication_dispatcher.py`
- `sfpcl_credit/communications/services.py`
- `sfpcl_credit/config/settings.py`
- `sfpcl_credit/processes/communication_delivery.py`
- `sfpcl_credit/processes/disbursement_advice_delivery.py`
- `sfpcl_credit/processes/tasks.py`
- `sfpcl_credit/tests/test_communication_dispatcher_jobs.py`
- `sfpcl_credit/tests/test_communication_job_migration.py`
- `sfpcl_credit/tests/test_communication_worker_runtime.py`
- `sfpcl_credit/tests/test_communications_api.py`
- `sfpcl_credit/tests/test_disbursement_advice_api.py`
- `sfpcl_credit/communications/migrations/0012_generic_provider_evidence.py`
- `sfpcl_credit/tests/test_communication_channel_contract.py`

Impacted test labels:
- None
