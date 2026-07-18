# Slice 009H8: Communications Worker Runtime and Crash Recovery Closure

## Status
Complete

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Make queued communication jobs discoverable and executable by the deployed asynchronous worker,
including bounded recovery of a worker that dies after claiming a job.

## Depends On
- 009H7

## Source / Review References
- `docs/source/integrations.md` §§7.3, 10.2-10.6, 21, 22, 29, and 33.3
- `docs/source/codebase-design.md` §§20.6, 34, 40.1, and 42.4
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-18_152831_architecture_review`
- Review probe `evidence/review-probes/review_contract_probes.py`

## Concrete Requirements
1. Configure the pinned Celery application in the Django project, explicitly register the top-level
   communications task, and supply environment-driven broker/result/runtime settings with safe test
   defaults. Queue creation schedules execution only through `transaction.on_commit`; no request
   invokes a provider.
2. Register a periodic due/retry/recovery schedule. The worker atomically claims bounded batches,
   and concurrent workers retain one claim/provider identity/final chain. A job left `running` by
   process death has an explicit lease/heartbeat or equivalent durable timeout and becomes safely
   retryable without resetting attempts or redispatching accepted evidence.
3. Preserve H7's generic dispatcher interface and H4/H6 provider truth. Crash before provider,
   after provider acceptance, before local commit, during acknowledgement, and during retry
   scheduling all recover exactly; accepted truth is never sent again. Claim/recovery selectors
   exclude H6 `legacy_0005`/`legacy_partial` outboxes even if a stale retained job points at one,
   and must not mutate that retained history while reporting the row as operator-blocked.
4. Expose operator-safe queued/running/retrying/sent/failed/recovered evidence without recipient,
   template body, provider id/error, bank/UTR, token, or internal payload leakage. Exhaustion creates
   one reachable task and never silently strands a row.

## Test Cases
- Copy the missing-runtime review probe failing first. Assert the configured app discovers the task,
  queue commit emits one async signature, rollback emits none, and the periodic schedule is loaded.
- Run eager/in-memory worker integration for generic and advice success/failure without network;
  verify retry ETA/backoff, exhaustion, restart, stale-running recovery, and both crash windows.
- Two five-caller queue races, two five-worker claim races, and stale-worker recovery races run twice
  on PostgreSQL with one provider acceptance and one terminal chain.

## Runtime Capabilities

postgresql-five-race-acceptance

## Database / Migration Impact
At most one communications migration for an explicit claim lease/heartbeat if the retained job
cannot represent crash recovery truthfully.

## Risk Level
High

## Acceptance Criteria
- A committed queued row is eventually discoverable/executable by the configured worker runtime.
- Worker death cannot strand a job or duplicate an accepted communication.

## Done Checklist
- [x] Execution plan written
- [x] Runtime discovery/crash probes written failing first
- [x] Celery app, enqueue, schedule, and recovery implemented
- [x] Eager/in-memory and PostgreSQL races green twice
- [x] No real external provider invoked in tests/evidence
- [x] Risk, evidence, handoff, state, contract, and digest updated
- [x] Commit delegated to the orchestrator after gates
