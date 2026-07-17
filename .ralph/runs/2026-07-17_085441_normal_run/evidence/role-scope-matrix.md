# Readiness Effective-Role / Scope Matrix

All allowed rows also require an active persisted user and the explicit
`finance.disbursement.readiness` permission. A role name, permission, intake assignment, inactive
catalogue role, or unknown `approval_authority_type` alone grants nothing.

| Effective source role | Canonical loan scope | Retained proof |
|---|---|---|
| Senior Manager Finance | Exact application/member where the actor is the newest SAP request assignee | Existing public API scope test in `09-focused-backend-green.txt` |
| Chief Financial Controller | Exact pending initiated disbursement/CFC-task relation | Governed CFC pre/post initiation test in `08-governed-cfc-owner-scope.txt` |
| Credit Manager | Active loan and monitoring statuses only; recovery/archive excluded | Source reader matrix in `16-zero-write-query-scope-proof.txt` |
| CFO | Portfolio detail | Primary and active governed CFO probes in `02-governed-cfo-green.txt` and `09-focused-backend-green.txt` |
| Internal Auditor | Explicit active `audit_readonly` role-scope grant | Source reader matrix in `16-zero-write-query-scope-proof.txt` |
| Multi-role Senior Finance + governed CFC | Union: the CFC relation admits the account even when SAP assignment does not | `03-role-union-green.txt` |
| Unknown/inactive governed authority or missing explicit permission | Denied before object scope with `403 FORBIDDEN` | `07-governed-role-denial-matrix.txt` |

Cross-account/member/application incoherence and intake-only assignment remain nondisclosing; the
focused proof is retained in `16-zero-write-query-scope-proof.txt`.
