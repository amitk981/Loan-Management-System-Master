# Epic 010 Digest — Servicing, Repayments, Interest, and Monitoring

Use this bounded digest with the selected `010*` slice. The cited source sections remain
authoritative; this file avoids reopening the full source set during ordinary execution.

## Shared source map

- Product rules: `docs/source/product-requirements.md` §§11.21, 11.23–11.25.
- Operational flows: `docs/source/user-flows.md` §§27–30.
- Business rules/modules: `docs/source/functional-spec.md` §§10.7–10.8, 11.9–11.11.
- Domain/data: `docs/source/domain-model.md` §§13.1, 13.4–14.2;
  `docs/source/data-model.md` §§18, 19.5–19.9, 20, 35.2–35.4.
- Interfaces: `docs/source/api-contracts.md` §§30, 32–34, 45 (idempotency).
- Roles: `docs/source/auth-permissions.md` §§12.9–12.10, 19.3, 20.2, 26.6.
- Module seams: `docs/source/codebase-design.md` §§17–18.2.
- Controls/tests: `docs/source/security-privacy.md` §§22.2–22.3;
  `docs/source/test-plan.md` §§13.15–13.16, 14.10, 16.11–16.13, 19.7, 20.2–20.3.
- Delivery/UI: `docs/source/implementation-roadmap.md` §15;
  `docs/source/screen-spec.md` S42–S52; `docs/source/component-spec.md` §§15–16.3.
- Borrower views: `docs/source/screen-spec-member-portal.md` MP15–MP18, §§8.6, 14.5.

## Shared invariants

1. Money is decimal, non-negative, and backend-owned. Never accept a client-calculated balance,
   allocation, accrual, DPD, capitalisation amount, or report total as authoritative.
2. Direct/subsidiary references are duplicate-protected. Allocation, monthly accrual, and annual
   capitalisation are idempotent and must not create a second financial movement.
3. Partial repayment allocation is principal, then interest, then charges only when an approved
   configuration exists. Unknown excess/charge policy stays explicitly unallocated/exceptional.
4. Balance changes and their ledger/audit evidence commit atomically. Ledger history is append-only;
   correction uses an authorised compensating/reversal entry, never mutation of history.
5. Interest calculations use the effective rate snapshot. Missing benchmark/spread, reset cadence,
   day-count, fee/tax, excess-payment, or invoice-owner policy must fail closed or remain configurable;
   it must not be silently invented.
6. Unpaid interest is capitalised only after 30 April of the next financial year, at most once per
   loan/FY, and the new principal is `old principal + eligible unpaid interest`.
7. DPD is derived from schedule plus posted ledger truth as of an explicit date. SOP buckets remain
   `Current`, `1–2 years`, `2–3 years`, and `>3 years`; optional operational buckets are separate.
8. Quarter-end loans outstanding beyond one year enter the reminder workflow. Reminder delivery,
   call outcome, and quarterly MIS inputs are retained as audit evidence.
9. Mutations require the exact finance/monitoring permission and loan-object scope. CFO/Auditor reads
   do not imply mutation. Portal users see only authenticated-member projections.
10. High-contention financial operations require a real PostgreSQL race test in addition to unit/API
    tests. Exact replay must have one retained result and one financial effect.

## Dependency and ownership boundaries

- `010A` establishes schedule/ledger read truth. `010B` captures direct receipts without allocating;
  `010C` owns allocation/balance/ledger effects.
- `010D` owns statement imports, lines, candidate matching, and unmatched exceptions. `010E` owns the
  subsidiary-specific receipt/reconciliation contract and reuses `010C` for allocation.
- `010F`, `010G`, and `010H` separately own invoice, accrual, and capitalisation behavior. Do not
  combine them into a general interest engine implementation slice.
- `010I` owns DPD snapshots only; default/grace/extension transitions remain Epic 011.
- `010J` owns reminder eligibility and records; `010K` owns immutable quarterly MIS snapshots.
- `010L` is the borrower-safe projection/UI. `010M` wires staff UI. `010N` and `010O` retain their
  already-sharpened global-search and header-notification scopes.

## Per-slice execution extracts

### 010A — Schedule and ledger

- Provide account schedule and paginated, deterministic ledger projections for S43/S46.
- Schedule dates/amounts originate in the approved terms; ledger rows expose disbursement and later
  servicing movements without duplicating or rewriting their owner records.
- Preserve 009 loan-account/disbursement behavior. No receipt posting, allocation, or UI wiring.
- Sources: product §11.21; data §§18.1–18.4; API §30; screens S42/S43/S46; roadmap §15.3.

### 010B — Direct repayment capture

- Capture a positive RTGS/NEFT receipt on a serviceable loan with bank reference, date, evidence,
  actor, idempotency key, pending allocation, and pending SAP status.
- Duplicate reference and changed idempotency replay fail before financial writes. Capture alone does
  not change balances; create the next-working-day SAP posting obligation/evidence seam.
- Sources: product §11.23; flow §27; functional M09/BR-055/057; API §§32.2/32.5; tests MOD-REP-001/2/5/9.

### 010C — Principal-first allocation

