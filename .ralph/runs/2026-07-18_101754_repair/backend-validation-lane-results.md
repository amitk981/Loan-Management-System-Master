# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 260
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/tests/test_credit_model_ownership_migration.py`
- `sfpcl_credit/tests/test_legal_checklist_migration_anchor.py`
- `sfpcl_credit/legal_documents/migrations/0015_checklist_constraint_state_owner_anchor.py`
- `sfpcl_credit/shared/migration_state_guard.py`

Impacted test labels:
- None
