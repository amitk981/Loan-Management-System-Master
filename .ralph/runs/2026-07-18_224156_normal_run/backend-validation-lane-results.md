# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 271
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/communications/models.py`
- `sfpcl_credit/communications/modules/communication_dispatcher.py`
- `sfpcl_credit/communications/services.py`
- `sfpcl_credit/communications/views.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/tests/test_communication_worker_runtime.py`
- `sfpcl_credit/communications/migrations/0011_communication_exception_queue.py`

Impacted test labels:
- None
