# Validation Results

Run: `2026-07-11_212738_architecture_review`

- PASS: `npm run lint`.
- PASS: `npm run typecheck`.
- PASS: `npm test -- --run` — 24 files, 150 tests.
- PASS: `npm run build` — 1,870 modules transformed.
- PASS: Ralph Python `manage.py check` — no issues.
- PASS: Ralph Python `manage.py makemigrations --check --dry-run` — no changes.
- PASS: Ralph Python coverage run — 400 tests, five expected PostgreSQL-only skips.
- PASS: coverage report — 94%, above the 85% floor.
- PASS: `ralph_slice_queue_lint docs/slices` under Bash.
- PASS: `bash scripts/tests/ralph-workflow-regression.sh`.
- PASS: `git diff --check`.
- PASS: working-tree edits contain no `sfpcl-lms/src/` or `sfpcl_credit/` production path.
- PASS: `.ralph/state.json` and `.ralph/permissions.json` parse as JSON.

The existing Vite CJS deprecation and large-chunk warnings remain non-failing and unchanged.
