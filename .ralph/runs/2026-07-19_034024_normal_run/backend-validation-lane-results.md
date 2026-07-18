# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 276
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/disbursements/views.py`
- `sfpcl_credit/processes/disbursement_workspace.py`
- `sfpcl_credit/tests/test_disbursement_workspace_api.py`

Impacted test labels:
- None
