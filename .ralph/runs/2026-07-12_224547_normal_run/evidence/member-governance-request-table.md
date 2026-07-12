# Member Governance Trusted-Browser Request Table

The Playwright spec asserts and writes the runtime JSON ledger as
`member-governance-request-ledger.json` during each trusted orchestrator execution.

| Order | Method | Path | Exact body authority | Canonical detail reads after step |
|---:|---|---|---|---:|
| 1 | POST | `/api/v1/members/` | Complete individual body | 1 |
| 2 | PATCH | `/api/v1/members/{created_id}/` | Version plus ordinary editable fields | 2 |
| 3 | POST | `/api/v1/members/` | Complete FPC body | 3 |
| 4 | POST | `/api/v1/members/` | Complete Producer Institution body | 4 |
| 5 | POST | `/api/v1/members/{verified_id}/identity-change-requests/` | Projected version, PAN, reason | 6 |
| 6 | POST | `/api/v1/member-identity-change-requests/{request_id}/approve/` | `{}` after enabled six-field action | 8 |

No other member mutation is accepted by the ledger assertion.
