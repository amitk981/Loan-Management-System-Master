# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 259
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/communications/modules/communication_dispatcher.py`
- `sfpcl_credit/disbursements/modules/disbursement_advice.py`
- `sfpcl_credit/tests/test_communication_advice_persistence.py`
- `sfpcl_credit/tests/test_disbursement_advice_api.py`

Impacted test labels:
- None
