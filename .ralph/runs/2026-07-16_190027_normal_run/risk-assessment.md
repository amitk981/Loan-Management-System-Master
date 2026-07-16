# Risk Assessment

Risk level: High

## Why

This slice changes the canonical Django owner for production SAP request, retained-workbook,
delivery, completion, replay, and customer-code state. A destructive or incomplete move could lose
financial identity, break loan relations, expose retained secrets, weaken uniqueness, or make fresh
and upgraded databases disagree.

## Controls and evidence

- One reversible custom migration changes ProjectState only; both database methods are no-ops and
  SQL rendering contains no schema/data statement.
- Forward and reverse executor tests compare exact row counts, primary/foreign keys, ciphertext,
  workbook/delivery checksums, completion digest, lifecycle timestamps, audit/workflow facts,
  physical table names, and introspected indexes/constraints.
- Canonical and compatibility names are object-identical; `finance.models` has no executable policy.
- Public HTTP/orchestration code was not moved or changed. The 101-test impacted suite passes.
- All three one-winner request/code tests pass in two independent PostgreSQL runs, twice per test.
- One migration was added; the run remains below the 30-file/2,000-line/one-migration limits.

## Residual risk

The full repository coverage/frontend gates and independent protected-path/diff validation remain
the orchestrator's responsibility. 009B3B must remove the remaining executable Finance↔SAP policy
edge without altering the state migration or public contracts.
