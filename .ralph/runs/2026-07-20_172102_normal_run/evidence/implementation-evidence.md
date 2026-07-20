# 010J Reminder Queue Evidence

## Behavior evidence

| Behavior | Permanent test | Evidence |
|---|---|---|
| Quarter-end eligibility, boundary, automatic dedupe, exact replay | `sfpcl_credit.tests.test_reminder_queue_api.ReminderQueueApiTests` | `terminal-logs/reminder-api-matrix.log` |
| Manual phone outcomes/follow-up, multiple calls, no provider row | `ReminderQueueApiTests.test_phone_log_retains_outcome_and_follow_up_without_provider_communication` | `terminal-logs/reminder-phone-red.log`, `terminal-logs/reminder-phone-green.log` |
| Stale resolved loan is cancelled before dispatch | `ReminderQueueApiTests.test_stale_electronic_reminder_is_cancelled_before_send` | `terminal-logs/reminder-stale-send-red.log`, `terminal-logs/reminder-stale-send-green.log` |
| Communications worker supplies honest provider-accepted state | `ReminderQueueApiTests.test_electronic_send_uses_worker_and_projects_provider_accepted_truth` | `terminal-logs/reminder-api-matrix.log` |
| Permission, scope, approved template and contact fail closed | `ReminderQueueApiTests.test_permission_contact_and_template_fail_closed_without_reminder`, `test_out_of_scope_loan_is_not_disclosed_by_manual_reminder_endpoint` | `terminal-logs/reminder-api-matrix.log` |
| Concurrent run/send retain one automatic reminder and job | `sfpcl_credit.tests.test_servicing_postgresql_acceptance.ReminderQueuePostgreSQLAcceptanceTests` (2 tests) | `terminal-logs/postgresql-reminder-acceptance-1.log`, `terminal-logs/postgresql-reminder-acceptance-2.log` |

## Reverse-consumer and schema evidence

- `terminal-logs/reverse-consumer-tests.log`: 59 DPD, schedule/ledger, allocation, communications
  dispatcher/job, retry and crash-recovery tests passed.
- `terminal-logs/backend-model-checks.log`: Django check passed and migrations are synchronized.
- RED evidence records the missing model, phone route, and electronic creation behavior before each
  tracer implementation. GREEN evidence records explicit zero exits.

No frontend files changed, no provider was called outside the repository's deterministic test
adapter, and no recipient/message/provider-sensitive values are included in these summaries.
