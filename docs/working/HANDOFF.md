# Ralph Handoff

## Last Run
2026-07-10_175450_normal_run

## Current Status
Completed `006D2C-loan-limit-concurrency-and-boundary-regression` under standing High-risk approval.

- Added deterministic PostgreSQL `TransactionTestCase` regressions using independent thread-local
  connections around `LoanLimitCalculator.calculate_for_application(...)`: valid/valid reruns must
  serialize to one stable UUID and consistent final row/audit/workflow facts; valid/invalid must
  preserve only the valid snapshot/evidence.
- Added `config.postgres_test_settings` plus the pre-approved pinned `psycopg[binary]==3.3.4` driver.
  The offline worktree cannot import the new driver, so PostgreSQL green execution is explicitly
  delegated to independent validation after requirements installation. SQLite reports two skips
  with a non-proof message; it is not accepted as concurrency evidence (A-055).
- Strengthened AST fixtures across `ast.Import`/`ast.ImportFrom`, package and aliased imports,
  concrete assessment/policy/private-helper access, required public imports, and required-method
  subsets that tolerate harmless extra methods.
- No calculator formula, endpoint, persistence, permissions, rerun semantics, audit payload,
  response, model, or migration changed.

## Validation
Backend check/migration sync passed; 347 SQLite/default tests passed with the two explicit
PostgreSQL-only skips at 94% coverage. Frontend lint/typecheck, 107 tests, and build passed. The
PostgreSQL command currently stops at the expected missing pinned driver and must be rerun by the
orchestrator after dependency installation. Evidence is in
`.ralph/runs/2026-07-10_175450_normal_run/`.

## Next Run
After independent PostgreSQL validation of 006D2C, run
`006E2-appraisal-source-contract-and-snapshot-hardening`. Then run sharpened 006F through
`AppraisalWorkflow.review(...)`; it must use 006E2's frozen projections and preserve repayment/
submission facts. Run 006F2 before 006G.
