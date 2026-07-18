# Evidence Index

- `terminal-logs/red-module-constant-guard.txt` — architecture-review bypass reproduced before the
  implementation change.
- `terminal-logs/green-module-constant-guard.txt` — first state-transition tracer test green.
- `terminal-logs/green-guard-indirection-matrix-final.txt` — final 12-case public guard matrix.
- `terminal-logs/green-migration-manifest-and-isolation.txt` — 27 retained legal and adjacent
  migration tests, including row/schema forward-reverse-reapply.
- `terminal-logs/backend-static-and-zero-sql.txt` — Django check, migration sync, compilation, diff
  check, and legal 0015 zero-SQL output.

All evidence is self-contained in this run folder. No screenshot or frontend artifact is required
because this slice changes only backend migration-test infrastructure and introduces no UI behavior.
