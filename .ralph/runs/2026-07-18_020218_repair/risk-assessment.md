# Risk Assessment

Risk level: High (inherited 009H3A slice); Low incremental repair risk

- Selected slice: 009H3A-communications-advice-persistence-and-provider-identity
- Mode: repair
- Independent validation required: yes, before any orchestrator commit.

## Demonstrated failure and repair scope

- Full parallel coverage reported five errors in retained credit-ownership and witness-evidence
  migration tests. Their historical app registries contained current application/credit models
  while the physical schema had correctly been reversed.
- The new communications migration must depend on the current disbursements leaf. That dependency
  makes communications a downstream leaf of current application and credit state, so the two old
  historical projections must exclude communications alongside their existing downstream owners.
- The repair changes only those two migration-test projection filters and explanatory comments. It
  does not change production models, migrations, adapters, services, permissions, APIs, frontend,
  dependencies, source documents, or protected files.

## Underlying slice risk retained

- 009H3A remains High risk because it transfers retained receipt model state without physical-table
  SQL, introduces durable outbox persistence, and changes provider identity semantics.
- The preserved migration and production implementation require complete independent coverage,
  protected-path, migration, and diff-limit validation before commit.

## Residual risk

- Focused tests prove the two known historical projections no longer outrun their reversed schemas,
  but only the orchestrator's full six-worker coverage run can prove no other order-dependent
  migration test was affected.
- 009H3B still owns durable pre-dispatch freeze, crash-window finalization, and PostgreSQL race
  closure; this repair does not broaden 009H3A's acceptance claim.
