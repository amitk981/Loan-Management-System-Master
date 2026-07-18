# Slice 011K: Compliance Control Tracker Foundation

## Status
Not Started

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance

## Goal
Provide one governed control/task/evidence engine for recurring compliance work, including the annual
money-lending review, without duplicating evidence owned by earlier modules.

## User Value
Compliance owners and reviewers can see due/overdue obligations and prove completion with reviewed evidence.

## Depends On
- 011J

## Source References
- `docs/source/api-contracts.md` §§37.1-37.4, 37.7
- `docs/source/data-model.md` §§23.1-23.3, 23.7-23.8
- `docs/source/functional-spec.md` M14 and Compliance Task Matrix
- `docs/source/user-flows.md` §35
- `docs/source/codebase-design.md` §19.4
- `docs/source/auth-permissions.md` §§12.12, 15.4, 15.11, 31
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011K

## Scope
- Add the compliance owner and `ComplianceControl`, `ComplianceTask`, `ComplianceEvidence`, and
  `MoneyLendingLawReview` persistence with period/control uniqueness and indexed due/status queries.
- Implement control GET/POST/PATCH, task GET/POST/PATCH, evidence submit/review, and money-lending
  review POST using standard envelopes, filters, and `available_actions`.
- Implement `ComplianceTaskEngine.generate_due_tasks(as_of_date)` through the existing scheduler/
  job-run seam: monthly/quarterly/annual/ongoing frequencies, owner assignment, due/overdue state,
  reminder/escalation, exact replay, and recorded partial failure.
- Require owner, due date, evidence requirement, reviewer, status, and audit. Evidence review is
  maker-checker; accepted evidence/comments are immutable unless a future audited reopen policy exists.
- Seed/source-map the R7 control catalogue. Consume rather than copy member-only lending, stamp-duty
  (008D), recovery-conduct, archive, access-review, and accounting evidence.
- Annual money-lending review retains financial year/state, applicability/exemption, restricted legal
  opinion, Board note, CS review facts, and corresponding task/evidence link.

## Permissions and Audit
- Apply exact §12.12 permissions: Critical control management, task create/update, evidence submit/
  review, and money-lending manage. Only source owners act; CFO/CS/Auditor get scoped views as defined.
- Control config, task transition, evidence submit/review, escalation, and restricted file access are audited.

## Acceptance and Negative Tests
- Each frequency generates one due task per control/period with correct owner/due/overdue state; replay
  and concurrent scheduler runs do not duplicate tasks or notifications.
- Evidence submit/review requires matching control/task/period, governed file, distinct authorised
  reviewer, and valid transition; rejection retains reason and history.
- Reject disabled controls, missing owner/date, foreign evidence, self-review, accepted-evidence edit,
  premature close, role/scope failure, invalid frequency/status, and changed replay with zero partial writes.
- Money-lending annual review requires restricted legal opinion and Board note per configured control;
  overdue review escalates but does not fabricate compliance.
- Reverse consumers: 008 stamp/notary, 011 recovery/archive, document access, scheduler/job, notification,
  and audit suites remain green; compliance never owns or rewrites their facts.

## Non-Goals
Section 186/NBFC calculations (011L), KYC tracker (011M), grievance workflow (011N), report/export UI,
or deciding legal exemption/jurisdiction absent approved evidence.

## Evidence
RED/GREEN model/engine/API/permission tests; migration and PostgreSQL scheduler races; owner/evidence/
maker-checker matrix; cross-owner read-only probes; full backend gate and API examples.

## Risk Level
Medium

## Acceptance Criteria
- `COMP-AC-001/006-007`, `MOD-COMP-008/010`, and `API-COMP-003` pass.
- Periodic work, evidence, review, escalation, and cross-owner provenance are unique and auditable.

## Done Checklist
- [ ] Execution plan and TDD evidence saved
- [ ] Models/engine/APIs/scheduler/permissions and catalogue completed
- [ ] Frequency, evidence, race/retry, reverse-consumer, and full gates passed
- [ ] Evidence saved; substantive risks/decisions recorded in review-packet/HANDOFF only when needed; mechanical bookkeeping left to Ralph
