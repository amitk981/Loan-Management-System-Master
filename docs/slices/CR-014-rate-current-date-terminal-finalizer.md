# Slice CR-014: Rate Current-Date Terminal Finalizer

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Depends On
- 010E4

## Architecture Review Finalizer
- Epic: 010
- Root ID: ROOT-010-RATE-VERSION-OWNER
- Exhausted corrective generation: 2

## Origin
Terminal architecture-review correction admitted by run
`2026-07-20_194456_architecture_review` after ordinary corrective generation 2 reproduced the same
effective-rate owner failure.

## Goal
Make one production-owned current-date decision keep the canonical effective rate, Loan Account
projection, public collections, and every interest consumer equal at and around a successor date,
without allowing a caller to publish future truth early.

## Depends-On Contract
010E4 supplied the protected version write boundary and date resolver. This finalizer must preserve
those protections while replacing its unowned, caller-controlled convergence path. No downstream
interest correction may consume rate truth until this slice is complete.

## Review Finding Closure
| Finding ID | Root ID | Reproducer | Acceptance IDs |
|---|---|---|---|
| AR-010-RATE-001 | ROOT-010-RATE-VERSION-OWNER | .ralph/runs/2026-07-20_194456_architecture_review/evidence/review-probes/rate-current-date.log | AC-RATE-F-1, AC-RATE-F-2, AC-RATE-F-3, AC-RATE-F-4, AC-RATE-F-5 |

## Source References
- `docs/source/functional-spec.md` M10-FR-001–002 and BR-064–065
- `docs/source/data-model.md` §§18.1, 18.5, 25.3, 34, and 35
- `docs/source/api-contracts.md` §§41.4 and 45.2
- `docs/source/codebase-design.md` §§17.3, 26, 38.1–38.2, and 42
- `docs/slices/010E4-rate-effective-date-and-write-boundary-closure.md`

## Concrete Requirements
1. Define one canonical current-date rate owner. A due successor becomes current exactly on its
   effective date through a production-owned invocation/selection path; the system must not depend
   on a test or an arbitrary client calling a convergence helper.
2. A caller-supplied future `as_of_date` may resolve historical/future read evidence but may never
   mutate the current Loan Account projection before the server's current date. Reject or make
   zero-write any early convergence attempt, with permission, account scope, audit, and replay
   behavior owned at the same boundary.
3. On the day before, day of, and day after a successor, canonical resolver, stored current
   projection, list count/rows, detail, invoice, accrual, and capitalisation consumers agree. No
   account may disappear because a collection filters a stale scalar before the owner resolves it.
4. Make the due-date owner idempotent and concurrency-safe for one account and bounded portfolio
   work. Exact replay retains one response/audit decision; changed/cross-account keys conflict with
   zero writes. Competing due versions retain one approved period and one projection.
5. Remove the obsolete unowned mutation seam from production and permanent tests. Cross-module
   consumers use the public rate decision and public builders, not private model/test helpers.

## Scope Boundaries / Non-Goals
- No new scheduler cadence, benchmark formula, reset policy, penal rate, invoice arithmetic,
  frontend, or rewriting of retained consumption history.
- If orchestration cadence is source-silent, expose a bounded idempotent owner callable by the
  existing runtime rather than inventing a business calendar.

## Trusted PostgreSQL Acceptance
- Test: `sfpcl_credit.tests.test_servicing_financial_owner_closure.RateCurrentDateFinalizerPostgreSQLAcceptanceTests`
- Expected tests: 5

## Acceptance Criteria
- [AC-RATE-F-1] Before/date/after matrices prove a future successor cannot publish early and the due
  successor becomes current without an ad-hoc caller.
- [AC-RATE-F-2] Resolver, current projection, collection count/rows/detail, and all three interest
  consumers select the same version at every effective boundary.
- [AC-RATE-F-3] Exact, changed-key, cross-account, competing-successor, and repeated due-run cases
  retain zero duplicate financial effects and immutable replay/audit evidence.
- [AC-RATE-F-4] Five PostgreSQL tests cover one and bounded-portfolio due-date races twice, including
  a stale starting projection and an account that must remain visible.
- [AC-RATE-F-5] The carried review probe becomes a permanent public-seam regression and all focused,
  reverse-consumer, permission, full-suite, and coverage gates pass.

## Risk Level
High

## Done Checklist
- [ ] Impact analysis written before code
- [ ] Failing public RED probe retained and converted to a permanent regression
- [ ] Current-date owner and production invocation implemented
- [ ] Exact closure evidence mapped to every acceptance ID
- [ ] PostgreSQL acceptance passed twice
- [ ] Reverse consumers and complete independent gates passed
- [ ] Risk/review evidence completed and commit delegated to the orchestrator
