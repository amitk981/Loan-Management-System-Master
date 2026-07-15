# Risk Assessment

Risk: High.

This slice changes retained encrypted-data format and schema, ordinary masking/reveal separation,
partial mutation semantics, and finance object scope. A defect could make protected account/cheque
metadata recoverable, corrupt retained encrypted values, bypass terminal custody, or expose Stage-4
objects before their source-defined finance state.

The change is bounded by one additive migration with a frozen v1/v2 crypto implementation,
row-count/hash/decrypt/plaintext reconciliation, current/previous-key support, and no reverse
downgrade. CDSL display suffixes are separate projections; ordinary masking does not decrypt;
blank-cheque responses stay `******`; only the reason-bearing, role/permission/object-scoped,
rate-limited reveal owner decrypts. PATCH merges only documented mutable fields under the retained
row lock and revalidates the whole candidate. Finance scope fails closed: Senior Manager Finance
requires `sanction_approved`; CFC stays denied until Epic 009 owns readiness.

TDD, focused/full suites, plaintext scans, migration sync, and two PostgreSQL five-worker runs cover
tamper/rotation/migration, partial/replay/stale/cross-object/terminal races, reader transitions,
forged evidence objects, and dependency direction. No frontend product code, external call,
dependency, protected file, `docs/source`, or git metadata changed. Test-generated local document
artifacts were removed. Standing High-risk approval applies and the veto list is empty.
