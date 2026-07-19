# Slice 011B: Grace Period Tracking

## Status
Not Started

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance

## Goal
Track the mandatory three-month grace interval, resolve repayment during grace, and require a
source-authorised reason assessment when an unpaid case expires.

## User Value
Credit teams know which cases remain in grace, were cured, or require intentionality assessment.

## Depends On
- 011A

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance.GracePeriodPostgreSQLAcceptanceTests`
- Expected tests: 1

## Source References
- `docs/source/api-contracts.md` §35.4
- `docs/source/data-model.md` §§21.1-21.2
- `docs/source/user-flows.md` §31
- `docs/source/functional-spec.md` M12-FR-002-005
- `docs/source/auth-permissions.md` §20.3
- `docs/source/test-plan.md` MOD-DEF-002-006, API-DEF-002-003
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011B

## Scope
- Add `DefaultAssessment` and the `DefaultWorkflow` grace/assessment operations; retain assessment
  type, classification, rationale, evidence ids, borrower interaction, assessor, time, and recommendation.
- Derive active/expired/cured state from server dates and canonical repayment/outstanding truth.
- Add a retry-safe grace-expiry processor through the existing scheduler/job-run seam; it creates a
  review state/task but never invents an assessment.
- Implement POST `/api/v1/default-cases/{id}/assess/` and expose current grace/assessment truth on
  existing detail/list endpoints.
- Payment during grace resolves the case without deleting history; unpaid expiry is the only gate to
  assessment. Classification vocabulary is intentional/non_intentional/unclear; criteria stay
  configurable and mandatory narrative/evidence preserves the source's open policy area.

## Permissions and Audit
- Credit Assessment Team with `defaults.assessment.create` assesses only expired scoped cases;
  Credit Manager monitors; Auditor reads only.
- Grace expiry, cure, and assessment each append workflow/audit evidence. Scheduled runs record
  bounded success/failure counts without borrower-sensitive logs.

## Acceptance and Negative Tests
- Month-end/leap-year due dates produce exactly three calendar months; boundary instants before/on/
  after expiry behave deterministically.
- Payment during grace cures; partial/unallocated payment does not falsely cure; expiry creates one
  assessment requirement under replay/concurrency.
- Reject early, paid, closed, foreign-scope, invalid classification, missing rationale, missing/
  foreign evidence, and duplicate-current assessment with zero partial writes.
- Reverse consumers: 011A open/list remains stable; repayment/allocation truth is read, never changed;
  scheduler replay cannot duplicate tasks/events.

## Non-Goals
Extension creation/document (011C), Non-Payment Note, reminder delivery, frontend, or defining
intentional-default policy absent from source.

## Evidence
RED/GREEN date/state/service/API tests; scheduler retry/concurrency proof; permission/audit tests;
migration checks; full backend gate and API examples.

## Risk Level
Medium

## Acceptance Criteria
- `DEFAULT-AC-002`, `MOD-DEF-002-006`, and `API-DEF-002-003` pass.
- Grace cannot be skipped, assessed early, or advanced from caller-supplied payment truth.

## Done Checklist
- [ ] Execution plan and TDD evidence saved
- [ ] Persistence, service/API, scheduler, permissions, and audit completed
- [ ] Boundary, negative, retry/race, reverse-consumer, and full gates passed
- [ ] Evidence saved; substantive risks/decisions recorded in review-packet/HANDOFF only when needed; mechanical bookkeeping left to Ralph
