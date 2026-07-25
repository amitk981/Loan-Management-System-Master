# Execution Plan

Selected slice: 012H-deployment-readiness-and-smoke-checks

## Boundary

Implement only the deployment-readiness contract selected by 012H:

- public `GET /health/live/` with no database access;
- public `GET /health/ready/` covering database connectivity, migration state, and
  critical configuration without exposing sensitive details;
- read-only `manage.py smoke_check --base-url <url>` covering liveness, readiness,
  a designated low-privilege user's authentication round-trip, and representative
  API-driven workflow reads;
- the exact trusted-browser spec and screenshot declared by the slice;
- API-contract, assumption, and current-run evidence updates.

No hosting, pipeline, worker, scheduler, deep-provider, migration, model, protected-path,
or business-record mutation work is in scope.

## Permission Check

`.ralph/permissions.json` allows changes under `sfpcl_credit/**`, `sfpcl-lms/**`,
`docs/working/**`, and this run's `.ralph/runs/**`. The planned changes stay inside
those paths. `scripts/**`, `.github/**`, Ralph configuration/permissions, policy files,
and `docs/source/**` are protected or forbidden and will not be edited.

## TDD Behaviours

1. RED/GREEN: liveness is reachable at the deployment path, is unauthenticated, returns
   only a terse machine-readable status, and executes zero database queries.
2. RED/GREEN: readiness reports ready only when database, migrations, and critical
   configuration are usable; database and migration failure variants return terse 503
   reason codes with no secret, personal-data, stack-trace, or dependency-version leak.
3. RED/GREEN: `smoke_check` reports a legible non-zero failure for each failed stage and
   returns zero for successful liveness, readiness, authentication, and representative
   paginated read-only workflow checks.
4. RED/GREEN: smoke requests are GET-only except the existing authentication round-trip,
   use a low-privilege configured account, and leave business-record counts unchanged.
5. GREEN/refactor: add the localhost browser contract that displays the deployment
   readiness result through existing dashboard patterns and captures
   `deployment-smoke-readiness.png` in two passing contract runs.

Each backend behaviour is added one at a time, with focused RED and GREEN command output
saved under `evidence/terminal-logs/`.

## Focused Validation

- Run focused Django test labels with
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Run Django `check` and `makemigrations --check`.
- Run the exact Playwright deployment-smoke spec twice with trusted evidence output.
- Run impacted frontend tests/typecheck/lint/build because the browser contract is added.
- Do not run the complete backend suite or full coverage; the orchestrator owns the
  authoritative risk-selected backend lane.

## Evidence and Review

Save ready/not-ready response examples, the local read-only smoke transcript, RED/GREEN
logs, browser screenshots, and focused gate logs in this run folder. Finish
`risk-assessment.md`, independently review against the fixed slice, and set the
`review-packet.md` Result section exactly to `Ready for independent validation`.
