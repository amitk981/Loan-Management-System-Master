# Statement Relationship and Migration Extracts

## Before

- `repayments.bank_statement_line_id`: nullable unique raw UUID independently writable by receipt capture.
- `repayments.statement_match_status`: independently writable duplicate match state.
- `bank_statement_lines.matched_repayment_id`: separate one-to-one relationship owner.
- A random UUID could therefore survive receipt capture even when no statement line existed, and the
  two sides could contradict each other.

## After

- `bank_statement_lines.matched_repayment_id` is the only database relationship owner.
- Receipt `bank_statement_line_id` and `statement_match_status` are read-only derived model/API
  projections from the owned line and its retained reason/audit decision.
- Direct capture resolves and locks an existing line, verifies exact amount/date/reference/account
  and narration facts, then claims it through the same matching module.
- Manual and automatic matching lock and update only the owned line relationship.

## Legacy migration decisions

| Legacy state | Forward result | Backward result |
|---|---|---|
| Both sides identify the same receipt/line | Keep canonical line owner; remove duplicate receipt fields | Reconstruct receipt projection from line |
| Receipt UUID names no line | Create immutable `legacy_statement_line_orphan` evidence; create no line | Restore the exact retained UUID |
| Receipt UUID names an unowned line | Create immutable `legacy_statement_link_incomplete` evidence; do not invent actor/audit | Restore the exact retained UUID |
| Receipt UUID conflicts with a line owned by another receipt | Keep line owner and create immutable `legacy_statement_link_contradiction` evidence | Restore the exact retained UUID |

Verified by `evidence/terminal-logs/statement-migration-green.log`, including a forward/backward
executor run and an assertion that no orphan counterpart was fabricated.

