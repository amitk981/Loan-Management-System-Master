# Backend Gates

Interpreter: `/Users/amitkallapa/LMS/.ralph/venv/bin/python`

- `manage.py check`: passed, zero issues.
- `manage.py makemigrations --check --dry-run`: passed, no changes detected.
- Coverage test command: found and ran 387 tests in 30.967 seconds; `OK (skipped=5)`.
- The five skips are the expected PostgreSQL-only concurrency tests in the routine SQLite suite;
  006F4's committed acceptance evidence separately ran all five twice on PostgreSQL with zero skips.
- Coverage: 14,927 statements, 951 missed, 94%; passed the 85% floor.

