# Slice 010H2: Interest Calculation, Payment, and Replay Owner Closure

## Status
Complete

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Make annual invoices, monthly accruals, and capitalisation consume one as-of accounting decision so
rate/principal changes, payments through 30 April, principal transfer, and idempotent replay retain
the same financial truth.

## User Value
Borrowers are invoiced and capitalised for the interest actually owed—not tax, fees, already-paid
interest, or a later rate retroactively applied to an earlier period.

## Depends On
- 010E4
- 010H

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Review Finding Closure
| Finding ID | Root ID | Reproducer | Acceptance IDs |
|---|---|---|---|
| AR-010-INTEREST-001 | ROOT-010-INTEREST-CALCULATION-OWNER | .ralph/runs/2026-07-20_121921_architecture_review/evidence/review-probes/interest-owner.log | AC-INT-1, AC-INT-2, AC-INT-3, AC-INT-4, AC-INT-5, AC-INT-6, AC-INT-7 |

## Source References
- `docs/source/product-requirements.md` §11.24
- `docs/source/user-flows.md` §§29.3–29.6
- `docs/source/functional-spec.md` BR-060–065 and M10-FR-001–011
- `docs/source/data-model.md` §§18.5, 19.7–19.9, 34, and 35.3
- `docs/source/api-contracts.md` §§33.1–33.7 and 45.2
- `docs/source/codebase-design.md` §§17.3, 26, 38.1–38.2, and 42
- `docs/slices/010F-interest-invoice-generation.md`
- `docs/slices/010G-monthly-interest-accrual.md`
- `docs/slices/010H-interest-capitalisation-after-30-april.md`
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md`

## Concrete Requirements
1. Introduce one public as-of calculation decision that consumes canonical principal movements,
   effective-rate periods, approved calculation configuration, and payment/application evidence.
   Under `simple_daily`, segment days at retained principal/rate boundaries; if an approved method
   cannot define a boundary, fail closed rather than applying the period-end scalar retroactively.
2. Annual invoice generation derives historical principal/rate segments and binds each payment to
   the exact interest obligation it settles. Do not subtract an unrelated or already-applied
   allocation merely because its receipt date falls inside the invoice period.
3. Monthly accrual uses the same as-of boundary decision. Mid-month principal/rate changes are
   segmented or rejected according to the approved version, while A-147's source-silent
   disbursement/closure-month policy remains fail closed and snapshots stay immutable.
4. Capitalisation resolves outstanding interest as of the end of 30 April, including payments after
   invoice issue and before the cutoff. Subtract paid interest exactly once; exclude tax, fees, and
   charges from capitalised principal unless a later source-governed rule explicitly includes them.
5. Treat capitalisation as one atomic reclassification: principal, interest state, total/account and
   schedule truth, immutable ledger, invoice/payment evidence, audit, queued email, and a durable
   hard-copy task/artifact agree. Provider status remains honest and cannot duplicate money.
6. Persist the exact original response for generation, issuance, accrual posting, and capitalisation.
   Later SAP/document/communication state changes never alter §45.2 `original_response`; changed or
   cross-owner keys remain zero-write conflicts.
7. Make approved calculation configuration and terminal invoice/accrual evidence immutable through
   model/queryset/bulk paths. Issuance authorization/template comes from the frozen generation
   decision, not a later edit to a live configuration row.
8. Keep the correction bounded behind invoice/accrual/capitalisation public owner functions. Record
   the existing general-module split as Epic 010 closure debt rather than exceeding the slice diff
   limit with a mechanical rewrite.

## Scope Boundaries / Non-Goals
- No new benchmark/spread/reset/day-count, penal-rate, tax, fee, payment-allocation, SAP-provider,
  communication-provider, scheduler, frontend, or invoice-reversal business policy.
- Do not rewrite retained historical invoices/accruals/capitalisations; isolate any unverifiable
  legacy row with explicit migration evidence.

## Trusted PostgreSQL Acceptance
- Test: `sfpcl_credit.tests.test_servicing_postgresql_acceptance.InterestAccountingOwnerPostgreSQLAcceptanceTests`
- Expected tests: 5

## Acceptance Criteria
- [AC-INT-1] Annual invoice fixtures prove rate/principal boundaries, FY/leap edges, exact obligation
  payment ownership, and no retroactive period-end scalar calculation.
- [AC-INT-2] Monthly accrual fixtures prove mid-period rate/principal behavior is segmented or fails
  closed under the approved version, with one immutable loan/month result.
- [AC-INT-3] Payments through 30 April reduce eligible unpaid interest exactly once; tax, fee,
  charges, unrelated allocations, and payments after cutoff do not enter capitalised principal.
- [AC-INT-4] One capitalisation atomically reconciles principal, interest/total/schedule truth,
  immutable ledger and evidence, email obligation, and durable hard-copy task/artifact.
- [AC-INT-5] Generation, issuance, SAP-posting, and capitalisation replays return byte-stable original
  responses after later state/delivery changes; changed and cross-owner keys remain zero-write.
- [AC-INT-6] Calculation configuration and terminal financial evidence reject model/queryset/bulk
  mutation, and issue authority/template is frozen before use.
- [AC-INT-7] Public tests cover exact and changed-key races, partial provider outcomes, reverse
  consumers, and the declared five-test PostgreSQL class twice before complete gates pass.

## Risk Level
High

## Done Checklist
- [ ] Execution plan and impact map written
- [ ] Failing public RED probes retained before implementation
- [ ] Calculation/payment/replay owners and permanent tests implemented
- [ ] Exact acceptance IDs mapped in `review-closure-evidence.md`
- [ ] PostgreSQL acceptance passed twice
- [ ] Reverse consumers and full gates passed
- [ ] Risk/review evidence completed and commit delegated to the orchestrator
