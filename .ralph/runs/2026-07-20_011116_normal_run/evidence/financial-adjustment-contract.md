# Financial Adjustment Contract Evidence

## API examples

Ordinary allocation requires a posted SAP decision and an allocation-specific key:

```http
POST /api/v1/repayments/{repayment_id}/allocate/
Idempotency-Key: allocation-001

{"allocation_rule":"principal_first","remarks":"Allocate confirmed receipt under the approved SOP."}
```

Manual exception approval and allocation are separate actions:

```http
POST /api/v1/repayments/{repayment_id}/manual-allocation-approvals/
Idempotency-Key: approval-001

{"loan_account_id":"uuid","amount":"100000.00","reason":"Approved retained exception."}

POST /api/v1/repayments/{repayment_id}/manual-allocate/
Idempotency-Key: manual-allocation-001

{"approval_id":"uuid","allocation_rule":"principal_first","remarks":"Apply approved exception."}
```

Reversal accepts no client amount or destination:

```http
POST /api/v1/repayments/{repayment_id}/reverse/
Idempotency-Key: reversal-001

{"reason":"Correct the erroneous posting."}
```

Success returns the immutable reversal/allocation references and server-owned restored balances.
Changed, missing, cross-receipt, stale, foreign, or duplicate-key requests return standard
`400/403/404/409` envelopes before financial writes.

## Permission matrix

| Capability | Credit Manager | Accounts Head | CFO/Auditor/read-only | Default correction grant |
|---|---:|---:|---:|---:|
| Capture repayment | Yes | Yes | No | n/a |
| Allocate posted ordinary repayment | Yes | Yes | No | n/a |
| Approve manual exception | No | No | No | None; explicit governance grant required |
| Reverse posted allocation | No | No | No | None; explicit governance grant required |

The last two actions additionally require ordinary allocation authority/object scope when used.
Assumptions A-142 and A-143 record why the source-silent checker/reverser roles remain default-denied.

## Balance and immutable-ledger proof

The focused reversal test begins with principal/total `400000.00`, allocates `100000.00`, and proves
principal/total `300000.00`. Reversal then restores principal/total `400000.00`, resets the exact
schedule application to `0.00`, preserves the original allocation and credit-ledger row byte for
byte, and appends one reversal plus one debit-ledger row for `100000.00`. The public ledger order is
`disbursement`, `repayment`, `reversal`.

`acceptance-matrix-green.log` proves the public behavior. `postgresql-adjustment-run-1.log` and
`postgresql-adjustment-run-2.log` each find and pass exactly four PostgreSQL tests, including
concurrent allocation/reversal and the 101-row schedule case. `reverse-consumers-green.log` passes
62 focused 010A–010D/catalogue tests with only the four SQLite-skipped PostgreSQL tests.

Audit JSON retains linked evidence ids, actor/role, before/after balances, request/timestamp facts,
and SHA-256 reason evidence. It excludes free-text reasons, statement narration, bank references,
and SAP reference values; mandatory bounded reasons remain on immutable governed records.
