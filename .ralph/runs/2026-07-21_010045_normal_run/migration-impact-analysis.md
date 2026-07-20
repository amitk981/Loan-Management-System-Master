# Migration Impact Analysis

## Intended schema change

- Replace the loan account's unbound current-DPD UUID storage with a database-backed relationship
  to a retained DPD snapshot while preserving the public pointer meaning.
- Add only fields/constraints needed to freeze the policy/source decision and enforce snapshot
  identity/ownership.

## Existing-data handling

- The additive migration must validate every existing pointer before applying stronger integrity.
- Coherent rows are preserved without recalculation or invented DPD values.
- Dangling or cross-loan legacy relationships must fail closed or be explicitly isolated by the
  migration; the implementation may not silently fabricate a replacement snapshot.

## Blast radius

- Monitoring DPD models/module and their migration state.
- Loan-account current-pointer reads used by monitoring APIs and reverse consumers.
- Existing DPD calculation/API tests plus PostgreSQL concurrency acceptance.
- No frontend, default-case, reminder, or unrelated servicing schema changes.

## Verification

- Migration behavior tests cover coherent and incoherent legacy relationships.
- Model state is checked with `makemigrations --check`.
- Direct-database, queryset/bulk, instance/service, deletion, and cross-loan paths are exercised.
- PostgreSQL acceptance proves same-date and portfolio race behavior against real constraints.
