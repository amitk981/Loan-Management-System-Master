# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 257
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/communications/adapters.py`
- `sfpcl_credit/communications/models.py`
- `sfpcl_credit/disbursements/models.py`
- `sfpcl_credit/disbursements/modules/disbursement_advice.py`
- `sfpcl_credit/communications/migrations/0004_advice_outbox_and_receipt_owner.py`
- `sfpcl_credit/tests/test_communication_advice_persistence.py`
- `sfpcl_credit/tests/test_communication_receipt_owner_migration.py`

Impacted test labels:
- None
