# Quality Gates Summary

Run from the architecture-review worktree on 2026-07-12.

## Review Reproduction (expected failure)

Command used the mandated interpreter and selected only
`ZExecutedObjectScopeLedgerTests.test_zz_executed_ledger_equals_all_eight_public_actions`.
Result: exit 1. The aggregate reported all eight expected rows absent, proving that it depends on
other test methods populating module-global state. This is finding evidence, not a configured gate.

## Backend Configured Gates

- `/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py check`: pass, no issues.
- `/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py makemigrations --check --dry-run`: pass,
  no changes detected.
- Full suite under coverage: pass, 467 tests, 8 expected SQLite skips, 57.282 seconds.
- Coverage: 93% (18,055 statements; 1,183 missed), above the 85% floor.

## Frontend Configured Gates

- `npm run build`: pass (Vite production build).
- `npm run typecheck`: pass.
- `npm run lint`: pass.
- `npm test -- --run`: pass, 29 files and 202 tests.

## Ralph Documentation Checks

- Slice queue lint under Bash: pass with no dangling dependency, malformed status/section, or cycle.
- `git diff --check`: recorded after final artifact generation.
- No production, source, frontend-design, script, configuration, or other protected file changed.
