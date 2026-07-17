# Disbursement Amount Boundary Matrix

Public boundary: `DisbursementWorkflow.initiate` / §31.2 HTTP route.

| Amount | Expected | Retained proof |
|---|---|---|
| `400000.00` | accepted | Existing exact-sanction success test |
| `399999.99` | accepted | Row, initiation audit, workflow trace, and CFC task retain `399999.99` |
| `250000.00` | accepted and CFC-approved | Terminal CFC audit retains `250000.00`; transfer remains pending |
| `0` | validation error | No disbursement artifacts |
| `400000.001` | validation error | More than two decimal places; no artifacts |
| `400000.01` | over-sanction conflict | No disbursement artifacts |
| `10000000000000000` | validation error | Outside numeric 18,2; no artifacts |

Exact replay returns the original projection without writes. Reusing the same idempotency key with
`399999.99` after an accepted `400000.00` request returns `409 CONFLICT`.

Evidence: `01-lesser-amount-red.txt`, `02-lesser-amount-green.txt`,
`10-lesser-cfc-and-scope-green.txt`, `13-focused-disbursement-loan-tests.txt`, and
`22-amount-replay-matrix.txt`.
