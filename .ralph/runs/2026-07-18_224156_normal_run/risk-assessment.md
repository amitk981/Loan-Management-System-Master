# Risk Assessment

Risk level: High

- Selected slice: `009H9B-communication-final-attempt-and-exception-queue-closure`
- Mode: `normal_run`
- Manual review required: Yes. This changes retry terminalisation, protected operator evidence,
  authorisation, and a database migration in a borrower-communication workflow.

## Primary risks and controls

- Duplicate or fourth delivery attempt: recovery locks each job, compares retained `attempts` to
  retained `max_attempts`, fences the old claim, and excludes terminal rows from due selection.
  PostgreSQL ten-contender acceptance passed twice with zero provider calls at the cap.
- Lost or duplicated exception truth: one protected one-to-one exception owns each exhausted job;
  opening task/audit/workflow evidence is created only with the winning row.
- Fabricated delivery: manual resolution never changes job attempts/status/provider evidence or the
  pending Communication, and unsupported post-cap retry fails closed.
- Sensitive-data disclosure: the public projection is allowlisted and excludes recipient/content,
  provider external/error/secret, bank/UTR, key/payload/request, and actor/network facts.
- Cross-operator access: HTTP permission checks are job-type specific and the dispatcher always
  filters by the retained assigned owner. Stale resolution uses a locked version token and exact
  exhausted-job coherence checks.
- Migration integrity: one additive communications migration creates the protected ledger and two
  completeness constraints. `makemigrations --check --dry-run` reports no drift.

## Residual risk

- A-135 records that governance has not supplied a separate exception assignee or a post-cap retry
  grant. The conservative implementation assigns the original sender and permits only honest manual
  closure after the cap. Any future governed retry must create a new predecessor-linked attempt;
  it must never reset this job.
- Complete backend coverage and the full suite remain delegated to the independent orchestrator as
  required. No real provider, paid service, deployment, or real personal/financial data was used.
