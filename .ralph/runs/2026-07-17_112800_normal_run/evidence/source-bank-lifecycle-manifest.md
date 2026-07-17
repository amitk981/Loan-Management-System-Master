# Source-Bank Lifecycle Manifest

## First activation

- Canonical permission: `config.source_bank_account.activate`, Critical, no default role grant.
- A governance UUID is generated before writes.
- Version `1` and `config.changed` audit are created for that UUID.
- The active governance row is inserted with both non-null proof relations in the same transaction.
- The database rejects an active row without both relations.

## Replacement

- The caller observes the current governance identity before entering the serialized writer.
- The predecessor receives `status=inactive`, `deactivated_at`, version `2`, a deactivation
  `config.changed` audit, and a closed activation effective range.
- The successor identifies the exact predecessor and its activation version/audit records the
  predecessor's final inactive evidence as old state.
- Original activation version/audit relations remain retained.

## Current resolution

Resolution returns a decision only when exactly one active row heads a chain containing every
governance row. It reconciles source-bank facts, activation/deactivation relations and bodies,
effective dates/timestamps, predecessor/successor links, actor/request/reason facts, and exact
version/audit sibling sets. Missing, duplicate, changed, cross-linked, orphaned, or temporally
incoherent history returns no current decision.

Evidence: `03-governance-proof-catalogue-red.txt`, `04-governance-proof-catalogue-green.txt`,
`06-governance-history-red.txt`, `07-governance-history-green.txt`, and
`19-postgresql-governance-and-initiation-races.txt`.
