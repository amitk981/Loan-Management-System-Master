# Ralph Handoff

## Last Run

2026-07-18_190359_normal_run

## Current Status

009H8 is complete pending independent validation. The pinned Celery application discovers explicit
generic/advice execution and periodic due/recovery tasks. Generic and advice queue creation publishes
one named signature only after commit; rollback publishes none, and a broker-publish crash leaves the
committed job discoverable by the periodic scan. Broker/result/provider/runtime values are
environment-driven with inert in-memory local defaults and an honest no-provider adapter.

Migration 0010 adds a fenced UUID claim, expiry, recovery count, and recovered timestamp without
rewriting retained attempts. Stale workers recover under bounded row locks, keep attempt history,
and cannot mutate a replacement claim. Retained provider acceptance finalizes after restart without
redispatch. H6 legacy-partial outboxes are excluded and remain unchanged while safe operator evidence
reports `operator_blocked`; ordinary evidence never exposes recipient/body/provider/financial/token/
actor/request/payload truth. Exhaustion keeps its singular reachable operator task.

The missing-runtime and crash probes failed first. Thirty-seven focused runtime/dispatcher/API/
migration tests pass with four expected PostgreSQL skips. Ten PostgreSQL queue/claim/stale-recovery
races pass in two final executions after correcting a PostgreSQL-only nullable-join lock to target
the job row. Django check and migration sync pass; complete backend coverage remains delegated to
the orchestrator. The unchanged frontend gates are recorded in this run's evidence.

## Next Run

The four-slice architecture-review cadence is now due. After that review, run 009I2 before 009J and
009K. 009I2, 009J, and 009K were re-read; all remain concrete, dependency-correct slices with exact
owner truth, role/action, validation, frontend fidelity, and browser/evidence requirements, so no
speculative sharpening edit was made.
