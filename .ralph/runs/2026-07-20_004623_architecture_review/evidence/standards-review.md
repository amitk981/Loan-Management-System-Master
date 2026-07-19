# Independent Standards Review

Boundary: `git diff 0b5be35c...HEAD` for 010A–010D. Mechanical Ralph artifacts were excluded from
product ranking. This pass was read-only and independent of the Spec pass.

## Findings

- High: allocation omits the API §45.1 `Idempotency-Key`; changed remarks are accepted as replay.
- High: `Repayment.bank_statement_line_id` and `BankStatementLine.matched_repayment` are independent,
  allowing orphaned or contradictory evidence instead of data-model §19.5's canonical relation.
- High: Accounts Head has SAP-posting permission but lacks the source/working-contract default
  create and allocate grants.
- Medium: allocation validates mandatory remarks but retains neither reason nor comment in immutable
  allocation/audit evidence.
- Medium judgment: the collection-bank-account input can be a raw sensitive value and is stored/
  returned without a central encryption/masking seam.
- Medium judgment: repayment capture creates a communications-owned Notification and servicing
  modules build AuditLog manifests directly instead of consuming narrow facades.
- Low judgment: new tests use other TestCase instances, private helpers, and deep fixture chains.

## Clean Areas

Response/error/list envelopes are centralized; views remain thin; money uses Decimal and meaningful
database constraints; mutations use atomic transactions/row locks; restricted documents use the
central storage facade; and PostgreSQL contention tests assert one retained effect.
