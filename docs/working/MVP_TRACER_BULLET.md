# MVP Tracer Bullet

## Purpose

The MVP tracer bullet proves the architecture connects end to end before the project deepens every module.

## Slice

`006X-mvp-end-to-end-happy-path.md`

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

## Source of Truth

The tracer bullet must still respect `docs/source/`; it may use the minimum required records, but it must not invent business rules silently.
