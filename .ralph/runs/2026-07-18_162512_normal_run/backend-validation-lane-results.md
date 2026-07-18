# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 266
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/communications/models.py`
- `sfpcl_credit/communications/modules/communication_dispatcher.py`
- `sfpcl_credit/processes/advice_evidence_migration.py`
- `sfpcl_credit/tests/test_communication_receipt_owner_migration.py`
- `sfpcl_credit/tests/test_disbursement_advice_api.py`
- `sfpcl_credit/tests/test_portal_disbursement_status_api.py`
- `sfpcl_credit/communications/migrations/0008_legacy_template_provenance_closure.py`

Impacted test labels:
- None
