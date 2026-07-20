# Slice 010J2: Reminder Eligibility and Delivery Integrity Closure

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Depends On
- 010I2
- 010J

## Goal
Make quarter-end reminder eligibility a calendar-correct retained decision and keep creation,
execution-time serviceability, idempotency conflicts, and batch outcomes honest through delivery.

## Review Finding Closure
| Finding ID | Root ID | Reproducer | Acceptance IDs |
|---|---|---|---|
| AR-010-REMINDER-001 | ROOT-010-REMINDER-DELIVERY-OWNER | .ralph/runs/2026-07-20_194456_architecture_review/evidence/review-probes/reminder-owner.log | AC-REM2-1, AC-REM2-2, AC-REM2-3, AC-REM2-4, AC-REM2-5 |

## Source References
- `docs/source/functional-spec.md` M11-FR-006/007 and BR-069
- `docs/source/data-model.md` §20.2
- `docs/source/api-contracts.md` §§34.3–34.4 and 45.2
- `docs/source/codebase-design.md` §§18.2, 26, 38.1–38.2, and 42
- `docs/slices/010J-reminder-queue.md`

## Concrete Requirements
1. Select “outstanding beyond one year” through the DPD owner's approved calendar-anniversary
   decision, not a fixed `days_past_due >= 365` proxy. Retain first-unpaid date, quarter cutoff,
   policy/version, and day-before/on/after evidence, including leap-year spans.
2. A newer still-overdue snapshot must not invalidate a retained quarter decision merely because
   the Loan Account pointer advanced. Before provider execution, recheck current serviceability,
   outstanding truth, permission/scope, recipient, and effective template through their public
   owners; resolved/repaid work is skipped/cancelled with durable reason and no send.
3. Translate communications exact replay and changed/cross-owner idempotency conflicts into the
   binding reminder API envelopes. A changed send key returns zero-write 409, never an uncaught 500;
   provider retry cannot duplicate the reminder or message.
4. Define an honest bounded batch contract: either commit atomically or return explicit
   calculated/skipped/failed results per loan. A late missing contact/template cannot hide earlier
   side effects behind one request-level failure.
5. Consume communications template, dispatch job, status, and evidence through public facades and
   public fixtures. Queue, provider acceptance, delivery, failure, phone outcome, follow-up, and
   audit remain distinct retained states.

## Scope Boundaries / Non-Goals
- No new reminder cadence below one year, DPD recalculation, default transition, provider, contact
  policy, frontend, or hard-coded message/recipient data.

## Trusted PostgreSQL Acceptance
- Test: `sfpcl_credit.tests.test_servicing_postgresql_acceptance.ReminderDeliveryIntegrityPostgreSQLAcceptanceTests`
- Expected tests: 5

## Acceptance Criteria
- [AC-REM2-1] Calendar day-before/on/after and leap-year matrices prove no reminder is created early
  and every approved quarter decision is reproducible.
- [AC-REM2-2] Advanced still-overdue snapshots remain eligible, while repayment/resolution before
  actual provider execution produces an honest skip/cancel and zero communication send.
- [AC-REM2-3] Exact, changed-key, cross-reminder, retry, and competing-send cases return stable
  200/409/provider envelopes with one message effect and one immutable evidence chain.
- [AC-REM2-4] Mixed portfolio batches disclose every calculated/skipped/failed identity and never
  conceal retained partial side effects; permission, contact, and template failures are isolated.
- [AC-REM2-5] The retained probe and public communication/DPD reverse-consumer tests pass with the
  five-test PostgreSQL class twice and all independent gates green.

## Risk Level
High

## Done Checklist
- [ ] Execution plan and impact analysis written
- [ ] Calendar/idempotency RED probes retained
- [ ] Eligibility and execution-time delivery owners implemented
- [ ] Exact acceptance closure evidence saved
- [ ] PostgreSQL acceptance passed twice
- [ ] Reverse consumers and complete gates passed
- [ ] Risk/review evidence completed and commit delegated to the orchestrator
