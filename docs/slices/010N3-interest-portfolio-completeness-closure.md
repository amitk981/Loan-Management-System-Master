# Slice 010N3: Interest Portfolio Completeness Closure

## Status
Complete

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Depends On
- 010N2

## Runtime Capabilities

none

## Goal
Make every staff interest read and portfolio accrual action truthful beyond the first 100 scoped
loans, with the backend retaining population and permission authority.

## Review Finding Closure
| Finding ID | Root ID | Reproducer | Acceptance IDs |
|---|---|---|---|
| AR-010-INTEREST-UI-001 | ROOT-010-INTEREST-PORTFOLIO-COMPLETENESS | .ralph/runs/2026-07-21_202321_architecture_review/evidence/review-probes/interest-portfolio-completeness.log | AC-E10-I1, AC-E10-I2, AC-E10-I3 |

## Source References
- `docs/slices/010MB-interest-and-monitoring-frontend-wiring.md`
- `docs/source/api-contracts.md` §§33.1–33.7 and 45
- `docs/source/screen-spec.md` S47–S49
- `docs/source/codebase-design.md` §42.3
- `docs/working/FRONTEND_DESIGN_RULES.md`

## Concrete Requirements
1. A portfolio-wide monthly accrual must omit explicit ids and let the canonical backend owner select
   its complete bounded scoped set, or present explicitly selected batches with full continuation and
   membership disclosure. Never pass a page-one account array as the complete financial population.
2. Traverse or visibly paginate canonical loan and invoice collections so loan/invoice 101 remains
   selectable and visible. Counts, pages, rows, action results, and refreshes must consume the same
   scoped owner and fail visibly on malformed or partial pagination.
3. Render mutation availability from backend-owned action projections. Client permission arrays may
   hide controls early but cannot create authority or claim a complete financial operation.
4. Add component/service regression matrices at 1/100/101 records for complete-set accrual, explicit
   batch behavior, invoice/account selection, replay, backend denial, and one-page failure. Preserve
   existing styling and the standard error/success patterns.

## Acceptance Criteria
- [AC-E10-I1] One portfolio action covers every canonical scoped loan or identifies an explicit
  selected batch; a 101st loan can never be silently omitted from a successful complete-set accrual.
- [AC-E10-I2] Loan and invoice reads expose truthful page/count/continuation state and make record 101
  reachable without fabricating local money, status, or permission policy.
- [AC-E10-I3] 1/100/101, replay, denial, malformed-response, and partial-failure tests pass with the
  original reproducer command GREEN and all independent gates green.

## Risk Level
High

