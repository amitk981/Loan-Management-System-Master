# Slice 010I: DPD Calculation and Monitoring Buckets

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Calculate deterministic as-of-date DPD snapshots from unpaid schedule and posted ledger truth, with
SOP and separately configured operational buckets for one loan or the active portfolio.

## User Value
Credit and CFO see the same reproducible overdue classification instead of manually maintained ageing.

## Depends On
- 010H

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_servicing_postgresql_acceptance.DpdSnapshotPostgreSQLAcceptanceTests`
- Expected tests: 1

## Source References
- `docs/source/product-requirements.md` §11.25
- `docs/source/user-flows.md` §30
- `docs/source/functional-spec.md` BR-066–068 and §11.11 M11-FR-001–004/008/010
- `docs/source/domain-model.md` §14.1
- `docs/source/data-model.md` §§20.1, 35.4
- `docs/source/api-contracts.md` §§34.1–34.2
- `docs/source/codebase-design.md` §18.1
- `docs/source/screen-spec.md` S50–S51
- `docs/source/test-plan.md` API-MON-001
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md` §010I

## Concrete Requirements
1. Implement `calculate_for_loan` and bounded portfolio calculation through the DPD owner. Use an
   explicit `as_of_date`; derive `days_past_due = as_of_date - earliest_unpaid_due_date` from the
   canonical schedule and posted allocations/ledger, never from a client bucket or cached UI total.
2. Persist one idempotent snapshot per loan/as-of date with principal, interest and total overdue,
   SOP bucket, optional standard bucket, inputs/version, and created time; update the loan's current
   DPD pointer without rewriting historical snapshots.
3. Always preserve SOP buckets `Current`, `1–2 years`, `2–3 years`, and `>3 years`. Treat optional
   0–30/31–60/61–90/>90 as a separate configured scheme, never a replacement.
4. The source does not settle inclusive year-boundary convention. Use an existing approved config;
   otherwise record the narrow calendar-boundary assumption under `DECISION_POLICY.md` before code
   and retain tests for day before/on/after every threshold.
5. A loan with no unpaid due schedule is Current with zero overdue; future as-of dates cannot consume
   payments posted after the requested date. Bulk results disclose calculated/skipped/failed loans.
6. Require `monitoring.dpd.calculate` for writes and `monitoring.dpd.read` for reads, plus account
   scope. Calculation records audit/run evidence but does not transition loan/default workflow state.

## Scope Boundaries / Non-Goals
- No default-case/grace/extension transitions (Epic 011), reminders (`010J`), MIS (`010K`), frontend,
  or source-silent manual override of DPD.
- No replacement of the SOP buckets with standard banking buckets.

## Acceptance and Reverse-Consumer Tests
- Current, first overdue day, and every configured bucket boundary return exact days/amounts/buckets;
  repayments before the as-of date reduce overdue while later repayments do not.
- Same loan/date replay is stable; concurrent calls retain one snapshot/current pointer. Missing
  schedule, invalid/future policy input, wrong permission, and cross-scope access do not fabricate DPD.
- Portfolio dry fixture reports per-loan outcomes and query bounds.
- 010A schedule/ledger, 010C allocations, and 010H principal remain unchanged; calculations read their
  canonical truth and create no default case or reminder.

## Evidence Required
- RED/GREEN date/bucket/payment timing matrix, API/permission/audit tests, database uniqueness proof,
  twice-run PostgreSQL same-date race, bulk/query-count evidence, response examples, and
  010A/010C/010H reverse-consumer results.

## Risk Level
Medium

## Acceptance Criteria
- DPD is deterministic, as-of-date correct, historical, idempotent, and derived from schedule/ledger
  truth with SOP buckets intact.
- No default workflow transition is hidden inside calculation.
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
