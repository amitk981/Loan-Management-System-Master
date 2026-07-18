# Risk Assessment

Risk level: High

The slice changes borrower-communication idempotency, provider-acceptance truth, asynchronous job
identity, concurrency control, application dependency direction, and an applied-data migration.
Failure could duplicate a borrower message, falsely mark an advice sent, strand a queued job, or
misclassify legacy evidence.

Controls and residual risk:

- Migration 0009 is additive/generalising and preserves every existing H5 job identity/history.
  Its data step refuses any non-verified/H6 legacy-partial outbox instead of upgrading it.
- Database uniqueness and shape constraints bind communication id, advice id, key, job kind,
  outbox presence, attempts, and all-or-none generic provider acceptance.
- PostgreSQL advisory transaction locks serialize absent-key generic/advice creation. Six
  five-caller races passed in two final executions.
- Manual/no-provider execution cannot return accepted/sent. Only Fake or a configured external
  adapter can produce accepted truth; generic acceptance is retained before final Communication
  mutation and advice retains its existing protected outbox/attempt/final chain.
- Static/runtime tests reject the removed disbursement-owner-to-process registration/import seam.
- No real provider, paid service, deployment, protected file, source document, money, loan,
  transfer, register, checklist, repayment, portal, or frontend behavior was invoked or changed.

Residual risk is bounded to independent full-suite/coverage validation and future H8 worker crash
recovery. H8 remains explicitly responsible for runtime discovery, on-commit enqueue, leases,
stale-running recovery, and crash-window integration; H7 does not claim those capabilities.
