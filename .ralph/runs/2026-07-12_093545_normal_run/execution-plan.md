# Execution Plan

Selected slice: `006X4-credit-action-parity-regression-matrix`

1. Inventory the public eligibility, loan-limit, appraisal, review, and approval-owned sanction interfaces, their six-field projections, existing fixtures, and the five PostgreSQL races. Build an action/write trace table from those interfaces without relying on private helpers as acceptance evidence.
2. Add one table-driven backend regression suite that enumerates every named action. For each action, exercise its public projection and matching public write for an enabled success and stable disabled denial, including role, permission, object scope, maker-checker, provenance/history, rejection validation, stale state, and zero success-side evidence.
3. Run the new suite before any production change and save the failing output under `evidence/terminal-logs/`. If it exposes predicate divergence, make the smallest correction at the shared public transition seam; do not change business rules.
4. Run the focused matrix green and save its output. Run the authoritative PostgreSQL five-race acceptance and add a projection/write race only if the inventory reveals an uncovered lock boundary. Save the action/write trace table and dependency scan.
5. Run all configured backend and frontend quality gates with the mandated Python interpreter, save logs, and review the diff for protected paths and size limits.
6. Complete Ralph artifacts: changed files, risk assessment, review packet, final summary, progress/state/handoff, digest, and selected-slice status. Sharpen the next one or two Not Started slices using only already-opened source material.

No frontend presentation, schema, migration, dependency, or API contract change is planned.
