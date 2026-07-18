# Risk Assessment

Risk level: High.

The slice changes when a borrower communication becomes terminal truth, adds a durable worker job
and one communications migration, and retries an external-side-effect boundary. The main risks are
duplicate borrower messages, provider acceptance followed by local rollback, stale financial facts
being finalized later, unsafe error/recipient leakage, infinite retry, and an app dependency cycle.

Controls implemented:

- HTTP freezes one outbox/job under locks and performs zero provider calls; exact replay returns the
  same identity and changed/current-evidence drift fails closed.
- Every worker attempt re-authorises the frozen actor against current disbursement evidence, uses
  the 009H4 stable provider identity, and marks sent only after the protected final chain exists.
- Attempts are database-bounded to three with safe codes/backoff; exhaustion produces one operator
  task and no Communication, receipt, or borrower-visible sent fact.
- General job/task evidence omits recipient, rendered content, full bank reference, provider id,
  and exception text. Static tests reject direct communications↔disbursements Python imports.
- Two queue races and two worker races passed on PostgreSQL; retained migration tests restore the
  current graph after historical projections.

Residual risk: Celery 5.5.3 is pinned but absent from the isolated agent venv, so local evidence used
the same callable task entry point without a broker. The orchestrator installs pinned dependencies
before validation; deployment still needs its normal worker/beat configuration. No real provider,
real borrower data, deployment, or network communication was used.
