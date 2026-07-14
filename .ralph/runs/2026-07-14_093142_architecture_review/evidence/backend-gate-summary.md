# Backend Gate Summary

Interpreter: `/Users/amitkallapa/LMS/.ralph/venv/bin/python`

- `manage.py check`: pass, no issues.
- `manage.py makemigrations --check --dry-run`: pass, no changes detected.
- Coverage suite: 722 tests pass in 176.995 seconds; 22 expected PostgreSQL-only skips.
- Coverage: 93%, above the configured 85% floor.
- Focused legacy register contract: 1/1 test passes.

The coverage detail and focused command output are retained in `evidence/terminal-logs/`.
