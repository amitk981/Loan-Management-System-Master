# Slice 006Z14: Member Authority Action and Calculation Proof Closure

## Status
Complete

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review

## Depends On
- 006Z13

## Runtime Capabilities

none

## Goal

Replace distributed and source-text authority claims with executable public proof that every member
action separates permission from persisted object scope and that every actorless active-member
calculation is reached only through an already-authorised owning boundary.

## Source / Review References

- `docs/source/auth-permissions.md` §§25.1, 32.1, and 34.2
- `docs/source/codebase-design.md` §§26.1-26.3, §27.1, and §§42.1-42.3
- `docs/source/functional-spec.md` M02-FR-004..006
- `docs/slices/006Z13-member-scope-persistence-and-action-matrix-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_083408_architecture_review`

## Concrete Requirements

1. Build one independently selectable module/HTTP matrix for member list, detail, update, identity
   approval, supply capture, supply verification, service/relaxation evidence create/update,
   active-status calculation, and active-status verification. Use a custom-role actor holding every
   named action permission but no `MemberScopeAssignment`; each row must return the documented
   nondisclosure error and preserve the complete member/evidence/maker/history/audit/workflow ledger.
2. Add only the matching `assigned` scope for each row and prove that row succeeds while at least
   one differently permissioned action remains denied. Independently prove `global`, `created_by`,
   active `team`, inactive-team, unrelated-team, and unrelated-member behavior without patching the
   authority evaluator.
3. Inventory the real production callers of `ActiveMemberStatusModule.calculate` by executable
   boundary behavior, not raw source strings or exact filenames. Staff eligibility must derive the
   member from an application that passed its action-specific object boundary; portal and borrower-
   limit paths must derive the member from authenticated/owned domain objects and reject client
   substitution.
4. Remove `calculate_for_actor` if no production public boundary owns it, or route the real staff
   boundary through it if source/API contracts require a direct member calculation action. Do not
   retain an unused security interface solely to satisfy a unit test.
5. Replace exact caller-set/string assertions with public interface tests plus the repository's
   established AST dependency guard only where a forbidden cross-module import cannot be observed
   through behavior.
6. Retain database constraints, immutable service-evidence maker history, BR-004/BR-006/BR-007
   calculations, and M02-FR-004..006 behavior unchanged.

## Test Cases

- Permission-without-scope and matching-scope rows for every named public action, with exact
  before/after state and no shared fixture that silently grants scope.
- Application-owned staff eligibility, authenticated portal ownership, and borrower-limit ownership
  each reject an attempted cross-member substitution and perform no writes.
- A harmless internal refactor that preserves public behavior does not fail an exact-filename or
  string-spelling assertion.

## Evidence Required

Failing independently selected authority/calculation rows, green complete action matrix, dependency
inventory, focused coverage, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Permission and object scope are separately executable facts for every public member action.
- No dead calculation authority seam or raw-source caller whitelist is treated as security proof.
