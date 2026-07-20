# Execution Plan

Selected slice: `010F-interest-invoice-generation`

## Boundary

Implement only annual interest-invoice draft generation, listing, and issuance in the backend.
The canonical interest module will derive loan/member identity, FY dates, principal, effective-rate
snapshot, paid/unpaid interest, and invoice amount. Monthly accrual, capitalisation, payment/reversal,
bulk UI, and frontend wiring remain outside this slice.

## Public interface and seams

- Add one deep interest module with generation and issuance interfaces; callers provide identity,
  financial year, idempotency key, and issuance channel/recipient—not monetary calculations.
- Reuse the existing loan-account scope selector, effective-rate configuration owner, immutable
  document storage, communication dispatcher, audit log, and standard API envelope/error seams.
- Add configurable, effective-dated invoice accounting/owner configuration because day count,
  tax/fee policy, and final operating owner are unresolved in source truth.

## Red → green tracer cycles

1. API generation creates one immutable FY draft from server-owned principal/rate/configuration,
   records snapshot/audit truth, and leaves account/ledger balances unchanged.
2. Exact idempotency replay returns retained truth; changed replay and same-period duplicate fail.
3. Missing/incomplete accounting or owner configuration, ineligible period/account, permission
   denial, and cross-scope access fail without writes or PII disclosure.
4. A later rate change cannot alter retained invoice bytes or calculation provenance.
5. Issuance creates exactly one retained invoice document and communication/job chain, transitions
   draft to issued without marking paid, and exact replay is stable while changed replay fails.
6. PostgreSQL concurrent same-period generation produces one retained invoice.

Each cycle will save a failing focused run and its subsequent passing run under
`evidence/terminal-logs/` before proceeding.

## Expected implementation

- Add interest invoice/configuration models and one migration with uniqueness, immutability, and
  financial integrity constraints.
- Add the canonical interest module, serializers/views/routes, document rendering/storage reuse,
  communication dispatch reuse, and audit actions.
- Update permission seed assignments only where an already-authorised configured role requires it;
  do not hard-code Sales, Credit, or Accounts as the owner.
- Update `docs/working/API_CONTRACTS.md` to remove caller-authoritative money fields.

## Verification and evidence

- Focused interest model/module/API tests after every red→green cycle.
- Declared PostgreSQL acceptance test (locally collect/execute when PostgreSQL is available).
- Reverse-consumer tests for 010A–010E loan balances/ledger and communications idempotency.
- Backend `manage.py check` and `makemigrations --check`; no complete backend suite locally.
- Save terminal logs, database/content evidence, risk assessment, final summary, and a review packet
  whose Result is exactly `Ready for independent validation`.
