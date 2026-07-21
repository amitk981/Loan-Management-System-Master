# Slice 010N6: Interest Portfolio Identity Closure

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Depends On
- 010N5

## Runtime Capabilities

none

## Goal
Make complete interest collections and multi-batch accruals prove stable unique membership, so a
101-row response cannot silently represent only 100 distinct scoped loans.

## Review Finding Closure
| Finding ID | Root ID | Reproducer | Acceptance IDs |
|---|---|---|---|
| AR-010-INTEREST-UI-001 | ROOT-010-INTEREST-PORTFOLIO-COMPLETENESS | .ralph/runs/2026-07-22_031437_architecture_review/evidence/review-probes/interest-portfolio-identity.log | AC-E10-I4, AC-E10-I5, AC-E10-I6 |

## Source References
- `docs/slices/010N3-interest-portfolio-completeness-closure.md` requirements 1–4
- `docs/source/api-contracts.md` §§8.1, 33.1–33.7, and 45
- `docs/source/codebase-design.md` §42.3
- `docs/working/FRONTEND_DESIGN_RULES.md`

## Concrete Requirements
1. Extend the shared complete-pagination boundary with a stable identity contract. Reject duplicates
   within or across pages, inconsistent page occupancy/continuation, and any response whose unique
   identity count differs from canonical `total_count`; callers must name the resource identity.
2. Validate the whole selected loan set before the first financial batch and reject duplicate loan
   ids across batches. A result count, progress message, or success state must never equate row count
   with unique portfolio membership.
3. Add 1/100/101 service and component matrices where page two repeats page-one boundary rows,
   omits loan 101, changes metadata, or returns duplicate/out-of-order batch membership. Preserve
   successful explicit-batch disclosure and already-completed partial results after later denial.
4. Reuse the shared pagination and existing screen patterns; do not add styling, client-side money,
   or permission policy.

## Acceptance Criteria
- [AC-E10-I4] Complete loan and invoice reads reject duplicate, missing, unstable, or count-incoherent
  identities before exposing a complete collection.
- [AC-E10-I5] Portfolio accrual validates one globally unique selected set before mutation and a
  101-row/100-identity selection cannot start or report success.
- [AC-E10-I6] Perfect 1/100/101, replay, later-batch denial, malformed-page, and duplicate-boundary
  matrices pass with the current review reproducer green and no regression to existing UI states.

## Risk Level
High
