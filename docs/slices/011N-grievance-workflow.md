# Slice 011N: Grievance Workflow

## Status
Complete

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance

## Goal
Create, assign, track, escalate, and resolve borrower grievances with supporting evidence, TAT, notice,
and special linkage for recovery-conduct complaints.

## User Value
Borrower complaints have an accountable owner and visible, auditable resolution rather than an offline log.

## Depends On
- 011M

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_compliance_postgresql_acceptance.GrievanceWorkflowPostgreSQLAcceptanceTests`
- Expected tests: 2

## Source References
- `docs/source/api-contracts.md` §38
- `docs/source/data-model.md` §24.3
- `docs/source/functional-spec.md` M15
- `docs/source/user-flows.md` §36
- `docs/source/component-spec.md` §19.6
- `docs/source/auth-permissions.md` §§19, 25, 26.7
- `docs/source/test-plan.md` MOD-COMP-009, API-COMP-004, §21.6
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011N

## Scope
- Add `Grievance` persistence and staff POST create, filtered/paginated GET list/detail, assign/update,
  and POST `/api/v1/grievances/{id}/resolve/` through one grievance service owner.
- Retain generated reference, member, optional matching loan/application/default, category, description,
  received date/channel, governed supporting documents, assignee, due date, status/history, resolution,
  close time, borrower-informed/acknowledgement, and audit.
- Calculate TAT/overdue from server dates; a retry-safe 011K job escalates overdue/sensitive cases but
  never resolves them. Recovery-conduct grievances link to loan/default/action and fair-practice logs.
- Resolution requires a nonblank summary and optional governed resolution document, transitions
  monotonically, and queues borrower notice through the existing communications owner.
- Provide the staff contract and self-scope primitives required by 011NA; borrower portal UI remains there.

## Permissions and Audit
- Borrower/Field Officer/CS may create only within source scope; CS assigns, relevant owner investigates,
  and authorised CS/owner resolves. Auditor reads only. Borrower sees own safe status/resolution only.
- Create/assign/update/escalate/resolve/notice/download and every denied cross-object attempt are audited;
  internal notes or other members' facts never leak.

## Acceptance and Negative Tests
- Each source category creates with one reference, valid owner/TAT, document provenance, and status;
  assignment and resolution history is retained and borrower notice truth is honest.
- Reject nonexistent/cross-member loan/application/default, foreign document, missing description/category/
  owner, invalid/backward status, resolve without summary, wrong role/scope, changed replay, and edit after close.
- Scheduler and concurrent create/resolve tests yield one escalation/reference/terminal chain.
- Recovery complaint is linked and escalated without exposing recovery notes to the borrower.
- Reverse consumers: communications jobs, document access, recovery fair-conduct, 011K task, member/
  loan object-scope, and Auditor read-only suites remain green.

## Non-Goals
Member portal UI (011NA), staff dashboard UI (011P), report/export (Epic 012), inventing a TAT when
configuration/source provides none, or changing recovery decisions.

## Evidence
RED/GREEN workflow/API/permission/object-scope tests; migration and race/retry proof; escalation and
notice evidence; recovery/privacy probes; full backend gate and API examples.

## Risk Level
Medium

## Acceptance Criteria
- `MOD-COMP-009`, `API-COMP-004`, and `COMP-GRV-001-005` pass.
- A grievance cannot cross borrower scope, close without reason, lose history, or falsely claim notice.

## Done Checklist
- [ ] Execution plan and TDD evidence saved
- [ ] Grievance persistence/service/APIs and task/communication integration completed
- [ ] Scope, privacy, escalation/race, reverse-consumer, and full gates passed
- [ ] Evidence saved; substantive risks/decisions recorded in review-packet/HANDOFF only when needed; mechanical bookkeeping left to Ralph
