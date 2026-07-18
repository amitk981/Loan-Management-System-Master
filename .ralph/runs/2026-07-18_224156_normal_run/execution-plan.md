# Execution Plan

Selected slice: `009H9B-communication-final-attempt-and-exception-queue-closure`

## Boundary

- Change only the communications-owned worker recovery, exception ledger, operator projection,
  resolution interface, migration, and focused tests required by 009H9B.
- Preserve the retained `CommunicationDeliveryJob.attempts` and per-row `max_attempts` contract,
  H6 legacy exclusion, H7 provider/idempotency truth, and H8 fenced claims.
- Do not implement the channel/provider-attempt work owned by 009H9C or any frontend screen.

## Public interfaces and module depth

- Keep `CommunicationDispatcher.retry_failed` as the single scheduled-job interface for selecting
  and recovering due work. Under its existing job lock, exact-cap stale claims become terminal and
  create one exception; below-cap claims remain retryable without incrementing attempts.
- Add narrow dispatcher interfaces to list redacted exceptions and resolve one exception with a
  stale-write token. HTTP views authenticate and authorize only, then call those interfaces.
- Store one protected exception row per exhausted job. Link at most one existing operator
  notification to that row; retain append-only audit and workflow evidence for resolution.
- Exhaustion never resets attempts or marks a communication sent. Since the source grants no retry
  beyond `max_attempts`, a retry resolution fails closed and manual closure remains available.

## TDD tracer bullets

1. RED: copy the architecture-review exact-cap crash probe into the retained worker test module.
   GREEN: recover the locked stale job to terminal `failed`, preserving attempts, fencing its claim,
   creating one exception and one notification, and returning no due job.
2. RED/GREEN incrementally cover below-cap recovery, repeated scans, stale claim losers, and
   malformed/absent exception evidence through dispatcher interfaces.
3. RED/GREEN add the redacted exception projection for generic, advice, and safe failure classes;
   assert forbidden recipient/content/provider/financial/key/payload/network facts never appear.
4. RED/GREEN add authorised manual resolution, denied ownership, stale resolution, retry-policy
   denial, and accepted-provider evidence closure without resend or fabricated delivery.
5. Add PostgreSQL five-scanner/five-worker race acceptance and run it twice when the configured
   PostgreSQL test database is available; otherwise preserve collection/local evidence for the
   orchestrator's declared `postgresql-five-race-acceptance` gate.

## Migration and contract

- Add at most one communications migration for the exception owner and its one-job/terminal-state
  constraints.
- Add operator list/detail-resolution routes using existing standard response/error conventions.
- Update `docs/working/API_CONTRACTS.md` and the selected epic digest with the implemented contract.

## Verification and evidence

- Save every focused RED and GREEN command output under
  `.ralph/runs/2026-07-18_224156_normal_run/evidence/terminal-logs/`.
- Run focused communications tests, Django check, migration sync, and Python compilation with
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python`; do not run the full backend suite/coverage.
- Inspect migration state, targeted diff hunks/stat, and protected-path status.
- Complete `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; leave mechanical state,
  slice status, changed-files, handoff, commit, merge, and push work to the orchestrator.
