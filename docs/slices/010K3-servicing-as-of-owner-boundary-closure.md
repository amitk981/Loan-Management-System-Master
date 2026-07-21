# Slice 010K3: Servicing As-Of Owner Boundary Closure

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Depends On
- 010K

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal
Replace the recurring private/live reconstruction seams across DPD, reminder delivery, and CFO MIS
with one protected as-of owner boundary whose current authority, immutable evidence, and concurrent
effects agree.

## Review Finding Closure
| Finding ID | Root ID | Reproducer | Acceptance IDs |
|---|---|---|---|
| AR-010-DPD-001 | ROOT-010-DPD-SNAPSHOT-OWNER | .ralph/runs/2026-07-21_054048_architecture_review/evidence/review-probes/dpd-owner.log | AC-SAO-1, AC-SAO-2, AC-SAO-5 |
| AR-010-REMINDER-001 | ROOT-010-REMINDER-DELIVERY-OWNER | .ralph/runs/2026-07-21_054048_architecture_review/evidence/review-probes/reminder-owner.log | AC-SAO-3 |
| AR-010-MIS-001 | ROOT-010-MIS-AS-OF-OWNER | .ralph/runs/2026-07-21_054048_architecture_review/evidence/review-probes/mis-owner.log | AC-SAO-4 |

## Source References
- `docs/source/functional-spec.md` M10-FR-001–011, M11-FR-001–008/010, BR-066–069
- `docs/source/data-model.md` §§19.9, 20.1–20.4, 34, 35.3–35.4
- `docs/source/api-contracts.md` §§33.6–33.7, 34, and 45.2
- `docs/source/codebase-design.md` §§17.3, 18.1–18.2, 26, 38.1–38.2, and 42
- `docs/slices/010I2-dpd-pointer-and-policy-integrity-closure.md`
- `docs/slices/010J2-reminder-eligibility-and-delivery-integrity-closure.md`
- `docs/slices/010K-cfo-quarterly-mis.md`

## Concrete Requirements
1. Enforce the same-loan current-DPD relationship in both directions. Pointer writes and direct
   snapshot owner mutation/reparent/delete must fail at the database boundary. Approved operational
   DPD policies are immutable; amendments create a distinct approved version and retained snapshots
   keep byte-stable policy evidence.
2. Make the DPD source owner consume every schedule-affecting public financial decision, including
   retained interest-capitalisation reclassification. Interest transferred into principal cannot be
   reported overdue again, while repayment/reversal timing and historical as-of replay remain exact.
3. Carry one reminder serviceability decision from claimed job through actual provider invocation.
   A repayment, scope/permission revocation, recipient change, template change, or resolution that
   wins before provider execution cancels/skips durably with no provider call. Consume communication
   template/job/evidence through public facades and make bounded batch truncation/continuation and
   every processed identity explicit.
4. Make MIS generation and every exact action replay recheck current permission, full report scope,
   and exact submitted-CFO authority before returning retained data. Build one cutoff-consistent
   snapshot from immutable public owner decisions: rows created after the cutoff, live status
   mutations, and concurrent repayment/interest/DPD/reminder changes cannot leak into or mix an
   historical report. Exact same-key transition races replay one response; changed-key races retain
   the documented conflict.
5. Replace changed tests' cross-`TestCase.setUp()` composition with stable public builders and prove
   the owner boundary through public API/module surfaces. Preserve the separate carried deep-ledger
   pagination debt; do not broaden this correction into frontend, default, recovery, or closure work.

## Scope Boundaries / Non-Goals
- No new DPD bucket, repayment, interest, reminder cadence, CFO field, provider, or reporting policy.
- No rewrite of coherent historical snapshots/reports and no product frontend change.
- Do not hold an unbounded portfolio or external provider operation under a broad database lock;
  use a bounded claim/version/owner protocol with explicit conflict and retry semantics.

## Trusted PostgreSQL Acceptance
- Test: `sfpcl_credit.tests.test_servicing_postgresql_acceptance.ServicingAsOfOwnerBoundaryPostgreSQLAcceptanceTests`
- Expected tests: 5

## Acceptance Criteria
- [AC-SAO-1] Instance, queryset, bulk, direct-SQL, delete, and competing paths cannot create a
  dangling/cross-loan current DPD relation or mutate one approved operational policy in place.
- [AC-SAO-2] Capitalisation-to-DPD and repayment/reversal day-before/on/after matrices prove each
  schedule amount is classified once from the public financial owner and historical replay is stable.
- [AC-SAO-3] Repayment/scope/recipient/template races at the final provider boundary produce zero
  sends when the adverse decision wins; exact retries send once, and 1/100/101-loan batches disclose
  every processed/skipped/failed identity plus continuation truth without private communication reads.
- [AC-SAO-4] Generate/submit/review replay authorization, late-created source rows, historical live
  mutations, exact/changed keys, and concurrent source-write matrices produce one cutoff-consistent,
  scope-safe MIS report and byte-stable original responses.
- [AC-SAO-5] All three retained review probes become permanent GREEN tests; the exact five-test
  PostgreSQL owner-boundary class passes twice, changed public fixtures have no cross-test setup
  dependency, and all independent gates are green.

## Risk Level
High

## Done Checklist
- [ ] Execution plan and impact analysis written
- [ ] Exact retained probes reproduced RED and converted to permanent tests
- [ ] Public as-of owner boundary and database constraints implemented
- [ ] Review closure evidence maps every finding and acceptance ID
- [ ] Trusted PostgreSQL class passes twice
- [ ] Reverse consumers and complete independent gates pass
- [ ] Risk/review evidence completed and commit delegated to the orchestrator
