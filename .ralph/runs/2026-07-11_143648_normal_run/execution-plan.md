# Execution Plan

Selected slice: `006G4-sanction-dependency-boundary-regression`

## Boundary

- Change only the sanction dependency regression tests and Ralph bookkeeping/evidence.
- Preserve the production dependency graph, sanction behavior, transactions, API contracts,
  database schema, frontend, and PostgreSQL race behavior.
- Treat `sfpcl_credit.credit.modules.appraisal_workflow` as the documented public credit handoff
  interface available to approvals; reject every credit-to-approvals import and every other
  approvals-to-credit module import.

## TDD Behaviors

1. Add a synthetic-fixture test that exercises direct, aliased, package-level, and package
   `__init__` import forms. Capture RED output showing the current narrow collector misses at least
   one forbidden form.
2. Replace the local collector with a package-aware AST resolver and make the fixture matrix GREEN.
3. Strengthen the repository scan so it reports no forbidden production edges and must positively
   observe the intended approvals-to-public-credit edge.
4. Run the focused sanction suite, then every configured frontend/backend quality gate.

## Evidence and Closeout

- Save red/green logs, repository dependency graph, focused suite output, and gate output under
  `.ralph/runs/2026-07-11_143648_normal_run/evidence/terminal-logs/`.
- Record changed files, risk, review traceability, final summary, slice completion, progress,
  state, and handoff.
- Review and sharpen the next one or two Not Started slices using only already-opened Epic 006
  digest/source extracts.
