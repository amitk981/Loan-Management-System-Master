# Repair Evidence

- `terminal-logs/red-migration-state-leak.txt`: exact ordered two-test reproduction of the missing
  witness column before repair.
- `terminal-logs/migration-graph-diagnosis.txt`: direct proof that communications 0004's forward
  plan contains current applications, credit ownership, and disbursements migrations.
- `terminal-logs/green-migration-state-leak.txt`: the identical ordered two-test command after repair.
- `terminal-logs/green-impacted-migration-modules.txt`: all six tests in the three implicated
  migration modules.
- `terminal-logs/green-advice-foundation-and-public-api.txt`: retained 009H3A persistence and 009H2
  public API behavior.
- `terminal-logs/django-check.txt`: Django system check.
- `terminal-logs/migration-sync.txt`: model/migration synchronization check.

The complete parallel backend coverage run is deliberately not repeated locally; Ralph's
independent validator owns that authoritative gate.
