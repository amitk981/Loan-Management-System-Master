# Slice 010J: Reminder Queue

## Status
Complete

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Create a deduplicated quarter-end queue for loans outstanding beyond one year and retain honest SMS,
email, phone-call, delivery, follow-up, actor, and audit evidence.

## User Value
Credit follows up every eligible overdue loan consistently without duplicate borrower messages or
invented delivery status.

## Depends On
- 010I

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_servicing_postgresql_acceptance.ReminderQueuePostgreSQLAcceptanceTests`
- Expected tests: 2

## Source References
- `docs/source/product-requirements.md` §11.25
- `docs/source/user-flows.md` §30.3
- `docs/source/functional-spec.md` BR-069 and §11.11 M11-FR-006/007
- `docs/source/data-model.md` §20.2
- `docs/source/api-contracts.md` §§34.3–34.4, 45
- `docs/source/codebase-design.md` §18.2
- `docs/source/screen-spec.md` S52
- `docs/source/component-spec.md` §16.3
- `docs/source/test-plan.md` API-MON-003
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md` §010J

## Concrete Requirements
1. Implement the reminder owner and a bounded quarter-end eligibility run. Select loans whose
   canonical as-of DPD/outstanding truth is beyond one year at quarter end; retain loan/member,
   quarter/as-of date, reason, channel, template/message snapshot, status, actor, and timestamps.
2. Prevent duplicate automatic reminders for the same loan, quarter, reason, and channel. Exact run
   replay is zero-write and concurrent runs retain one eligible reminder per deduplication identity.
3. Send SMS/email only through the existing communications dispatcher/job/provider seam with its
   idempotency, channel, retry, and evidence rules. Queueing is not delivery; preserve queued/sent/
   failed truth and safe provider evidence.
4. Support phone reminders as an authorised manual log with outcome and next-follow-up date; never
   report a provider send for a phone log. Retain who contacted whom in borrower-safe audit form.
5. Recheck current eligibility before send. A fully repaid/resolved loan is skipped/cancelled with
   reason rather than receiving stale automation.
6. Require `monitoring.reminder.create`, account scope, approved/effective templates, and audit.

## Scope Boundaries / Non-Goals
- No DPD recalculation, default/grace transition, capitalisation, custom communications provider,
  hard-coded recipient data, frontend wiring, or policy for reminders below one year.
- Do not expose message/recipient/provider-sensitive data in ordinary run summaries or logs.

## Acceptance and Reverse-Consumer Tests
- A quarter-end loan beyond one year creates one reminder; under-threshold/current/fully repaid loans
  do not. Boundary dates and repeat/concurrent runs are exact.
- SMS/email queue through the correct channel owner; phone log retains outcome without provider call;
  communication failure/retry never duplicates the reminder.
- Wrong permission, cross-scope loan, missing/unapproved template, missing contact, or stale resolved
  loan fails/skips honestly with no false sent status.
- 010I DPD snapshots and 010A/010C balances remain immutable; existing 009 communications delivery,
  retry, and crash-recovery tests remain green.

## Evidence Required
- RED/GREEN eligibility/boundary/channel tests, API/permission/audit tests, communications job and
  phone-log evidence, database dedupe proof, twice-run PostgreSQL run/send race, and 009 communications
  plus 010A/010C/010I reverse-consumer results.

## Risk Level
Medium

## Acceptance Criteria
- Quarter-end reminders are eligibility-correct, channel-correct, duplicate-safe, permission-scoped,
  and honest about queue/delivery/call outcomes.
- Stale or failed work cannot message a resolved loan or fabricate success.
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
