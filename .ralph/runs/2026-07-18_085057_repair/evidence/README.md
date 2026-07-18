# Repair Evidence

This folder contains the deterministic reproduction and focused verification for the one failure
reported by independent coverage. No complete backend suite was run by the agent; Ralph's
orchestrator owns authoritative complete coverage revalidation.

- `terminal-logs/red-receipt-owner-migration.txt`: exact missing-outbox failure before repair.
- `terminal-logs/green-receipt-owner-migration.txt`: exact test passing after repair.
- `terminal-logs/green-focused-migration-dispatcher-public.txt`: migration isolation plus current
  communications/public advice contract.
- `terminal-logs/backend-static-gates.txt`: Django check, migration sync, compile, and whitespace.
- `terminal-logs/scope-and-diff.txt`: repair scope, dependency, protected-path, and diff-budget
  assessment.
