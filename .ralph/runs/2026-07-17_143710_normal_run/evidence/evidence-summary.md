# Evidence Summary

- RED→GREEN success: `terminal-logs/red-advice-success.log` and `green-advice-success.log`.
- RED→GREEN replay: `terminal-logs/red-advice-replay.log` and `green-advice-replay.log`.
- RED→GREEN retained-ledger drift: `terminal-logs/red-advice-ledger.log` and
  `green-advice-ledger.log`.
- Final focused matrix: `terminal-logs/advice-focused-final.log` (6 pass, 2 PostgreSQL-only skips).
- Final impacted matrix: `terminal-logs/impacted-backend-tests-final.log` (81 pass, 10 skips).
- Django/model gates: `terminal-logs/django-check.log`, `migration-sync.log`, `ruff-final.log`.
- PostgreSQL sandbox evidence: `terminal-logs/postgresql-five-race-run-1.log` and
  `postgresql-acceptance.md`.
- Sanitized response/replay/failure examples: `advice-examples.md`.
