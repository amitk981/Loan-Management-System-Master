# Closure Behaviour Matrix

| Behaviour | Expected result | Evidence |
|---|---|---|
| Zero principal, interest, and charges; reconciled ledger; no recovery | Ready | Closure focused tests/log 16 |
| Principal non-zero | `principal_paid` fails; no close | Closure focused tests/log 16 |
| Interest non-zero and no source-defined adjustment | `interest_paid_or_approved_adjustment` fails; no close | Closure focused tests/log 16 |
| Charges non-zero | `charges_paid` fails; no close | Closure focused tests/log 16 |
| Pending allocation/SAP/reconciliation | `ledger_reconciled` fails; no close | Closure focused tests/log 16 |
| Pending/under-recovery action | `recovery_clear` fails; no close | Closure focused tests/log 16 |
| Applicable physical/demat/cheque/PoA security | Named downstream applicability retained | Close success test/log 16 |
| Forged readiness/balance fields | 400; denial evidence; no close | Closure focused tests/log 16 |
| Readiness becomes stale before POST | Fresh 409; denial evidence; no close | Closure focused tests/log 16 |
| Exact duplicate | Original close replayed; one close/requirement set | Unit and PostgreSQL logs 16, 24-25 |
| Changed duplicate or unsupported type | 409/400; no second close | Closure focused tests/log 16 |
| Auditor / permission-only wrong role | Read-only / 403 close | Closure focused tests/log 16 |
| Wrong workflow scope | Nondisclosing 404 plus safe denial evidence | Closure focused tests/log 16 |
| Direct save/update/bulk mutation after close | Validation error under row lock | Lock-safe focused test/log 23 |
