# Review Packet: 2026-07-20_092159_normal_run

## Result
Ready for independent validation

## Slice
010H-interest-capitalisation-after-30-april

## Delivered capability

- Zero-write portfolio preview derives cutoff eligibility and old/unpaid/new principal from scoped
  issued invoice truth.
- Atomic finalisation derives money server-side, moves principal/total once, stores immutable
  invoice/rate/calculation/accrual provenance, and appends a capitalisation ledger row.
- Official email is snapshotted and queued through the communications dispatcher; a confidential
  hard-copy PDF is stored through the document owner; both are bound to the audit chain.
- Exact replay, duplicate FY, changed key binding, cutoff, paid/zero/missing invoice, caller money,
  missing template, permission, scope, incoherent balance, and failed-delivery retry paths fail
  closed or return the retained chain without a second financial movement.
- Loan Account 360 and ledger/principal-as-of reverse consumers now expose the revised principal
  while retaining canonical creation, transfer, scope, and balance-coherence checks.

## Source traceability

- The source says unpaid interest remaining through 30 April is added to principal once and the
  borrower receives official email and hard-copy intimation (`product-requirements.md` §11.24;
  `user-flows.md` §§29.5–29.6; BR-061–063; M10-FR-007–010). The code derives issued unpaid invoice
  truth, enforces a post-cutoff date and unique loan/FY, updates principal atomically, queues email,
  stores a letter, and preserves audit/source evidence. This is verified by
  `InterestCapitalisationApiTests` cutoff/finalisation/replay/rollback/delivery tests.
- The source says new-FY interest uses revised principal and historical snapshots remain tied to
  their original versions (BR-062; M10-FR-009/011). The code adds capitalisation ledger truth to the
  canonical principal-as-of resolver and leaves invoice/accrual snapshots unchanged, verified by
  the finalisation test and the 010F/010G reverse-consumer suite.
- The source/API idempotency contract requires duplicate prevention for this financial action
  (`api-contracts.md` §§33.6–33.7, 45; `data-model.md` §35.3). Database uniqueness, account locking,
  replay digests, and the declared PostgreSQL race class implement that contract.

## Evidence

- RED preview: `evidence/terminal-logs/interest-capitalisation-preview-red.log`
- GREEN preview: `evidence/terminal-logs/interest-capitalisation-preview-green.log`
- RED finalisation: `evidence/terminal-logs/interest-capitalisation-finalisation-red.log`
- GREEN finalisation: `evidence/terminal-logs/interest-capitalisation-finalisation-green.log`
- Final focused gates: `evidence/terminal-logs/interest-capitalisation-final-focused-gates.log`
  (`110` tests passed, `12` expected PostgreSQL-only skips, exit `0`; Django check and migration-sync
  also passed).
- PostgreSQL contract collection:
  `evidence/terminal-logs/interest-capitalisation-postgresql-collection.log` (exactly one declared
  test collected; expected SQLite skip; exit `0`).

## Review focus

- Confirm migration constraints and the after-account-lock idempotency recheck under PostgreSQL.
- Confirm Account 360's broadened serviceable selector remains restricted by canonical creation,
  transfer, role/object scope, and total-parts coherence.
- Confirm communication/provider failure remains separate from financial commit and is never
  represented as sent merely because the queue job exists.

## Recommended Next Action
Run Ralph's independent full backend coverage, migration, protected-path, and twice-run PostgreSQL
acceptance gates. No frontend validation is slice-specific because no frontend file changed.
