# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 274
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/communications/migrations/0008_legacy_template_provenance_closure.py`
- `sfpcl_credit/communications/models.py`
- `sfpcl_credit/communications/modules/communication_dispatcher.py`
- `sfpcl_credit/communications/views.py`
- `sfpcl_credit/processes/communication_delivery.py`
- `sfpcl_credit/processes/tasks.py`
- `sfpcl_credit/tests/test_communication_channel_contract.py`
- `sfpcl_credit/tests/test_communication_job_migration.py`
- `sfpcl_credit/tests/test_communication_receipt_owner_migration.py`
- `sfpcl_credit/tests/test_communication_worker_runtime.py`
- `sfpcl_credit/communications/migrations/0013_exception_provider_vocabulary.py`

Impacted test labels:
- None
