# Permission, Scope, Source-Fact, and Privacy Matrix

| Path | Required authority/scope | Retained result |
|---|---|---|
| Import | authenticated finance role + `finance.bank_statement.import` | File/line retained; no match without match authority |
| Automatic match | `finance.bank_statement.match` + receipt loan-object scope | One canonical line owner or safe unmatched reason |
| Manual match | `finance.bank_statement.match` + line and receipt loan-object scope | One canonical line owner and immutable audit |
| List | `finance.bank_statement.read` + source loan-object scope | Filtering occurs before count/page/row projection |
| Direct capture with line | repayment-create + statement-match authority + exact in-scope line | One receipt, one line owner, one match audit |
| Operator exception | statement-match authority + line scope | One terminal exception decision linked to audit |

Subsidiary narration matrix: borrower-only, application-only, account-only, and missing facts remain
unmatched; borrower plus application is eligible when all exact receipt facts also agree. Direct
matching retains its separate exact account/application/borrower identity rule.

Privacy matrix: imports accept only the opaque UUID selected by central SFPCL source-bank governance;
the identifier is not echoed. Raw account numbers, narration, bank reference, file bytes, and manual
reason text do not enter ordinary statement responses or audit JSON. Legacy collection labels are
encrypted during migration when they cannot be mapped to the active governed account.

Evidence: `evidence/terminal-logs/acceptance-matrix-green.log`,
`evidence/terminal-logs/subsidiary-matrix-red.log`, and
`evidence/terminal-logs/list-scope-privacy-red.log`.

