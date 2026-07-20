# Backend Validation Lane Results

- Authoritative lane: full
- Shadow recommendation: full
- Recommendation reason: high-risk backend slice
- Enforcement: full configured backend gates remain mandatory
- Slice risk: high
- Candidate completion ordinal: 303
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/loans/models.py`
- `sfpcl_credit/monitoring/modules/dpd_monitoring.py`
- `sfpcl_credit/tests/test_servicing_postgresql_acceptance.py`
- `sfpcl_credit/loans/migrations/0009_dpd_pointer_integrity.py`
- `sfpcl_credit/loans/modules/dpd_source_decision.py`
- `sfpcl_credit/tests/test_dpd_integrity_closure.py`

Impacted test labels:
- None
