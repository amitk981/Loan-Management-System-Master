# Slice 010H3: Interest Policy and Reclassification Integrity Closure

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Depends On
- CR-014
- 010H2

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal
Freeze the approved interest calculation policy at approval and make capitalisation either
reconcile every financial owner exactly or fail with no partial reclassification.

## Review Finding Closure
| Finding ID | Root ID | Reproducer | Acceptance IDs |
|---|---|---|---|
| AR-010-INTEREST-001 | ROOT-010-INTEREST-CALCULATION-OWNER | .ralph/runs/2026-07-20_194456_architecture_review/evidence/review-probes/interest-owner.log | AC-INT3-1, AC-INT3-2, AC-INT3-3, AC-INT3-4, AC-INT3-5 |

## Source References
- `docs/source/functional-spec.md` M10-FR-001–011 and BR-060–065
- `docs/source/data-model.md` §§18.5, 19.7–19.9, 34, and 35.3
- `docs/source/api-contracts.md` §§33.1–33.7 and 45.2
- `docs/source/codebase-design.md` §§17.3, 26, 38.1–38.2, and 42
- `docs/slices/010H2-interest-calculation-payment-and-replay-owner-closure.md`

## Concrete Requirements
1. Freeze an approved interest calculation configuration from the approval transition—not only
   after first use—across instance save/delete, queryset update/delete, bulk paths, and database
   constraints. Amendments create a new approved version and never rewrite retained calculations.
2. Put monetary rounding mode, precision, and application boundary in the approved policy/evidence.
   If no approved version defines them, fail closed rather than hard-code per-segment
   `ROUND_HALF_UP`. Annual invoice, monthly accrual, and capitalisation consume the same decision.
3. Before capitalisation, reconcile eligible unpaid invoice interest, interest ledger/account
   outstanding, schedule interest, payments through 30 April, and the exact principal increment.
   Any mismatch rejects the operation with zero principal, schedule, ledger, task, communication,
   or audit side effects; never add a full invoice amount while reducing only an available minimum.
4. On success, one atomic immutable decision reclassifies exactly the reconciled interest once,
   excluding tax, fees, charges, and already-applied payments. Reversal/failure/retry and exact or
   changed-key replay retain coherent original evidence.
5. Keep calculation, invoice, accrual, and capitalisation behind explicit public owner seams and
   use public fixtures. Preserve the general module-split debt under the servicing-seam finding.

## Scope Boundaries / Non-Goals
- No new rate, tax, fee, penal-interest, invoice-reversal, or provider business policy.
- Do not infer a rounding policy from current output or mutate retained terminal financial rows.

## Trusted PostgreSQL Acceptance
- Test: `sfpcl_credit.tests.test_servicing_postgresql_acceptance.InterestPolicyIntegrityPostgreSQLAcceptanceTests`
- Expected tests: 5

## Acceptance Criteria
- [AC-INT3-1] Approved configurations reject every supported mutation/deletion path before and after
  consumption; an amendment is a separately approved immutable version.
- [AC-INT3-2] Configured rounding is applied once at the approved boundary for leap, partial-period,
  multi-segment, and half-unit cases; missing policy fails without a monetary write.
- [AC-INT3-3] Exact and mismatched invoice/account/schedule/payment matrices prove capitalisation
  either reconciles the same amount everywhere or leaves every owner unchanged.
- [AC-INT3-4] Exact/changed-key and competing capitalisation races retain one principal increment,
  one reclassification ledger decision, and byte-stable original evidence.
- [AC-INT3-5] The retained probe and public reverse-consumer tests pass with the declared five-test
  PostgreSQL class twice and all independent gates green.

## Risk Level
High

## Done Checklist
- [ ] Execution plan and impact analysis written
- [ ] Failing public RED probes retained
- [ ] Policy and atomic reconciliation owners implemented
- [ ] Exact acceptance closure evidence saved
- [ ] PostgreSQL acceptance passed twice
- [ ] Reverse consumers and complete gates passed
- [ ] Risk/review evidence completed and commit delegated to the orchestrator
