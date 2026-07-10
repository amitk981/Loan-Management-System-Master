# Risk Assessment

Risk level: High

- Selected slice: `006F3-appraisal-lock-order-and-postgresql-concurrency-closure`
- Mode: `normal_run`
- Result: Failed / not eligible for commit or merge.

## Risk analysis

- Concurrency risk remains open because the authoritative PostgreSQL tests did not execute. SQLite
  cannot prove `SELECT ... FOR UPDATE` ordering or deadlock behavior.
- The candidate changes alter transaction lock acquisition in appraisal mutations and narrow joined
  PostgreSQL locks to the intended row with `FOR UPDATE OF self`. A defect could deadlock appraisal
  review, permit duplicate terminal evidence, or block legitimate actions.
- Rejection is cross-module and atomic: appraisal projection, immutable history, rejection note,
  audit, and workflow evidence must remain all-or-nothing. The candidate tests assert this, but only
  a reachable PostgreSQL run can close the risk.
- No formula, permission, payload, appraisal state, frozen snapshot, sanction behavior, migration,
  dependency, frontend, or protected path was intentionally changed.

## Controls applied

- Public `AppraisalWorkflow` interface and rejection-note seam preserved.
- Two PostgreSQL-only `TransactionTestCase` races added through public interfaces.
- Full default backend suite, coverage, Django check, migration sync, and all frontend gates passed.
- Slice status remains `Not Started`; state records a failed run and repair requirement.
