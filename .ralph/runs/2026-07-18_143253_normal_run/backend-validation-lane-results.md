# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 264
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/communications/models.py`
- `sfpcl_credit/communications/modules/communication_dispatcher.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/disbursements/modules/disbursement_advice.py`
- `sfpcl_credit/members/portal_views.py`
- `sfpcl_credit/communications/migrations/0007_portal_advice_download_capability.py`
- `sfpcl_credit/processes/portal_disbursement_status.py`
- `sfpcl_credit/tests/test_portal_disbursement_status_api.py`

Impacted test labels:
- None
