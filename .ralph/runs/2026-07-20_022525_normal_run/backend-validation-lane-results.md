# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 290
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/loans/models.py`
- `sfpcl_credit/loans/modules/bank_statement_matching.py`
- `sfpcl_credit/loans/modules/direct_repayment_posting.py`
- `sfpcl_credit/tests/test_bank_statement_matching_api.py`
- `sfpcl_credit/tests/test_direct_repayment_posting_api.py`
- `sfpcl_credit/tests/test_repayment_adjustment_api.py`
- `sfpcl_credit/loans/migrations/0007_statement_evidence_owner_scope_closure.py`
- `sfpcl_credit/tests/test_statement_evidence_boundary_postgresql.py`
- `sfpcl_credit/tests/test_statement_evidence_owner_migration.py`
- `sfpcl_credit/tests/test_statement_evidence_owner_scope_closure.py`

Impacted test labels:
- None
