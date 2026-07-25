# Risk Assessment

Risk level: Medium

- Selected slice: 012H-deployment-readiness-and-smoke-checks
- Mode: normal_run
- Database/model impact: none; `makemigrations --check --dry-run` is clean.
- Public surface: two unauthenticated, GET-only infrastructure endpoints return only
  fixed status and reason tokens. Tests cover zero-query liveness and sanitized database,
  migration, and configuration failures.
- Credential boundary: the smoke command reads credentials only from environment
  variables, validates `/auth/me/`, rejects admin identity, and requires the exact
  permission set of a dedicated `deployment_smoke_reader` role.
- Mutation boundary: login is the sole POST. All workflow requests are GETs with bounded
  pagination; the local-server integration test proves representative business-record
  counts do not change.
- Deployment dependency gap: Redis, worker/beat, remote storage, scheduled jobs, and
  central monitoring are not claimed ready because production hosting remains
  owner-deferred. This is recorded as A-258.
- Browser acceptance: the exact two-run Playwright contract is present and parses.
  Local Chrome exited during launch twice before a page existed, so the required
  screenshot remains for authoritative trusted validation; no screenshot was fabricated.

Residual risk is Medium because readiness is intentionally limited to dependencies that
truthfully exist in the current repository, and browser execution remains environment
dependent. Independent validation should run the configured risk-selected backend lane
and trusted browser contract.
