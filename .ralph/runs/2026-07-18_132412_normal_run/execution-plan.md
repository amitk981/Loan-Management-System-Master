# Execution Plan

Selected slice: `009H5-communications-dispatcher-job-and-dependency-closure`

## Scope and owner seams

- Keep disbursement authority and locked financial/current-context resolution in
  `disbursements`; move the cross-owner composition into a shallow `processes`
  coordinator that exchanges primitive immutable context only.
- Make `communications.modules.communication_dispatcher.CommunicationDispatcher`
  the one public owner for template preparation, durable queueing, sending, accepted
  finalization, and failed-job retry. Route the existing generic communication API
  and disbursement advice through that interface and reject runtime imports in either
  direction between `communications` and `disbursements`.
- Add at most one communications-owned migration for an advice communication job with
  frozen actor/role/team/request/network/context identity, queued/running/retrying/sent/
  failed lifecycle, bounded attempts/backoff, safe bounded error classification, and
  protected links to the existing 009H4 outbox/final chain.
- Pin Celery as the source-required worker boundary and keep the task entry point thin:
  the task calls the dispatcher module; tests invoke that same task contract eagerly
  with Manual/Fake/Future adapters and no network provider.

## TDD tracer cycles

1. RED then GREEN: public send-advice request queues one job, invokes no provider,
   returns safe queued truth, replays the exact request to the same job, and conflicts
   on changed request/evidence without creating sent or downstream truth.
2. RED then GREEN: task execution freezes running state, uses the retained outbox and
   adapter idempotency identity, finalizes accepted delivery exactly once, and exposes
   sent only after the complete 009H4 receipt/Communication/action/audit/workflow chain.
3. RED then GREEN: timeout/rejection/malformed/crash outcomes retain only safe bounded
   retry evidence, schedule bounded backoff, exhaust honestly to failed plus an
   operator-visible task, and recover pre/post-acceptance without duplicate delivery.
4. RED then GREEN: generic template/send behavior delegates through the dispatcher;
   static dependency/source tests reject duplicate render/send policy and all runtime
   `communications`↔`disbursements` or `shared`→business edges.
5. Add the declared PostgreSQL five-caller queue and five-worker execution races, run
   both methods twice where the socket is available, and preserve the sandbox skip as
   honest evidence otherwise.

## Verification and closeout

- Save each focused failing and passing command under
  `evidence/terminal-logs/`; use only the orchestrator venv Python path.
- Run impacted communications/disbursement/scheduler tests, Django check,
  `makemigrations --check`, and Python compilation. Do not run the complete backend
  suite or coverage locally.
- Update the working API contract and Epic 009 digest, mark 009H5 complete, sharpen
  the next one or two Not Started slices only when source material already opened
  supplies a concrete improvement, then update state, progress, handoff, changed-files,
  risk assessment, review packet, and final summary.
