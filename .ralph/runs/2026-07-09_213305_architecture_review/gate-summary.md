# Gate Summary

Slice: `architecture-review`

## Backend

- `manage.py check`: passed. See `evidence/terminal-logs/backend-check.log`.
- Full backend tests: 256/256 passed. See `evidence/terminal-logs/backend-tests.log`.
- Migration sync: passed, `No changes detected`. See
  `evidence/terminal-logs/backend-makemigrations-check.log`.
- Coverage: passed at 95% against floor 85. See `evidence/terminal-logs/backend-coverage.log`.

## Frontend

- `npm run lint`: passed. See `evidence/terminal-logs/frontend-lint.log`.
- `npm run typecheck`: passed. See `evidence/terminal-logs/frontend-typecheck.log`.
- `npm test`: 80/80 passed. See `evidence/terminal-logs/frontend-tests.log`.
- `npm run build`: passed. See `evidence/terminal-logs/frontend-build.log`.

## Miscellaneous

- `git diff --check`: passed. See `evidence/terminal-logs/git-diff-check.log`.
- Review-window and source-extract logs saved under `evidence/terminal-logs/`.
