# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: shared backend root changed: shared
- Enforcement policy: selective
- Slice risk: medium
- Candidate completion ordinal: 359
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/dashboard/services.py`
- `sfpcl_credit/deployment_smoke.py`
- `sfpcl_credit/identity/management/commands/seed_e2e_users.py`
- `sfpcl_credit/ops.py`
- `sfpcl_credit/shared/management/commands/smoke_check.py`
- `sfpcl_credit/tests/test_health_api.py`
- `sfpcl_credit/tests/test_seed_e2e_users.py`
- `sfpcl_credit/tests/test_smoke_check_command.py`

Impacted test labels:
- `sfpcl_credit.tests.test_health_api`
- `sfpcl_credit.tests.test_seed_e2e_users`
- `sfpcl_credit.tests.test_smoke_check_command`
- `sfpcl_credit.tests.test_catalogue_seed`
- `sfpcl_credit.tests.test_dashboard_api`
- `sfpcl_credit.tests.test_quarterly_mis_api`
