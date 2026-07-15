# Evidence Index

- `terminal-logs/01-missing-review-red.log` and `02-missing-review-green.log`: mandatory frozen
  review RED/GREEN tracer.
- `terminal-logs/03-selector-boundary-red.log` and `04-selector-boundary-green.log`: acyclic
  selector/read-boundary RED/GREEN tracer.
- `terminal-logs/08-boundary-matrix-green.log`, `10-frozen-history-green.log`, and
  `25-review-fixes-focused-green.log`: malformed snapshot, immutable history, and review fixes.
- `terminal-logs/40-review-link-fixtures-green.log`, `48-nested-schema-green.log`, and
  `54-post-standards-fix-approval-modules.log`: immutable review-link, typed nested-schema, and
  complete 143-test approval/sanction regressions.
- `terminal-logs/55-final-backend-check.log`, `56-final-migrations-check.log`,
  `57-final-backend-coverage-tests.log`, and `58-final-backend-coverage-report.log`: exact final
  backend gates after both independent reviews.
- `terminal-logs/59-final-ralph-integrity.log`: queue/state/diff/protected-path final integrity.
- `terminal-logs/21-frontend-build.log` through `24-frontend-tests.log`: unchanged frontend gates.

The retained-row inspection attempt is saved in `11-retained-row-inspection.log`; it truthfully
records that this isolated worktree has no migrated `approval_cases` table. Migration-history proof
is in `12-migration-history-green.log`.
