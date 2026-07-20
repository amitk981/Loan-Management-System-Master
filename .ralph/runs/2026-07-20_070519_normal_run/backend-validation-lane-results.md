# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 294
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/settings.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/tests/test_servicing_postgresql_acceptance.py`
- `sfpcl_credit/interest/__init__.py`
- `sfpcl_credit/interest/apps.py`
- `sfpcl_credit/interest/migrations/0001_initial.py`
- `sfpcl_credit/interest/migrations/__init__.py`
- `sfpcl_credit/interest/models.py`
- `sfpcl_credit/interest/modules/__init__.py`
- `sfpcl_credit/interest/modules/interest_engine.py`
- `sfpcl_credit/interest/views.py`
- `sfpcl_credit/tests/test_interest_invoice_api.py`

Impacted test labels:
- None
