# Slice 006Z13: Member Scope Persistence and Action Matrix Closure

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review

## Depends On
- 006Z11

## Runtime Capabilities

none

## Goal

Make the persisted member-scope authority structurally valid at the database boundary and prove
that every public member action and calculation entry path consumes that authority without relying
on permission, role, or an actorless member identifier as object scope.

## Source / Review References

- `docs/source/auth-permissions.md` §§19.1, 25.1, 32.1, and 34.2
- `docs/source/codebase-design.md` §§26.1-27.1 and §§42.1-42.3
- `docs/slices/006Z11-member-scope-assignment-and-list-nondisclosure-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_055322_architecture_review`

## Concrete Requirements

1. Add database-enforced scope-type and field-shape constraints for `MemberScopeAssignment`:
   `global` and `created_by` name neither member nor team; `assigned` names exactly one member and
   no team; `team` names one member and one team. Invalid rows must fail even through `bulk_create`
   or direct ORM writes that bypass `save()/clean()`.
2. Enforce the intended uniqueness of global, created-by, assigned-member, and team-member grants
   despite nullable SQL uniqueness semantics. Duplicate grants must not create a second authority
   fact; preserve existing valid assignments with a non-destructive migration.
3. Add independently selected module and HTTP behavior for list, detail/update, identity approval,
   supply capture/verification, service/relaxation evidence maintenance, active-status calculation,
   and active-status verification. For each action, permission without the matching object scope is
   denied with the documented nondisclosure contract and complete zero business writes; adding only
   the matching scope enables only that action.
4. Treat `ActiveMemberStatusModule.calculate` as domain computation, not an object-access API. Map
   every production caller: staff paths must establish action-specific scope before calculation;
   portal paths must derive the member only from the authenticated `PortalAccount`. Add a dependency
   guard and public tests so no HTTP path can calculate an arbitrary caller-supplied member id.
5. Prove `global`, `team`, `assigned`, and `created_by` behavior with real queryset/action results,
   including inactive team membership, unrelated team/member assignments, and list totals computed
   after scope filtering. Do not patch the authority evaluator in acceptance tests.
6. Preserve the immutable service-evidence maker set and include its many-to-many rows in denial
   snapshots so a prior maker cannot become checker-eligible after another updater.

## Test Cases

- Direct invalid/duplicate assignment writes fail at the database boundary; every valid scope shape
  migrates and evaluates once.
- A custom-role actor holding every named action permission but no assignments is denied across the
  complete public matrix with identical before/after member/evidence/history/audit/workflow state.
- Adding one action-specific assigned grant enables that one row; global and active team grants
  expose only their intended rows; created-by never grants checker actions implicitly.
- Portal own-member calculation succeeds, cross-member substitution is impossible, and staff
  calculation cannot bypass the common authority boundary.
- Actor A creates evidence, actor B updates it, and both maker-link rows remain unchanged when A's
  verification is denied.

## Evidence Required

Failing database-constraint and permission-without-scope rows, green public module/HTTP action
matrix, migration proof, dependency scan, focused coverage, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Invalid or duplicate persisted authority cannot exist through an ORM path that bypasses model
  validation.
- Every public member action proves permission and object scope as separate observable facts.

