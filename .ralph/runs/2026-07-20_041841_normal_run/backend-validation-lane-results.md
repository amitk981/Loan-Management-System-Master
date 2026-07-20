# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 292
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/configurations/models.py`
- `sfpcl_credit/configurations/views.py`
- `sfpcl_credit/configurations/migrations/0006_interestrateconfig_borrowerratenoticeobligation_and_more.py`
- `sfpcl_credit/configurations/modules/interest_rate_configuration.py`
- `sfpcl_credit/tests/test_interest_rate_config_api.py`

Impacted test labels:
- None
