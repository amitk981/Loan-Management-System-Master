# Sanitized Current-Tail Resolution Manifest

No member, file, account, or user identifiers are included. Labels describe structural identities
only.

## Bare ordinary successor

| Order | Copy | Predecessor | Exact correction identity | Reconciled | Current tail |
|---:|---|---|---|---|---|
| 1 | copy-A | none | none | yes | no |
| 2 | copy-B | copy-A | correction-1 | yes | no |
| 3 | copy-C | copy-B | none | yes | yes |

Decision: `correction-1 = open`. The current path after copy-B contains copy-C without an exact
correction identity. Workspace is blocked; item completion is disabled; ordered approval is not
available; retained completed-item truth excludes the affected item; legal readiness and all three
pre-disbursement approval projections are false. Projection calls write no evidence.

## Genuine sequential corrections

| Order | Copy | Predecessor | Exact correction identity | Reconciled | Current tail |
|---:|---|---|---|---|---|
| 1 | copy-A | none | none | yes | no |
| 2 | copy-B | copy-A | correction-1 | yes | no |
| 3 | copy-C | copy-B | correction-2 | yes | yes |

Decision: both corrections remain resolved. Every successor after each exact resolver carries a
reconciled correction identity, and copy-C is the unique current tail.

## Fail-closed fields

Resolution fails if the current chain becomes ambiguous or any retained resolver/tail fact changes:
resolution identity, predecessor, document file/checksum, uploader, workspace action, upload audit,
legal audit, workflow event, version history, review action evidence, application/document scope, or
current renderer ownership.

Evidence: `tdd-red-current-tail.log`, `tdd-green-current-tail.log`,
`focused-tail-mutation-consumers-green.log`, and
`focused-final-documentation-class.log` in `evidence/terminal-logs/`.
