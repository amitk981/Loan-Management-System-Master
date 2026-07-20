# Failure Summary

- Run: 2026-07-21_020140_normal_run
- Mode: normal_run
- Slice: 010J2-reminder-eligibility-and-delivery-integrity-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
postgresql-acceptance-results.md:- FAIL: first independent run did not satisfy the slice contract and exact count.
postgresql-acceptance-results.md:- FAIL: second independent run did not satisfy the slice contract and exact count.
postgresql-acceptance-results.md:- FAIL: PostgreSQL environment evidence is missing.
```

## Last 50 lines: postgresql-acceptance-results.md

```
# PostgreSQL Acceptance Results

- Contract expected tests: 5
- Contract labels:
  - sfpcl_credit.tests.test_servicing_postgresql_acceptance.ReminderDeliveryIntegrityPostgreSQLAcceptanceTests
- FAIL: first independent run did not satisfy the slice contract and exact count.
- FAIL: second independent run did not satisfy the slice contract and exact count.
- FAIL: PostgreSQL environment evidence is missing.
```

## Changed files (git status)

```
docs/working/API_CONTRACTS.md
sfpcl_credit/communications/modules/communication_dispatcher.py
sfpcl_credit/monitoring/models.py
sfpcl_credit/monitoring/modules/dpd_monitoring.py
sfpcl_credit/monitoring/modules/reminder_engine.py
sfpcl_credit/processes/communication_delivery.py
sfpcl_credit/tests/test_reminder_queue_api.py
sfpcl_credit/tests/test_servicing_postgresql_acceptance.py
.ralph/runs/2026-07-21_020140_normal_run/
sfpcl_credit/monitoring/migrations/0003_reminder_eligibility_decision.py
```
