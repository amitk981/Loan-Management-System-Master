# Review Packet: 2026-07-18_190359_normal_run

## Result
Complete pending independent Ralph validation

## Slice
009H8-communications-worker-runtime-and-crash-recovery-closure

## Recommended Next Action
Run independent full validation and coverage, then let the orchestrator commit. The four-slice
architecture-review cadence is due before 009I2.

## Outcome

The project now has a discoverable Celery application, explicit generic/advice execution task,
periodic due/recovery task, robust commit-only publication, configured adapter seam, and durable
fenced worker leases. Worker death cannot silently strand a row; retained acceptance is finalized
without redispatch, expired claims cannot mutate replacements, and legacy-partial advice remains
operator-blocked without mutation.

## Traceability

- Integrations §§7.3/10.2/10.5-10.6/22/33.3 say communications are asynchronous, retryable with
  backoff, status-bearing, and visible after exhaustion. `config/celery.py`, settings, runtime
  enqueue, thin tasks, dispatcher recovery, and the singular existing failure Notification implement
  that contract. Runtime discovery, eager success/failure, retry, exhaustion, publish-crash, and
  migration tests verify it.
- Codebase design §§34/40.1/42.4 say Celery tasks are thin and policy stays behind the communications
  module interface with a replaceable external adapter. The tasks only execute/project the deep
  `CommunicationDispatcher`; Manual/Fake/configured adapters remain the true external seam.
- H6/H7 require verified frozen provenance and stable provider/idempotency truth. Due/recovery
  selectors require `verified` + `frozen_before_dispatch`, while accepted generic/advice evidence is
  reconciled before terminal completion. Legacy and crash-window tests verify both positive and
  negative paths.
- The slice requires bounded concurrent claims and stale recovery. Migration 0010 adds claim token,
  expiry, recovery count, and recovered time; 10 PostgreSQL race methods pass twice with one provider
  acceptance and one terminal chain.

## Review notes

- Public HTTP response shapes and financial workflow facts are unchanged; API_CONTRACTS documents
  only the now-real runtime behavior.
- Operator/task evidence is allowlisted and excludes recipient, rendered body, provider identity or
  error text, bank/UTR, actor, idempotency key, request/network, and payload facts.
- 009I2, 009J, and 009K were re-read and already satisfy the sharpening standard. No speculative
  queue edits were made.
