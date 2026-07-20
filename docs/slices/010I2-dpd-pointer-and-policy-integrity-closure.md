# Slice 010I2: DPD Pointer and Policy Integrity Closure

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Depends On
- 010H3
- 010I

## Goal
Bind each Loan Account's current DPD pointer to a valid snapshot owned by that loan and freeze the
exact policy and source decision needed to reproduce historical monitoring truth.

## Review Finding Closure
| Finding ID | Root ID | Reproducer | Acceptance IDs |
|---|---|---|---|
| AR-010-DPD-001 | ROOT-010-DPD-SNAPSHOT-OWNER | .ralph/runs/2026-07-20_194456_architecture_review/evidence/review-probes/dpd-owner.log | AC-DPD2-1, AC-DPD2-2, AC-DPD2-3, AC-DPD2-4, AC-DPD2-5 |

## Source References
- `docs/source/functional-spec.md` M11-FR-001–004/008/010 and BR-066–068
- `docs/source/data-model.md` §§20.1 and 35.4
- `docs/source/api-contracts.md` §§34.1–34.2
- `docs/source/codebase-design.md` §§18.1, 26, 38.1–38.2, and 42
- `docs/slices/010I-dpd-calculation-and-monitoring-buckets.md`

## Concrete Requirements
1. Replace the unbound current DPD UUID with database-enforced referential integrity to a retained
   DPD snapshot. The current pointer must reference the same Loan Account and a coherent current
   owner decision; dangling and cross-loan pointers fail at the write/database boundary.
2. Freeze the SOP boundary convention, optional operational scheme identity/version, and exact
   inputs with each calculation. Later scheme edits never alter replay bytes or the meaning of a
   historical snapshot; an approved amendment produces a distinct version.
3. Resolve schedule, posted ledger/allocation, permission, and account scope through public owner
   decisions, rechecking the protected loan under the calculation lock. Do not copy private models
   or trust a pre-lock scope/schedule projection.
4. Same-loan/date replay and current-pointer advancement must be idempotent under one and portfolio
   races. An older as-of calculation may be retained historically but cannot replace a newer
   coherent current pointer; failed calculation leaves both history and pointer honest.
5. Provide an additive migration/backfill that validates every existing pointer/snapshot/loan
   relationship and fails closed or isolates incoherent legacy data without fabricating DPD.

## Scope Boundaries / Non-Goals
- No default-case transition, reminder rule, new DPD bands, manual override, frontend, or rewrite of
  coherent historical calculations.

## Trusted PostgreSQL Acceptance
- Test: `sfpcl_credit.tests.test_servicing_postgresql_acceptance.DpdOwnerIntegrityPostgreSQLAcceptanceTests`
- Expected tests: 5

## Acceptance Criteria
- [AC-DPD2-1] Dangling, deleted, and wrong-loan current pointers are impossible through instance,
  queryset, bulk, service, and direct database paths.
- [AC-DPD2-2] Historical replay returns the frozen SOP/operational version and inputs after later
  policy edits; missing/unapproved policy fails without a snapshot.
- [AC-DPD2-3] Public schedule/ledger/scope decisions and as-of payment timing produce exact amounts
  at day-before/on/after every calendar boundary.
- [AC-DPD2-4] Same-date, older-date, and bounded-portfolio races retain one snapshot per identity and
  the newest coherent current pointer under the declared PostgreSQL matrix.
- [AC-DPD2-5] Migration, retained review probe, API permission/audit, and reverse-consumer tests pass
  with the five-test PostgreSQL class twice and all independent gates green.

## Risk Level
High

## Done Checklist
- [ ] Execution plan and migration impact analysis written
- [ ] Failing integrity RED probe retained
- [ ] Relational pointer and frozen policy decision implemented
- [ ] Migration/backfill evidence saved
- [ ] Exact acceptance closure evidence and PostgreSQL twice-run saved
- [ ] Reverse consumers and complete gates passed
- [ ] Risk/review evidence completed and commit delegated to the orchestrator
