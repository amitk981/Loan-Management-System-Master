# Slice 011M: KYC Re-KYC Compliance Tracker

## Status
Not Started

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance

## Goal
Generate and track two-year re-KYC reviews from governed member/KYC truth, with due, warning, overdue,
completion, reminder, and restricted-evidence states.

## User Value
Credit and Compliance can act before borrower KYC becomes stale without bypassing verification controls.

## Depends On
- 011L

## Source References
- `docs/source/data-model.md` §23.6
- `docs/source/api-contracts.md` §18.5 and compliance task APIs §37.2
- `docs/source/user-flows.md` §34
- `docs/source/component-spec.md` §19.3
- `docs/source/screen-spec.md` S65
- `docs/source/auth-permissions.md` §§12.3, 12.12, 19.4, 22
- `docs/source/test-plan.md` §§16.17, 21.4
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011M

## Scope
- Add `KYCReview` and a compliance-owned service/query API for onboarding/re-KYC review status,
  filtering due within 30 days, overdue, member type/status, and assignment.
- Generate one re-KYC review/task per member/cycle exactly two calendar years after canonical last
  completed KYC; use 011K's scheduler/job/task/reminder owner and preserve retry-safe period identity.
- Project completeness from existing governed individual/FPC profile, KYC document/verification,
  CKYC consent, nominee/beneficial-owner requirements, and risk facts; do not copy or mutate them.
- Completion requires a real new governed KYC verification result and records before/after status,
  reviewer, completion, evidence links, and audit. The tracker cannot mark verification itself.
- Send due/overdue requests through the existing communications owner with honest delivery status.

## Permissions and Audit
- `compliance.kyc_review.manage` for source-authorised Credit/KYC owners; Compliance/CFO/Auditor read
  summaries as allowed. KYC files remain masked/restricted and every download is audited.
- Generation, assignment, reminder, overdue transition, governed completion link, and denied access
  append safe audit/workflow evidence without PAN/Aadhaar in logs.

## Acceptance and Negative Tests
- Individual and FPC fixtures calculate exact two-year due dates, 30-day warning, and overdue state;
  scheduler replay/concurrency yields one review/task/reminder identity per cycle.
- Missing PAN/CKYC/FPC beneficial ownership projects incomplete; completed new verification closes the
  review while stale/same-cycle/caller-supplied status cannot.
- Reject foreign member/evidence, wrong scope/role, premature completion, direct KYC mutation,
  invalid dates/status, changed replay, and unrestricted document access.
- Reverse consumers: member/KYC verification, maker-checker, sensitive reveal/download, 011K task,
  notification, and portal self-scope suites remain green.

## Non-Goals
Changing KYC fields/documents, defining CKYC/bureau integration, portal correction request (011M2),
staff dashboard wiring, or changing generic task/communication policy.

## Evidence
RED/GREEN date/completeness/service/API/permission tests; migration and PostgreSQL scheduler race;
governed-completion and masking/download probes; full backend gate and API examples.

## Risk Level
High

## Acceptance Criteria
- `COMP-AC-004`, `MOD-COMP-006`, `COMP-KYC-004-007`, and E2E-017 backend contract pass.
- Tracker state is derived, cycle-unique, access controlled, and can close only from real KYC verification.

## Done Checklist
- [ ] Execution plan and TDD evidence saved
- [ ] KYCReview/service/API and scheduler/task/communication integration completed
- [ ] Date, completeness, race/retry, masking, reverse-consumer, and full gates passed
- [ ] Evidence saved; substantive risks/decisions recorded in review-packet/HANDOFF only when needed; mechanical bookkeeping left to Ralph
