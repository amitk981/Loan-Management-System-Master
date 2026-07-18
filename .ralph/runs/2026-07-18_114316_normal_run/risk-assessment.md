# Risk Assessment

Risk level: High.

- One reversible communications migration changes FK ownership while preserving physical UUID
  columns, uniqueness, tables, ids, and retained rows.
- Coherent legacy deliveries are classified by an explicit top-level coordinator; ambiguous rows
  remain untouched and cannot re-enter transport.
- Reverse is allowed only before runtime provider attempts exist and refuses rather than deleting
  new evidence.
- Ordinary provider-attempt mutation/deletion and terminal-chain deletion are blocked; raw drift is
  detected through the public owner.
- Standing high-risk approval applies; no revoked operation was found and no financial amount,
  balance, transfer, API shape, or frontend behavior was changed.
