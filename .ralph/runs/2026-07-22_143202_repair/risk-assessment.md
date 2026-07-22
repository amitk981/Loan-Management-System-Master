# Risk Assessment

Risk level: High

- Selected slice: 011D-non-payment-note-workflow
- Mode: repair
- Failed domain: PostgreSQL five-worker create/submit acceptance.

## Root cause and correction

The candidate applied `select_for_update()` to querysets that eager-joined nullable workflow
relations. PostgreSQL rejects locks against nullable outer-join sides. When explicit lock targets
were first combined with the same nullable eager joins, concurrent submit replay also demonstrated a
stale cached `approval_case=None` after the winning request committed.

The final correction uses `select_for_update(of=...)` to lock only the owning workflow row and the
canonical loan row, and eager-loads only non-null relations involved in those lock targets. This
preserves duplicate convergence and protects the financial balance snapshot while avoiding nullable
outer joins and stale cached approval relations.

## Risk controls and residuals

- Final PostgreSQL acceptance: exactly 2 tests passed, including five concurrent creates and five
  concurrent submits converging on one note and one approval chain.
- Focused API regression: 6 tests passed. Django check and migration-drift checks passed.
- PostgreSQL 14.20 environment evidence is retained. No migration, API, permission, frontend, source,
  protected, dependency, or business-rule change was introduced by this repair.
- `FOR UPDATE OF` is deliberately PostgreSQL-shaped because PostgreSQL is the production and trusted
  concurrency database. SQLite remains covered by the focused workflow tests but is not concurrency
  evidence.
- Residual process risk: Ralph must still perform its fresh independent validation runs before any
  commit. No blocking product risk remains from the demonstrated validator.
