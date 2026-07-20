# Slice 010G: Monthly Interest Accrual

## Status
Complete

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Calculate single and bulk monthly interest accruals from server-owned principal and effective rate
snapshots, with one retained accrual per loan/month and honest SAP-posting status.

## User Value
Accounts receives reproducible monthly accrual entries without duplicates or spreadsheet-supplied
financial truth.

## Depends On
- 010F

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_servicing_postgresql_acceptance.MonthlyInterestAccrualPostgreSQLAcceptanceTests`
- Expected tests: 1

## Source References
- `docs/source/product-requirements.md` §11.24
- `docs/source/user-flows.md` §29.4
- `docs/source/functional-spec.md` §11.10 M10-FR-001–004/011
- `docs/source/data-model.md` §§18.5, 19.8
- `docs/source/api-contracts.md` §§33.4–33.5
- `docs/source/screen-spec.md` S47
- `docs/source/component-spec.md` §15.7
- `docs/source/codebase-design.md` §17.3
- `docs/source/test-plan.md` MOD-INT-003/004/010, FIN-INT-001/003/004/010
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md` §010G

## Concrete Requirements
1. For a loan/month, derive the accrual period, eligible principal base, applicable historical rate,
   configured day-count/calculation version, and amount in the interest owner. The request supplies
   identity/month, not authoritative financial results.
2. Persist the calculation snapshot and SAP status/reference fields with a database uniqueness rule
   for `(loan_account, accrual_month)`. Exact replay is zero-write; concurrent creation yields one row.
3. Closed loans do not accrue after closure; pre-disbursement/ineligible periods, missing rate history,
   and missing required calculation configuration fail closed without a zero/fabricated accrual.
4. Bulk generation supports an explicit dry run with no writes and a bounded selected/all-active-loan
   run. Report per-loan created/existing/skipped/failed outcomes so one bad loan is not hidden.
5. Create the monthly SAP posting obligation and allow authorised reference/status capture without
   claiming external SAP delivery. Preserve audit truth for calculation and posting transitions.
6. Require `finance.accrual.create` or `finance.accrual.bulk_generate` plus loan-object scope.

## Scope Boundaries / Non-Goals
- No yearly invoice changes, capitalisation, rate administration, provider/SAP integration, report
  export, schedule orchestration beyond the declared callable job, or frontend wiring.
- Do not invent benchmark, spread, reset, or day-count policy.

## Acceptance and Reverse-Consumer Tests
- Single and bulk runs calculate from exact rate/principal snapshots and retain one row per month;
  dry run leaves database/audit/SAP-task counts unchanged.
- Duplicate/concurrent month, changed replay, missing config/rate, post-closure period, unauthorised
  actor, and cross-scope loan cannot create or overwrite an accrual.
- Rate changes affect only periods from their effective date; past accrual and 010F invoice snapshots
  remain immutable.
- 010A ledger/balance, 010C repayment balances, and Epic 009 disbursement truth remain consistent.

## Evidence Required
- RED/GREEN month/FY/leap-boundary calculation fixtures, single/bulk/dry-run API tests,
  permission/audit/SAP-status evidence, database uniqueness proof, twice-run PostgreSQL same-month
  race, and 010A/010C/010F reverse-consumer results.

## Risk Level
High

## Acceptance Criteria
- Monthly accrual is backend-calculated, historical-rate-bound, duplicate-safe, auditable, and honest
  about SAP status and per-loan bulk outcomes.
- Missing accounting policy fails closed rather than changing money.
- Required focused, contention, reverse-consumer, and full gates pass.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested, if needed
- [ ] Audit events tested, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Substantive risks/decisions recorded in `review-packet.md` (and HANDOFF only when needed)
- [ ] Commit created only after passing gates
