# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 304
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/communications/modules/communication_dispatcher.py`
- `sfpcl_credit/monitoring/models.py`
- `sfpcl_credit/monitoring/modules/dpd_monitoring.py`
- `sfpcl_credit/monitoring/modules/reminder_engine.py`
- `sfpcl_credit/processes/communication_delivery.py`
- `sfpcl_credit/tests/test_reminder_queue_api.py`
- `sfpcl_credit/tests/test_servicing_postgresql_acceptance.py`
- `sfpcl_credit/monitoring/migrations/0003_reminder_eligibility_decision.py`

Impacted test labels:
- None
