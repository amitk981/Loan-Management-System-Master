# Slice 010E4: Rate Effective-Date and Write-Boundary Closure

## Status
Complete

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Close the final effective-rate successor boundary so approved rate rows can be created or changed
only through one canonical decision, and future-effective versions never become current loan truth
before their effective date.

## User Value
Finance and borrowers see the approved rate for the requested date, without a future rate appearing
early or an ORM write fabricating approved financial configuration.

## Depends On
- 010E3

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Review Finding Closure
| Finding ID | Root ID | Reproducer | Acceptance IDs |
|---|---|---|---|
| AR-010-RATE-001 | ROOT-010-RATE-VERSION-OWNER | .ralph/runs/2026-07-20_121921_architecture_review/evidence/review-probes/rate-owner.log | AC-RATE-1, AC-RATE-2, AC-RATE-3, AC-RATE-4 |

## Source References
- `docs/source/functional-spec.md` M10-FR-001–002 and BR-064–065
- `docs/source/data-model.md` §§18.1, 18.5, 25.3, 34, and 35
- `docs/source/api-contracts.md` §§41.4 and 45.2
- `docs/source/codebase-design.md` §§17.3, 26, 38.1–38.2, and 42
- `docs/slices/010E3-servicing-financial-owner-and-replay-convergence.md`
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md`

## Concrete Requirements
1. Reject fabricated active rate rows and mutation through model save/delete, queryset update/delete,
   bulk create/update, service, and public API paths. Database constraints must require coherent
   approval actor/time/idempotency evidence for active rows; the canonical owner retains the narrow
   internal transition needed to activate and close periods.
2. Keep proposed and active effective periods contiguous, non-overlapping, immutable after use, and
   deterministic under competing successors. Preserve the consumed-date guard and append-only
   version/audit evidence delivered by 010E3.
3. Do not write a future-effective successor into `LoanAccount.current_interest_rate` on activation.
   Expose one public rate facade that resolves an explicit date and makes the current-date projection
   agree with the canonical effective period; any due-date convergence write must be idempotent,
   auditable, and callable without inventing a scheduler policy.
4. Remove direct cross-owner mutation/model imports from the changed rate-to-loan path. Loan and
   interest consumers use the public rate decision/facade, and permanent tests use public builders
   rather than constructing another `TestCase` or calling its private helpers.
5. Freeze activation replay bytes independently of later notice delivery, keep per-loan histories
   coherent at the effective boundary, and retain exact/changed-key behavior under PostgreSQL races.

## Scope Boundaries / Non-Goals
- No benchmark formula, reset calendar, penal-rate policy, interest invoice/accrual arithmetic,
  frontend, or scheduler cadence.
- Do not rewrite retained rate consumptions, histories, notices, invoices, or accruals.

## Trusted PostgreSQL Acceptance
- Test: `sfpcl_credit.tests.test_servicing_financial_owner_closure.RateEffectiveDatePostgreSQLAcceptanceTests`
- Expected tests: 4

## Acceptance Criteria
- [AC-RATE-1] Every supported ORM/service/API path rejects an active rate without the canonical
  approval decision and coherent database evidence.
- [AC-RATE-2] Future activation preserves the currently effective loan/read projection until the
  successor date, then the public resolver and current projection agree without rewriting history.
- [AC-RATE-3] Consumed-date, overlap, gap, exact replay, changed-key, and competing-successor cases
  retain one immutable decision under focused and twice-run PostgreSQL tests.
- [AC-RATE-4] Changed consumers and permanent tests use public rate/loan facades and public fixture
  builders; no cross-`TestCase` construction or private helper chain remains in that boundary.

## Risk Level
High

## Done Checklist
- [ ] Execution plan and impact map written
- [ ] Failing public RED probes retained before implementation
- [ ] Rate owner, database constraints, facade, and permanent tests implemented
- [ ] Exact acceptance IDs mapped in `review-closure-evidence.md`
- [ ] PostgreSQL acceptance passed twice
- [ ] Reverse consumers and full gates passed
- [ ] Risk/review evidence completed and commit delegated to the orchestrator
