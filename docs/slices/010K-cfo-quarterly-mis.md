# Slice 010K: CFO Quarterly MIS

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Generate an immutable as-of quarterly portfolio snapshot and move its MIS report through draft,
submit-to-CFO, and reviewed states with drill-down, export, permissions, and audit evidence.

## User Value
CFO reviews a reproducible quarter-end portfolio report whose totals reconcile to loan, repayment,
interest, DPD, and reminder truth.

## Depends On
- 010J

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_servicing_postgresql_acceptance.QuarterlyMisPostgreSQLAcceptanceTests`
- Expected tests: 2

## Source References
- `docs/source/product-requirements.md` §11.25
- `docs/source/user-flows.md` §§30.3–30.5
- `docs/source/functional-spec.md` BR-066/068 and §11.11 M11-FR-005/008/010, CFO MIS Fields
- `docs/source/domain-model.md` §14.2
- `docs/source/data-model.md` §20.3
- `docs/source/api-contracts.md` §34.5
- `docs/source/auth-permissions.md` §§12.10, 26.6
- `docs/source/component-spec.md` §16.2
- `docs/source/test-plan.md` API-MON-002
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md` §010K

## Concrete Requirements
1. Generate for explicit financial year, quarter, and quarter-end `as_of_date`. Freeze the source IDs/
   versions and portfolio totals required by M11: active/sanctioned/disbursed, principal/interest,
   quarter repayments, DPD distribution, >1-year overdue, reminders, loan statuses/exceptions, and
   the current availability of later default/closure/compliance facts.
2. Totals and drill-down rows derive only from canonical owner records as of the cutoff. Do not use
   live browser aggregates, future-dated repayments, or silently fabricate a not-yet-built Epic 011/
   012 metric; represent unavailable fields explicitly according to the documented contract.
3. Persist a portfolio snapshot and report identity/document with draft, submitted, and reviewed
   timestamps/actors. A submitted/reviewed snapshot is immutable and remains reproducible after later
   financial activity.
4. Define deterministic exact-replay/version behavior for the same FY/quarter/as-of input in the API
   contract. Concurrent generation cannot create two authoritative reports or overwrite submitted
   evidence.
5. Require `monitoring.mis.generate`, `.submit`, and `.review` for their exact transitions, plus
   portfolio/account read scope. CFO review cannot be inferred from read access; invalid transition
   order is rejected and audited.
6. Provide bounded paginated drill-down plus PDF/Excel export through existing document/report seams;
   report and export totals must match the frozen snapshot.

## Scope Boundaries / Non-Goals
- No DPD/reminder recalculation inside report generation, default/recovery implementation, live BI
  warehouse, custom chart UI, email distribution, or frontend wiring.
- Do not rewrite a submitted quarter when corrections are needed; preserve evidence and use the
  documented revision behavior.

## Acceptance and Reverse-Consumer Tests
- Seeded quarter produces exact totals and drill-downs across principal, interest, repayments, DPD,
  and reminders; PDF/Excel values reconcile to the API snapshot.
- Transactions after cutoff do not change the report. Repeat/concurrent generation, invalid quarter/
  cutoff, missing owner truth, invalid state transition, wrong permission, and cross-scope read fail
  without overwriting evidence.
- Submit and review retain distinct actor/timestamp audit events and freeze the snapshot.
- 010A/010C/010F–010J owner rows remain unchanged; each report total traces to their as-of records.

## Evidence Required
- RED/GREEN seeded reconciliation and cutoff tests, API/permission/state/audit tests, snapshot/export
  hashes and samples, database identity proof, PostgreSQL concurrent generation/transition evidence,
  query-count evidence, and 010A–010J reverse-consumer results.

## Risk Level
Medium

## Acceptance Criteria
- Quarterly MIS is cutoff-correct, reproducible, immutable after submission, permission-scoped, and
  reconcilable from report totals to source records.
- Missing future-epic metrics are represented honestly rather than fabricated.
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
