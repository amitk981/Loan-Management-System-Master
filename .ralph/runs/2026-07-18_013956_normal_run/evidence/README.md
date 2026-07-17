# Evidence Index

Slice: `009H3A-communications-advice-persistence-and-provider-identity`

- `terminal-logs/red-ownership.txt` and `green-ownership.txt`: canonical model ownership tracer.
- `terminal-logs/red-migration-focused.txt` and `green-migration.txt`: genuine retained-receipt
  forward/reverse/reapply cycle.
- `terminal-logs/red-adapters.txt` and `green-adapters.txt`: shared Manual/Fake/Future stable-key
  identity and retry contract.
- `terminal-logs/green-all-focused-final.txt`: 24 foundation plus retained 009H2 tests; two declared
  PostgreSQL-only race tests are skipped under the local SQLite lane.
- `terminal-logs/migration-plan-and-sql.txt`: migration order and generated SQL. The receipt-owner
  operation emits no SQL; only the outbox table/constraints/index are created.
- `terminal-logs/migration-sync-final.txt`: no model/migration drift.
- `terminal-logs/django-check-final.txt` and `compile-final.txt`: backend system/static checks.
- `terminal-logs/final-static-checks.txt`: final state JSON, migration sync, Django, protected-path,
  and configured diff-limit summary.
- `migration-state-manifest.md`: receipt table/row preservation and outbox schema summary.
- `provider-identity-manifest.md`: adapter replaceability, stable identity, and rejection behavior.
- `import-compatibility-graph.md`: canonical model/adapter direction and shallow legacy seam.

The authoritative complete backend suite and coverage floor are delegated to the independent Ralph
orchestrator as required. No frontend file changed, so frontend gates are not impacted by this slice.
