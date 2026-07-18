# Execution Plan

Selected slice: `009H7-communications-dispatcher-interface-and-idempotency-closure`

## Scope and interface

- Deepen `communications.modules.communication_dispatcher.CommunicationDispatcher` to expose the
  source interface: `create_from_template`, `send(communication_id, idempotency_key)`, and
  `retry_failed`.
- Route generic `/api/v1/communications/send/` and disbursement advice through that same interface.
  Keep advice authority/current-evidence preparation and terminal financial finalization behind the
  top-level process coordinator.
- Require a trimmed, nonblank `Idempotency-Key` of at most 255 characters for both HTTP actions and
  bind it to communication/advice identity, frozen payload, and current actor. Exact replay returns
  retained truth; missing, changed, or cross-object reuse is zero-write validation/conflict.
- Generalise the retained `CommunicationDeliveryJob` in one communications migration, preserving
  existing row ids/status/attempts and excluding `legacy_0005` / `ambiguous_legacy` outboxes from
  attachment, replay, or upgrade.
- Replace default manual-provider acceptance with honest pending/manual-confirmation truth. Only an
  explicitly configured external adapter or test fake may return accepted provider evidence.
- Remove the lazy `disbursements -> processes -> disbursements` import cycle. Views/tasks call the
  process coordinator; business-owner modules import neither each other nor their coordinator.

## TDD tracer bullets

1. Copy the architecture-review missing-`send` probe into retained public tests and make it fail.
   Implement the smallest public dispatcher interface that routes generic send through the retained
   job/outbox seam.
2. Add one missing/exact/changed/cross-object idempotency case at a time for generic HTTP send, then
   the equivalent advice HTTP matrix; save each focused RED and GREEN command output.
3. Add migration tests proving ids/history/status/attempt preservation and H6 provenance exclusion;
   implement the single generalising migration.
4. Add static/runtime import-graph tests for lazy/callback/registry/package-level cycles; move
   composition to the process seam without changing owner decisions.
5. Add manual/default negative truth tests, then preserve fake/configured-provider exact replay and
   safe failure behavior.
6. Add and run the declared PostgreSQL five-caller generic/advice races twice.

## Verification and closeout

- Run focused impacted backend tests with
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python`, then Django check, migration sync, and Python
  compilation. Do not run the complete backend suite or coverage locally.
- Run frontend typecheck, lint, tests, and build because Ralph requires repository-wide gates even
  though this slice has no frontend changes.
- Save terminal evidence, migration/schema evidence, changed-files, risk assessment, review packet,
  final summary, and update API contracts, Epic 009 digest, handoff, progress, state, and slice
  status. Recheck/sharpen the next one or two Not Started slices using already-opened source facts.
