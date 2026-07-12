# Slice 006Z11: Member Scope Assignment and List Nondisclosure Closure

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review

## Depends On
- 006Z9

## Runtime Capabilities

none

## Goal

Replace the 006Z9 assumption that an action permission is itself row-independent global member
scope with one explicit assignment/management projection, and make member list, detail, identity
approval, evidence maintenance, and active verification use it consistently.

## Source / Review References

- `docs/source/auth-permissions.md` §§3-3.1, §19.1, §25.1, and §34.2
- `docs/source/codebase-design.md` §§26.1-27.1 and §§42.1-42.3
- `docs/slices/006Z9-active-member-authority-and-decision-contract-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_044409_architecture_review`

## Concrete Requirements

1. `members.member.read`, `members.active_status.verify`, and
   `members.member.identity_change.approve` remain action permissions only; possession of one must
   not silently grant `global` scope. Field Officers with `members.member.read` remain limited to
   created/assigned/team members, as §25.1 requires.
2. Introduce one persisted or configuration-backed member-scope assignment understood by the
   member-authority module (`global`, `team`, `assigned`, `created_by`, or denied). Do not derive it
   from `Role.is_system_role`, a role-name switch, an unowned row, or a caller Boolean. If the source
   does not name the management assignee, keep the grant configurable and seed no new business
   authority.
3. Apply the same projection to list and detail reads, member update/identity approval, supply and
   service/relaxation evidence maintenance, calculation, and verification. List pagination counts
   and filters must be computed after the scope predicate so excluded members cannot be inferred.
4. Preserve maker-checker separation independently of object scope: an assigned/global actor still
   cannot verify evidence they captured, verified, created, or materially updated. Preserve the
   creator and every material updater as immutable provenance; replacing `verified_by_user` must
   not erase a prior maker and make that actor eligible to verify the derived status.
5. Replace A-072's temporary permission-as-global assumption with the final assignment contract and
   document the exact list/detail nondisclosure behavior in `API_CONTRACTS.md`.

## Test Cases

- Field Officer and arbitrary custom role with `members.member.read`: owned/assigned rows visible;
  unrelated and unowned rows absent from list and denied on detail with no count/existence leak.
- Explicit management/global assignment: the same rows are visible without role-provenance checks.
- Verify and identity-approve permissions without object assignment remain denied; adding assignment
  enables only the named action and does not bypass maker-checker.
- Actor A creates service/relaxation evidence, actor B updates it, then A attempts active-status
  verification: deny with zero status/history/audit/workflow writes.
- Independently selected public module and HTTP rows cover every action, list pagination totals, and
  complete zero-write evidence on denial.

## Evidence Required

Failing permission-is-not-global list/detail/verify tests, green assignment/action matrix, dependency
scan proving no role/caller bypass, API contract diff, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Action permission and member object scope are separate, reviewable facts.
- Member lists and detail/actions enforce one source-backed scope without disclosing unrelated rows.

