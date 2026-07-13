# Execution Plan

Selected slice: 006G5-relative-import-dependency-guard

1. Extend the existing sanction dependency fixture matrix first, passing explicit package context
   and covering parent/deeper-relative, alias, wildcard, package exposure, safe same-package, and
   ADR-0005 public-handoff forms. Run the focused tests and preserve the expected red output.
2. Make the test-side AST resolver canonicalize every `ImportFrom` using the scanned module's
   concrete package, including `__init__.py`, and update the repository scan to supply that context.
3. Re-run the syntax matrix, repository dependency scan, focused sanction/API/module/rollback
   suites, then all configured backend and frontend quality gates; save terminal output as evidence.
4. Record the dependency graph, changed files, risk/review/final artifacts, mark 006G5 complete,
   update Ralph state/progress/handoff, and reconfirm the next queued slices are already concrete.

Permissions checked: planned edits are confined to `sfpcl_credit/tests/**`, `.ralph/runs/**`,
`.ralph/state.json`, `.ralph/progress.md`, `docs/working/**`, and the selected `docs/slices/**`, all
allowed by `.ralph/permissions.json`. No protected, forbidden, production, source, frontend, schema,
or dependency file is in scope.
