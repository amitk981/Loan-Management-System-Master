# Risk Assessment

Risk level: High

- Selected slice: 006F4-postgresql-credit-concurrency-acceptance
- Mode: repair
- Standing approval: confirmed; no slice-specific `[revoked]` entry exists.

## Risk Analysis

- This slice validates financial/workflow concurrency across loan-limit, appraisal/rejection, and
  sanction submission paths. An incorrect lock or assertion could permit duplicate terminal facts,
  mixed snapshots, deadlock, or false acceptance evidence.
- Production change is limited to making eligibility lock only the `LoanApplication` base row;
  nullable joined rows remain read projections. This matches the established application-first lock
  order used by loan-limit and appraisal modules.
- Test-only corrections restore Python static-method semantics and query the canonical
  `WorkflowEvent` fields while preserving decision UUID, state, cardinality, and loser-no-write
  assertions.
- No schema, migration, formula, endpoint, permission, state transition, dependency, or frontend
  behavior changed.

## Mitigations and Residual Risk

- All five public-interface races passed twice on PostgreSQL 14.20 with deterministic ordering and
  zero skips; a fail-closed verifier rejects incomplete or misleading packets.
- The full 378-test default suite passed at 94% coverage, alongside migration/check and all frontend
  gates.
- Timing-sensitive behavior could regress during the 006G2 approval-case ownership extraction, so
  that slice is sharpened to rerun the exact five-test PostgreSQL command twice.
- Manual review is appropriate because the production edit changes database lock scope, even though
  the lock target is narrower and no public contract changed.
