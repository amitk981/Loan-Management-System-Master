# Slice 009L6: Epic 009 Owner-Selector Equivalence and Matrix Closure

## Status
Complete

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Replace Epic 009's repeatedly partial selector copies with one owner-level eligibility boundary per
collection, so the identities counted and paginated are exactly the identities that can be
projected and acted on.

## Depends On
- 009L5

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_epic009_exact_selector_postgresql.Epic009ExactSelectorPostgreSQLAcceptanceTests`
- Expected tests: 4

## Source / Review References

- `docs/source/functional-spec.md` M07-FR-001 through M07-FR-010 and M08-FR-001 through M08-FR-011
- `docs/source/api-contracts.md` §§29-31 and 45
- `docs/source/auth-permissions.md` §§19.3, 25.7, 26.5, and 34.7
- `docs/source/codebase-design.md` §§16, 26, and 42
- `docs/working/API_CONTRACTS.md` Loan Account 360 and staff-workspace contracts
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-19_133456_architecture_review`
- `.ralph/runs/2026-07-19_133456_architecture_review/evidence/review-probes/test_009l5_exact_selector_probes.py`

## Concrete Requirements

1. Define one public, owner-level collection-eligibility interface for Loan Accounts and for each
   S36, S37, combined Senior Finance, and CFC workspace branch. The scalar read and collection
   selector must consume the same immutable decision or integrity manifest; do not maintain a SQL
   subset beside a stricter Python projector.
2. Make selection total: every identity admitted before count/offset/limit must project exactly one
   row for the same actor and transaction snapshot. Lifecycle, SAP send/completion, transfer,
   initiation, task, audit/workflow, actor/team, request, readiness, file-integrity, and aggregate
   drift must affect neither totals nor reachability; projection may not silently drop a selected
   row.
3. Preserve database pagination and portfolio-independent query ceilings. If a fact cannot be
   queried directly, move it behind an owner-maintained, integrity-protected decision/manifest that
   both scalar and collection reads consume; do not restore overscan or a full-portfolio scan.
4. Keep account/application/member/customer-code edges, role/object scope, assignment,
   maker-checker, available-action, and mutation authority behind their existing owners. Every
   advertised action must be accepted by the matching mutation for the unchanged actor/row/input;
   every mutation denial must remove both action and unauthorised row/count disclosure.
5. Complete the previously omitted executable matrix for Loan Account, S36, S37, combined Senior
   Finance, and CFC collections: 1/21/101 mixed rows, more than four adjacent drifts, first/middle/
   last/out-of-range pages, every scalar evidence component, all SAP/readiness/workspace/portal
   consumers, action/mutation parity, stable ordering/query ceilings, and independent 400/403/409
   surfaces.
6. Replace the private `_current_pre_payment_stages` unit test with an HTTP or public-module
   observable and remove the duplicate empty PostgreSQL discovery subclass. Keep the five retained
   009L4 probes and the four 009L5 review probes green through public seams.
7. Make the `pgcrypto` prerequisite ownership-safe and reversible without dropping an extension
   that predated this app. Prove the exact SHA-256 selector behavior on PostgreSQL through the
   declared acceptance class; SQLite compatibility remains a secondary local-test contract.

## Scope Boundaries

- `CR-012` remains the sole owner of hosted nine-state Epic 009 browser/image-hash evidence and
  runs after this product-correctness closure.
- No Epic 010 schedule, ledger, repayment, interest, DPD, default, or closure behavior.
- No new SAP-posting confirmation actor, permission, adapter, or success evidence under A-135.
- No frontend styling, layout, or component change.

## Acceptance and Reverse-Consumer Tests

- A table-driven invariant mutation suite proves database collection identities equal their public
  scalar-owner decisions for every lifecycle, SAP, transfer, initiation, task, audit/workflow, and
  aggregate field, rather than testing only one field per owner.
- Mixed 1/21/101-row portfolios prove exact totals, full page contents, deterministic order,
  nondisclosure, boundaries, and stable query ceilings for all five collection branches.
- Every projected action has a paired successful public mutation; every role/permission/scope/
  assignment/maker/evidence denial has paired row, count, action, and mutation assertions.
- The declared four-test PostgreSQL label runs twice and covers Loan Account, S37, combined Senior
  Finance, and CFC exact-selection behavior with the production database functions enabled.
- Existing Epic 009 creation, readiness, transfer, advice, portal, migration-history, and frontend
  contracts remain green.

## Risk Level
High

## Acceptance Criteria

- Count, offsets, total pages, projected rows, and public scalar reads share one owner decision.
- Evidence drift cannot disclose a row or strand a later valid row, regardless of which invariant
  changed or how many adjacent invalid candidates exist.
- Exactness remains database-bounded and is proven on PostgreSQL, not inferred from SQLite alone.
- Epic 009's required action/error/consumer matrix is executable before hosted UI proof or Epic 010.

## Done Checklist

- [ ] Execution plan and impact boundary written
- [ ] Backend/business RED-GREEN evidence saved
- [ ] Owner-selector equivalence implemented without partial rule copies
- [ ] Full drift, pagination, consumer, action, and error matrices green
- [ ] PostgreSQL acceptance and reverse-consumer gates passed
- [ ] Risk/review evidence completed; commit delegated to Ralph
