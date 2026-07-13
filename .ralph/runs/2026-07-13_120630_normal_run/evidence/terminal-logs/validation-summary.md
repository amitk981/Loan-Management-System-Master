# Validation Summary

- RED 1: governed rule supersession failed because `config.changed.new_value_json` omitted the
  retained predecessor's closed projection (`red-winner-evidence-content.log`).
- RED 2: governed rule creation failed because VersionHistory had no approval reference/time or
  old/new proposal/resource content (`red-version-history-content.log`).
- GREEN tracer: rule create/supersede history and audit content pass
  (`green-version-history-content.log`).
- PostgreSQL acceptance: four independently named rule/committee create/supersede races executed
  twice; each run reports 4 tests, 0 failures, and 0 skips (`postgresql-four-races-run-1.log`,
  `postgresql-four-races-run-2.log`).
- Focused backend: 26 approval-matrix tests pass with four expected SQLite skips.
- Backend: `manage.py check` passes; `makemigrations --check --dry-run` reports no changes; 568 tests
  pass with 16 expected SQLite skips; coverage is 93% against the 85% floor.
- Frontend: build, typecheck, lint, and 208 tests pass.
- Review: parallel Standards and Spec reviews report no remaining findings after the exact
  VersionHistory content/timestamp correction.
