# Review Packet: 2026-07-18_132412_normal_run

## Result
Complete pending independent orchestrator validation.

## Slice
009H5-communications-dispatcher-job-and-dependency-closure

## Outcome

The public advice request is queue-first and provider-free. A communications-owned job freezes the
009H4 outbox plus actor/request context, and the shallow process coordinator later re-resolves
disbursement authority/current facts before the dispatcher calls Manual/Fake/Future adapters and
finalizes exactly one protected chain. Generic `/communications/send/` now delegates its template,
render, Communication, notification, and audit behavior to the same dispatcher owner.

## Traceability

- The source says BR-054/M08-FR-010 advice is shared/generated after disbursement; code exposes it
  as sent only after accepted worker finalization; verified by
  `test_worker_acceptance_finalizes_job_and_advice_once` and MP14 contract wording.
- Integrations §§10.2/10.5/10.6/33.3 say asynchronous queue plus retry/backoff; code persists
  queued/running/retrying/sent/failed with three bounded attempts and a safe exhaustion task;
  verified by `test_send_advice_request_queues_without_calling_provider` and
  `test_provider_timeout_retries_with_backoff_then_fails_safely`.
- Codebase-design §§20.2-20.6/40.1-40.2 say one dispatcher owns templates/provider/status/audit and
  tasks contain no policy; generic and advice paths now delegate that owner and the task calls the
  process coordinator; verified by generic API tests and the static dependency test.
- Integrations §21 says communication idempotency uses `communication_id`; the retained 009H4
  outbox/provider attempt remains the identity, verified by two five-caller queue and two
  five-worker PostgreSQL races.

## Review focus

Review the migration constraint/lifecycle, the process coordinator's two-phase provider/finalize
flow, retry classifications, safe evidence fields, and the Celery worker/beat configuration after
the newly pinned dependency is installed. No frontend or source document changed.

## Recommended Next Action

Run independent full coverage and all configured gates, then commit/merge through Ralph. If green,
execute 009I followed by 009J.
