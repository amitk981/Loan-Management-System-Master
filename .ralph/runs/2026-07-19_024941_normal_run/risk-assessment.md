# Risk Assessment

Risk level: High

- Selected slice: `009J-loan-account-360-initial-view`
- Mode: `normal_run`
- Manual review required: yes, for the unavailable browser screenshots described below.

## Financial and data-integrity boundary

The projection does not infer an account from mutable status or balance fields. Every row first
reconciles the singular 009C creation status history, audit event, workflow event, immutable terms,
member/application/sanction links, and current SAP link. Active funding additionally resolves the
existing 009G3 post-transfer facade and requires exact account/application/member/amount, balance,
tenure-start, activation, register, and advice coherence. Incoherent records are omitted from lists
and return the same 404 as missing detail records.

Residual risk: the projection intentionally recognizes only `sanctioned` and `active`. Later
servicing states remain unavailable until their 010M/servicing owners can provide equally strong
evidence; this is safer than presenting unproved balances or statuses.

## Authorization and disclosure

Both endpoints require an active authenticated user, the effective
`finance.loan_account.read` permission, and a source role/object-scope predicate. List and detail
share the same predicate. Missing and inaccessible details are nondisclosing. Responses whitelist
display fields; tests ratchet out bank/UTR, advice/register ids, evidence/checksum/storage,
idempotency/request/network, and sensitive member identity data. Reads create no business, audit,
or workflow records.

Residual risk: portfolio-wide Accounts Head/CFO access is source-defined and therefore broad. Any
future narrowing must occur in the canonical source scope, not in the UI.

## Frontend and visual evidence

The initial list/header/KPI/Summary paths use the shared authenticated API and server decimal/status
values. Later mock-backed tabs remain in place under the binding 010M owner; the initial Summary
does not expose their EMI, DPD, interest, default, closure, or NOC claims.

The real Django database migrated and the guarded demo users seeded successfully, but the sandbox
denied both local server binds (`Operation not permitted` / `listen EPERM`) and the Browser runtime
returned `No browser is available`. The repository also has no guarded sanctioned/active 009J
browser fixture. No screenshots were fabricated. Component tests cover the required UI states, and
Django API tests cover real sanctioned/active projections, but the four specified screenshots
remain an independent manual/orchestrator review item.
