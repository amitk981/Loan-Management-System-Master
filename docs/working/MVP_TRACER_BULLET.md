# MVP Tracer Bullet

## Purpose

The MVP tracer bullet proves the architecture connects end to end before the project deepens every module.

## Slices

- `002EX-early-end-to-end-tracer-bullet.md` — runs right after login + protected shell (002E). Thin skeleton of the whole loan life cycle with minimal fields; proves frontend → API → database plumbing before any module is deepened.
- `006X-mvp-end-to-end-happy-path.md` — the full-fidelity verification pass once member, application, eligibility, and sanction modules exist for real.

## Minimum Happy Path

1. Create one member.
2. Create one loan application.
3. Pass completeness.
4. Calculate loan limit.
5. Submit appraisal and approve sanction.
6. Complete minimum documentation readiness.
7. Create a loan account.
8. Mark disbursed with a controlled transfer success record.
9. Post one repayment.
10. Close the loan.

## Out of Scope

- Every exception path.
- Every legal document template.
- Every report/export.
- Full compliance tracker coverage.
- Full repayment/interest edge cases.
- Production migration/import.

## Evidence Required

- One end-to-end test or scripted smoke run.
- API response samples for each major transition.
- Screenshots for the visible staff workflow states.
- Risk assessment showing which controls are intentionally still deferred.

## 002EX Result

Slice `002EX-early-end-to-end-tracer-bullet` proved the first thin path end to end:

1. Backend staff login through `POST /api/v1/auth/login/`.
2. Session-bound `GET /api/v1/auth/me/` returning explicit `tracer.lifecycle.run`.
3. Create member.
4. Create loan application with a positive amount.
5. Sanction application.
6. Create loan account.
7. Mark disbursed.
8. Post one repayment.
9. Close the loan.

What was proven:
- React route/action visibility can be driven by canonical backend permissions through the 002E/002E2 role bridge.
- The API path persists data in the Django database and writes one audit log plus one workflow event per tracer transition.
- Invalid state transitions, zero/invalid amounts, unauthenticated requests, revoked access sessions, and authenticated users without `tracer.lifecycle.run` are rejected before domain writes.

What remains deferred:
- Real member/KYC/application/appraisal/sanction/documentation/SAP/disbursement/repayment/interest/closure business rules.
- Idempotency keys for financial actions beyond the in-test duplicate/state guards.
- Object-level permissions and production approval authority.
- Browser screenshot evidence in this sandbox; localhost binding failed with `EPERM`, so `002EY` must capture real Playwright screenshots/baselines.

## Source of Truth

The tracer bullet must still respect `docs/source/`; it may use the minimum required records, but it must not invent business rules silently.
