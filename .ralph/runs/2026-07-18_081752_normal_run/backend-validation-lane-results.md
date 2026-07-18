# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 258
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/disbursements/modules/disbursement_advice.py`
- `sfpcl_credit/tests/test_communication_advice_persistence.py`
- `sfpcl_credit/tests/test_disbursement_advice_api.py`
- `sfpcl_credit/communications/modules/__init__.py`
- `sfpcl_credit/communications/modules/communication_dispatcher.py`
- `sfpcl_credit/disbursements/modules/disbursement_advice_context.py`

Impacted test labels:
- None