- Lock the receipt/account, create exactly one explicit allocation, atomically update outstanding and
  append ledger evidence. Never drive a balance negative or silently consume excess/charges.
- Sources: product §11.23; functional §11.9 allocation logic; data §§19.6/35.2; codebase §17.2;
  tests MOD-REP-006–008 and FIN-REP-001–005.

### 010D — Statement matching and unmatched receipts

- Model manual statement imports/lines; match exact, high-confidence UTR/amount/date/borrower/loan
  facts, retain ambiguous/missing facts in an unmatched queue, and audit authorised manual matches.
- A statement line cannot be consumed twice. Matching does not allocate or alter balances.
- Sources: flow §27.4; functional M09-FR-008/009; roadmap §§15.2–15.4; tests API-REP-006/007.

### 010E — Subsidiary deduction reconciliation

- Require subsidiary/produce/transfer facts and tri-party agreement. Missing borrower/application
  narration prevents auto-match and creates an exception; Treasury verification precedes SAP posting.
- Reuse statement matching and allocation owners; do not duplicate either policy.
- Sources: product §11.23; flow §28; functional BR-058/059 and M09; API §32.3;
  tests MOD-REP-003/004, INT-SUB-001–007, E2E-012.

### 010F — Annual interest invoices

- Generate annual draft invoices at financial-year close from server-side balance/rate snapshots,
  prevent duplicate period invoices, preserve historical calculations, and issue through the approved
  communication/document seam. Invoice owner remains configurable until confirmed.
- Sources: product §11.24; flow §29.3; functional M10; data §19.7; API §§33.1–33.3;
  tests MOD-INT-001/002/010 and FIN-INT-001/002/010.

### 010G — Monthly accrual

- Calculate single/bulk monthly accruals from server-owned principal and effective rate; unique by
  loan/month. Missing accounting configuration and post-closure periods fail closed. Retain SAP status.
- Sources: product §11.24; flow §29.4; functional M10-FR-003/004; data §19.8;
  API §§33.4/33.5; tests MOD-INT-003/004 and FIN-INT-003/004.

### 010H — Capitalisation

- Preview eligibility without writes; after 30 April atomically capitalise eligible unpaid interest
  once, retain old/new principal, append ledger evidence, and queue official email plus hard-copy task.
- Sources: product §11.24; flow §29.5/29.6; functional BR-061–063; data §§19.9/35.3;
  API §§33.6/33.7; tests MOD-INT-005–009, FIN-INT-005–009, E2E-013.

### 010I — DPD calculation

- Calculate one loan or portfolio as of an explicit date from the earliest unpaid due date, persist an
  idempotent snapshot, update the current pointer, and return SOP plus separately configured standard
  buckets. Do not open default cases.
- Sources: product §11.25; flow §30; functional M11-FR-001–004; data §§20.1/35.4;
  API §§34.1/34.2; codebase §18.1; test API-MON-001.

### 010J — Reminder queue

- At quarter-end create deduplicated reminders for loans outstanding beyond one year; send SMS/email
  through the communications owner and log phone calls, outcomes, delivery, follow-up, actor, and audit.
- Sources: product §11.25; flow §30.3; functional BR-069/M11-FR-006/007; data §20.2;
  API §§34.3/34.4; codebase §18.2; test API-MON-003.

### 010K — CFO quarterly MIS

- Freeze an as-of portfolio snapshot and report for FY/quarter; expose draft, submit-to-CFO, and review
  transitions without recomputing submitted evidence. Totals drill down to the same account/DPD truth.
- Sources: product §11.25; flow §§30.3/30.4; functional M11-FR-005/008 and CFO MIS fields;
  domain §14.2; data §20.3; API §34.5; component §16.2; test API-MON-002.

### 010L — Member portal repayment view

- Project MP15–MP18 from authenticated member ownership only. Show only verified/posted repayment
  truth, borrower-safe references, approved repayment account details, and no internal SAP/user notes.
- Wire list/detail/schedule/history/invoice/direct-instructions states with no runtime fixtures.
- Sources: portal MP15–MP18, §§8.6/14.5; auth §§19.3/20.2; product §11.21.

### 010M–010O — already concrete

- `010M`: staff S43–S52 wiring, final servicing/monitoring mock removal.
- `010N`: permission-filtered server-side global-search foundation; no sensitive/client-side index.
  It delivers six groups and a default-empty provider seam; `011M3` adds the seventh compliance
  group only after 011K–011M own real compliance records.
- `010O`: real header notification summary and final `Header.tsx` mock removal.

## Unresolved policy — required handling

- Interest benchmark/spread/reset/day-count, penal rate, fees/tax, allocation of excess, and invoice
  owner are open (`docs/working/maps/Open Decisions Index.md`, Interest section). Keep configurable and
  fail closed where calculation correctness depends on them.
- The exact inclusive calendar boundaries of the year-based DPD buckets are not specified. Use an
  existing approved configuration; otherwise record the narrow boundary assumption under the Ralph
  decision policy before implementation and test every boundary.
- Member Portal MVP inclusion and borrower UTR/proof submission are unconfirmed. `010L` implements
  the already-queued read projection; keep optional borrower submission disabled unless configuration
  and an approved contract already exist.
