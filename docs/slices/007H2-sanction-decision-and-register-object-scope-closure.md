# Slice 007H2: Sanction Decision and Register Object-Scope Closure

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007G2

## Runtime Capabilities

none

## Goal

Keep permissioned sanction-decision and register reads inside the same application/case object
scope that governs approval history, including counts and pagination.

## Source / Review References

- `docs/source/api-contracts.md` §§8, 25.8, and 25.9
- `docs/source/auth-permissions.md` §§15.8-15.9, 19.1-19.2, 32.1, 34.5, and 37.3
- `docs/source/functional-spec.md` M05-FR-009 and the 15 Credit Sanction Register fields
- `docs/source/codebase-design.md` §§13.1, 26.3, 27.1, and 42.1-42.2
- `docs/slices/007H-credit-sanction-register.md` requirements 2-4
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_200023_architecture_review`

## Concrete Requirements

1. `GET /loan-applications/{id}/sanction-decision/` requires both
   `approvals.sanction.read` and the canonical approval/application object decision. An assigned,
   effective, or acted approver may read their case's decision; an otherwise same-permission
   Director receives nondisclosing `403 OBJECT_ACCESS_DENIED` for an unrelated application. Source-
   backed persisted legal/audit/management readers retain their defined read-only scope.
2. Credit Sanction Register collection filtering delegates to the canonical approval-case selector
   before count, financial-year/decision filters, ordering, and pagination. A Director sees only
   attributable cycles and cannot infer other rows from `total_count`, page bounds, or filters;
   globally scoped CFO/legal/audit readers see only the scope their persisted grant defines.
3. Permission and object scope stay separate: possessing register/sanction permission does not make
   case permission global, and a case reader without the specific register/sanction permission
   remains forbidden. Register reads never grant action or document-download authority.
4. Preserve the frozen 15-field row, immutable generation, 404-before-approval/after-rejection
   sanction-decision contract, FY filters, and distinct case/exception/meeting references. Update
   `API_CONTRACTS.md`, the role-seed tests, Epic 007 digest, and frontend run-ahead contracts with
   exact row-scope semantics.

## Test Cases

- Two unrelated terminal cases with same-permission Directors: each decision/detail/register read
  exposes only attributable data and exact scoped counts; direct cross-case reads are nondisclosing.
- CFO, Company Secretary legal reader, Internal Auditor audit reader, Credit Manager, unused
  committee candidate, conflicted original, effective alternate, and acted historical actor matrix
  across approved/rejected/returned cycles.
- Permission-only and object-only negatives, invalid filters, empty pages, and page-boundary cases
  prove filtering occurs before count/pagination with zero writes.

## Risk Level
High

## Acceptance Criteria

- No same-permission user can read or count an unrelated sanction decision/register row.
- Source-backed global/read-only scopes remain explicit and do not create action authority.
- All configured gates pass with public role/object regression evidence.

