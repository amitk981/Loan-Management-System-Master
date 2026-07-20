# Review Closure Evidence

## Finding Evidence

| Finding ID | Root ID | Permanent Test | RED Evidence | GREEN Evidence |
|---|---|---|---|---|
| AR-010-REMINDER-001 | ROOT-010-REMINDER-DELIVERY-OWNER | sfpcl_credit.tests.test_reminder_queue_api.ReminderQueueApiTests.test_calendar_anniversary_not_day_count_controls_leap_year_eligibility | evidence/terminal-logs/reminder-calendar-red.log | evidence/terminal-logs/reminder-calendar-green.log |

## Acceptance Evidence

| Acceptance ID | Test | Evidence |
|---|---|---|
| AC-REM2-1 | sfpcl_credit.tests.test_reminder_queue_api.ReminderQueueApiTests.test_calendar_anniversary_not_day_count_controls_leap_year_eligibility | evidence/terminal-logs/reminder-calendar-green.log |
| AC-REM2-2 | sfpcl_credit.tests.test_reminder_queue_api.ReminderQueueApiTests.test_newer_still_overdue_snapshot_preserves_retained_quarter_send | evidence/terminal-logs/reminder-serviceability-green.log |
| AC-REM2-3 | sfpcl_credit.tests.test_reminder_queue_api.ReminderQueueApiTests.test_changed_send_key_returns_conflict_and_retains_one_delivery_job | evidence/terminal-logs/reminder-idempotency-green.log |
| AC-REM2-4 | sfpcl_credit.tests.test_reminder_queue_api.ReminderQueueApiTests.test_mixed_batch_retains_success_and_discloses_late_contact_failure | evidence/terminal-logs/reminder-batch-green.log |
| AC-REM2-5 | sfpcl_credit.tests.test_servicing_postgresql_acceptance.ReminderDeliveryIntegrityPostgreSQLAcceptanceTests.test_provider_execution_rechecks_serviceability_and_reverse_consumers | evidence/terminal-logs/reminder-postgresql-run-1.log |

The exact five-test PostgreSQL class also passed independently a second time in
`evidence/terminal-logs/reminder-postgresql-run-2.log`; the non-secret server facts are retained in
`evidence/postgresql-environment-validation.md`.
