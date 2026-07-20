# PostgreSQL Acceptance

The declared test label is
`sfpcl_credit.tests.test_interest_rate_config_api.InterestRateActivationPostgreSQLAcceptanceTests`
with exactly three tests.

- `terminal-logs/postgresql-acceptance-real-run-1.log`: 3 tests executed, 3 passed, zero skips,
  `EXIT_STATUS=0`.
- `terminal-logs/postgresql-acceptance-real-run-2.log`: 3 tests executed, 3 passed, zero skips,
  `EXIT_STATUS=0`.

Each run used the repository's PostgreSQL-only settings and a distinct isolated test database, which
Django destroyed after success. The races prove one effective winner for competing versions, one
activation history under exact concurrent replay, and one loan-level obligation with one email and
one SMS communication under competing activation calls.

The earlier `postgresql-acceptance-run-1.log` and `postgresql-acceptance-run-2.log` are intentionally
retained local SQLite collection probes; they show three tests discovered and skipped because SQLite
cannot provide the authoritative row-lock behavior. They are not claimed as PostgreSQL evidence.
