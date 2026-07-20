# Risk Assessment

Risk level: High

- Selected slice: CR-014-rate-current-date-terminal-finalizer
- Financial/data-integrity risk: the change updates the mutable Loan Account current-rate scalar.
  Mitigations are a server-owned date, account row locking, one immutable account/version decision,
  globally unique idempotency keys, an audit one-to-one, retained actor/role evidence, and unchanged
  append-only rate/consumption history.
- Concurrency risk: same-account exact/changed keys, cross-account keys, bounded portfolio runs, and
  competing runs are represented by exactly five PostgreSQL acceptance tests. The local database is
  SQLite, so those tests were collected and skipped locally; Ralph must run the declared class twice
  on PostgreSQL before committing.
- Read-boundary risk: list/detail now converge only the selected bounded window and bulk-refresh the
  scalar so stale rows remain countable without introducing an N+1 query regression. The complete
  Loan Account read module and its query ceiling passed locally.
- Runtime risk: one Celery task delegates to the bounded owner, but no new beat cadence or business
  calendar was introduced. List/detail are also production-owned invocation paths.
- Migration risk: additive table only; no retained Loan Account, rate history, invoice, accrual, or
  capitalisation data is rewritten.
- Permission/audit risk: manual publication requires `config.interest_rate.manage`; production due
  publication is truthfully attributed to the system with its invocation path. Manual publication
  also requires the loan-owned account scope check; no historical approver is impersonated.
- Aggregate-boundary risk: the configuration owner resolves the effective rate and retains the
  decision, while all current-scalar selection/mutation is delegated to a loan-owned facade. A
  retained decision repairs a subsequently stale scalar without creating a second decision.
- Rollback: application code and the additive migration can be reverted before production use. Any
  decisions written after deployment are financial audit evidence and must not be deleted casually.

Manual review required: independent High-risk validation and twice-run PostgreSQL acceptance.
