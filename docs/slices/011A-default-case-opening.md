# Slice 011A: Default Case Opening

## Status
Complete

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance

## Goal
Create the default-domain foundation and idempotently open one case when canonical repayment truth
shows a missed scheduled principal repayment.

## User Value
Credit staff see an auditable default case immediately instead of tracking missed principal offline.

## Depends On
- CR-015

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance.DefaultCaseOpeningPostgreSQLAcceptanceTests`
- Expected tests: 1

## Source References
- `docs/source/api-contracts.md` §§35.1-35.3
- `docs/source/data-model.md` §§8 `default_case_status`, 21.1
- `docs/source/product-requirements.md` §11.26 (`DEFAULT-AC-001`)
- `docs/source/codebase-design.md` §18.3
- `docs/source/auth-permissions.md` §§12.10, 20.3, 25.8
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011A

## Scope
- Add the `defaults` owner, `DefaultCase` persistence/migration, and source-shaped
  `DefaultWorkflow.open_if_missed_repayment` entry point.
- Consume 010 schedule, allocation, outstanding, and DPD facts; callers may provide the due date and
  reason but never assert whether payment is missed.
- Implement POST `/api/v1/loan-accounts/{id}/default-cases/open/`, GET case detail, and filtered list
  with standard envelopes, pagination, object scope, and `available_actions`.
- Set grace start to the scheduled due date, calculate the three-calendar-month end, retain member/
  loan/trigger facts, and append audit/workflow evidence (`default.case_opened`).
- Make repeated detection/manual replay converge on the same open case; concurrent attempts cannot
  create two active cases for one missed obligation.

## Permissions and Audit
- `defaults.case.open` for source-authorised Credit Manager action; scoped read for Credit, CS,
  configured approvers, and Auditor read-only.
- Denied, wrong-loan, and successful opens must not leak another member's facts; successful state
  change is audited with actor, loan, case, trigger, and safe before/after state.

## Acceptance and Negative Tests
- Missed principal opens one case with exact API fields and three-month dates; fully paid/current or
  non-principal obligations do not.
- Reject nonexistent/foreign loan, wrong permission, invalid trigger/date, and a caller-forged missed
  status with zero writes.
- Prove exact replay and a PostgreSQL concurrent-open race yield one case and one transition chain.
- Reverse consumers: 010 repayment/allocation and DPD tests remain green; opening a case never changes
  ledger/outstanding facts; auditor GET succeeds while every mutation remains forbidden.

## Non-Goals
Grace expiry/assessment (011B), extension (011C), recovery, frontend wiring, or new repayment logic.

## Evidence
RED/GREEN service and API tests; migration forward/reverse/reapply and sync; permission/audit probes;
PostgreSQL race; full backend gate and response examples.

## Risk Level
Medium

## Acceptance Criteria
- `DEFAULT-AC-001`, `MOD-DEF-001`, and `API-DEF-001` pass through one domain owner.
- No duplicate case, caller-derived financial truth, or unaudited transition is possible.

## Done Checklist
- [ ] Execution plan and TDD evidence saved
- [ ] Models/migrations/service/API and permissions completed
- [ ] Targeted, reverse-consumer, race, and full gates passed
- [ ] Evidence saved; substantive risks/decisions recorded in review-packet/HANDOFF only when needed; mechanical bookkeeping left to Ralph
