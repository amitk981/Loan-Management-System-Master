# Source-Bank Governance Evidence Manifest

Slice: `009E4-source-bank-rationale-and-approval-evidence-closure`

All identifiers below are deliberately sanitized labels. The executable assertions use genuine
database rows and prove that account ciphertext, account hash, account digits, capabilities, and
unrelated identities are absent from the retained governance/version/audit surfaces.

## First activation

```json
{
  "governance_id": "<activation-governance-id>",
  "source_bank_account_id": "<protected-bank-row-id>",
  "predecessor_governance_id": null,
  "status": "active",
  "change_context": {
    "action": "config.changed",
    "change_kind": "activation",
    "reason": "Move settlement routing to the verified operating account.",
    "reason_digest": "<sha256-of-exact-reason>",
    "request_id": "req-source-bank-reviewable",
    "actor_user_id": "<provisioner-id>",
    "actor_role_codes": ["senior_manager_finance"],
    "actor_team_codes": [],
    "ip_address": "192.0.2.44",
    "user_agent": "governance-review/1.0"
  },
  "change_context_digest": "<sha256-of-canonical-context>"
}
```

The linked `VersionHistory` has the provisioner only as `author_user`; `reviewer_user`,
`approver_user`, `board_approval_reference`, `approval_reference`, and `approved_at` are empty.
The linked audit has the same canonical manifest and separately matching request-network fields.

## Replacement

The predecessor's terminal version/audit add only the sanitized successor identity and exact
replacement context. The successor's activation manifest carries `change_kind: replacement`, its
own distinct rationale/request/actor context, and the predecessor identity. The predecessor
effective range closes on the successor activation date. All three version rows retain empty
approval fields.

## Executable proof

- RED: `terminal-logs/009E4-red-reviewable-rationale.log` fails because no reviewable rationale
  field existed.
- GREEN rationale/approval contract: `terminal-logs/009E4-green-reviewable-rationale.log`.
- Unsafe rationale zero-write matrix: `terminal-logs/009E4-green-rationale-validation.log`.
- One-field rationale/attribution/false-approval tamper matrix:
  `terminal-logs/009E4-green-attribution-tamper.log`.
- Six focused source-bank tests: `terminal-logs/009E4-green-source-bank-contract.log`.
- PostgreSQL race proof: `terminal-logs/009E4-postgresql-races.log` runs both five-caller first and
  replacement race methods; each method asserts one complete reviewable winner and four conflicts.
- Catalogue/downstream proof: `terminal-logs/009E4-downstream-and-catalogue-tests.log` passes 42
  tests. The production catalogue creates the Critical permission while the focused catalogue
  assertion proves no `RolePermission` grants it by default.

Legacy governance rows have no recoverable rationale. Migration `0005` clears their known false
approval attribution but does not invent rationale; the resolver therefore keeps them fail-closed.
