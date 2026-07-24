# Execution Plan — 012B Register Exports

## Scope

Implement only the backend report-export job module and its POST/status interfaces for the
registered 012A report catalogue. Reuse existing report selectors, permission, audit, task, and
storage seams. Do not add frontend work, sensitive unmasking, scheduled delivery, saved views, or
new report queries.

## Permission Check

- Product and test edits: `sfpcl_credit/**` — allowed.
- Contract/assumption updates: `docs/working/**` — allowed, except protected policy files.
- Run evidence: `.ralph/runs/2026-07-24_041849_normal_run/**` — allowed.
- One non-destructive migration is permitted by the configured diff limits.
- No edits will be made to `docs/source/**`, protected workflow/configuration files, slice status,
  `.ralph/state.json`, `.ralph/progress.md`, `changed-files.txt`, or mechanical handoff text.

## Public Interface and Deep-Module Seam

The external seam is `POST /api/v1/reports/exports/` plus
`GET /api/v1/reports/exports/{export_job_id}/`. The interface exposes validated report code,
format, canonical filters, idempotent job identity, lifecycle state, failure code, and an expiring
download grant. Selector execution, serialization, storage, retry safety, checksum calculation,
auditing, and lifecycle enforcement stay local to the report-export module; the task remains a thin
adapter.

## TDD Behaviours

Implement in vertical red/green cycles:

1. An authorised request for a registered report and supported format creates one queued job and a
   replay with the same actor/report/canonical filters/format/key returns that job.
2. Invalid report, format combination, filter, missing idempotency key, authentication, or
   permissions fail through the standard error envelope.
3. A thin worker executes the registered selector, creates one deterministic file with generator,
   generation time, report code, and canonical-filter metadata, and completes the job.
4. Worker retry/restart is idempotent; forward lifecycle transitions are enforced and terminal jobs
   cannot be rerun in place.
5. Status reports queued/running/completed/failed truthfully, exposes stable failure codes without
   stack traces, and returns only a short-lived storage grant for an unexpired completed job.
6. Each supported report/format combination parses and reconciles with its 012A selector output;
   unsupported combinations are explicit.
7. Request and download audit events contain job/report/outcome references but no exported values.
8. A PostgreSQL five-race acceptance test proves concurrent duplicate requests converge on one job
   and one generated file.

## Verification and Evidence

- Save every focused failing and passing command under `evidence/terminal-logs/`.
- Run focused export tests with
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Run the declared PostgreSQL acceptance test when the configured database is available.
- Run Django `check` and `makemigrations --check`; do not run the complete backend suite or coverage.
- Update `docs/working/API_CONTRACTS.md` and assumptions only when the implementation requires it.
- Save lifecycle examples, format matrix, parsed-file/checksum reconciliation, concurrency/retry,
  expiry/permission negatives, risk assessment, final summary, and review packet.
- Finish only when `review-packet.md` contains the exact result:
  `Ready for independent validation`.
