# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: high-risk slice
- Enforcement policy: selective
- Slice risk: high
- Candidate completion ordinal: 313
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/monitoring/modules/quarterly_mis.py`
- `sfpcl_credit/tests/servicing_builders.py`
- `sfpcl_credit/tests/test_epic010_terminal_owner_finalizer.py`

Impacted test labels:
- `sfpcl_credit.tests.test_epic010_terminal_owner_finalizer`
- `sfpcl_credit.tests.test_dpd_integrity_closure`
- `sfpcl_credit.tests.test_dpd_monitoring_api`
- `sfpcl_credit.tests.test_quarterly_mis_api`
- `sfpcl_credit.tests.test_reminder_queue_api`
- `sfpcl_credit.tests.test_servicing_as_of_owner_boundary`
- `sfpcl_credit.tests.test_servicing_postgresql_acceptance`
- `sfpcl_credit.tests.test_dashboard_api`
