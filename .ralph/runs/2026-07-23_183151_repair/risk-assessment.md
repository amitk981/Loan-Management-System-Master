# Risk Assessment

Risk level: Medium.

- Selected slice: 011N-grievance-workflow
- Mode: repair
- Manual review required: Ralph independent validation remains authoritative before integration.

## Demonstrated failure and root cause

Both retained PostgreSQL acceptance runs found the required two tests. The concurrent create test
passed, while concurrent resolve/escalate failed before completing because grievance resolution is
a service API that permits `request=None`, but generic communication audit unconditionally read
HTTP transport metadata from that request.

The repair keeps the immutable communication audit and actor identity intact while recording blank
IP address and user agent for a legitimate non-HTTP caller. This matches the dispatcher's existing
request-optional audit handling and does not fabricate transport evidence.

## Evidence

- Exact PostgreSQL RED:
  `evidence/terminal-logs/01-postgresql-acceptance-red.log` — 2 discovered, 1 passed, 1 errored.
- Minimized behavior RED/GREEN:
  `02-requestless-notice-audit-red.log` and `03-requestless-notice-audit-green.log`.
- Exact PostgreSQL GREEN runs:
  `04-postgresql-acceptance-green-1.log` and `05-postgresql-acceptance-green-2.log` — each found
  exactly 2 tests and passed 2/2 in a distinct database.
- Focused regression pack:
  `06-focused-grievance-communications-green.log` — 43 tests run, 31 passed, and 12 expected
  engine-specific tests skipped.
- Static integrity:
  `07-django-check-migration-drift-green.log` — Django check clean and no model drift.
- PostgreSQL environment:
  `08-postgresql-environment.log` — Django vendor `postgresql`, PostgreSQL 14.20.

## Residual risk

The changed generic-audit boundary is shared by governed communication callers. Focused
communications API and dispatcher-job tests passed, and request-present behavior remains unchanged.
Ralph must still run the independently selected validation lane before integration.
