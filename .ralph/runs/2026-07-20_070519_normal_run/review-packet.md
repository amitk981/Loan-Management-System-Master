# Review Packet: 2026-07-20_070519_normal_run

## Result
Ready for independent validation

## Slice
010F-interest-invoice-generation

## Recommended Next Action
Run the Ralph independent gates, including the declared PostgreSQL race twice and complete backend
coverage. No owner decision is required for this candidate.

## Implementation Review

- Added a deep `interest` module whose generation interface accepts actor, loan, FY, and idempotency
  only; all calculation inputs are resolved behind that seam.
- Added immutable invoice/configuration snapshots, financial/issuance constraints, one migration,
  scoped generate/list/issue endpoints, deterministic PDF creation, communication job reuse, and
  audit evidence.
- Exact replay is zero-write; changed replay and same-period duplicates conflict. Queryset and model
  mutation paths reject historical calculation rewrites.
- No frontend or mock surface changed.

## Traceability

- Product requirements §11.24 and Functional M10-FR-005/006/011 say yearly invoices must be generated
  and history preserved; `generate_invoice` freezes the FY calculation and the public generation,
  replay/list, and immutability tests verify it.
- Domain model §13.5 says ownership is unresolved; `InterestInvoiceConfiguration.owner_role_codes`
  is required and the permission/scope denial test proves possession of a code alone is insufficient.
- Data model §19.7 defines loan/member/FY/period/principal/rate/amount/status/document/communication;
  the migration stores each plus version/idempotency/audit evidence, verified by the generation and
  issuance tests.
- API contracts §§33.1–33.3 name generate/list/issue; `docs/working/API_CONTRACTS.md` now records the
  backend-owned request and standard envelopes, verified through real HTTP tests.
- Test plan MOD-INT-001/002/010 and FIN-INT-001/002/010 map to generation, duplicate replay,
  immutable rate/calculation snapshots, fail-closed configuration, and the PostgreSQL race contract.

## Evidence

- RED/GREEN logs: `evidence/terminal-logs/interest-invoice-*-red.log` and matching `*-green.log`.
- Focused/reverse consumers: `evidence/terminal-logs/focused-interest-and-reverse-green.log`.
- Backend checks/migration sync: `evidence/terminal-logs/backend-check-migrations-green.log`.
- Evidence index: `evidence/interest-invoice-evidence.md`.

## Independent Review Focus

- Confirm PostgreSQL serialisation produces `[200, 409]` with one retained chain.
- Confirm the full suite accepts the new app/migration and communication dispatcher integration.
- Confirm configured `simple_daily` accounting is acceptable only when explicitly provisioned, as
  recorded in A-146; no default business policy is present.
