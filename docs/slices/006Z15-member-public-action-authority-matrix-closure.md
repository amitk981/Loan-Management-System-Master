# Slice 006Z15: Member Public-Action Authority Matrix Closure

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review

## Depends On
- 006Z14

## Runtime Capabilities

none

## Goal

Replace 006Z14's repeated authority-evaluator checks with independently selectable executions of
the real public member actions, so permission and persisted object scope are proved at the same
interfaces production callers use.

## Source / Review References

- `docs/source/auth-permissions.md` §§24.1, 25.1, 32.1, and 34.2
- `docs/source/codebase-design.md` §§26.1-26.3 and §§42.1-42.2
- `docs/source/functional-spec.md` M02-FR-004..006
- `docs/slices/006Z14-member-authority-action-and-calculation-proof-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_100911_architecture_review`

## Concrete Requirements

1. Replace the ten `evaluate_member_authority` aliases in
   `test_member_authority_action_matrix.py` with one independently selectable module/HTTP row per
   real action: member list, detail, update, identity-change approval, supply capture, supply
   verification, service-evidence create, service-evidence update, active-status calculation, and
   active-status verification. Each row must invoke the production boundary, not a copied predicate
   or private helper.
2. Give one custom-role actor every named action permission and no `MemberScopeAssignment`. Each
   public row must return the documented nondisclosure result (`403 OBJECT_ACCESS_DENIED`, or the
   matching module exception where no HTTP adapter exists) and preserve the complete member,
   identity request, supply/service/status, maker/history, audit, and workflow ledger.
3. Add only that row's matching persisted `assigned` scope, execute the same boundary successfully,
   and assert the exact response/write/evidence outcome. In the same arrangement prove at least one
   differently permissioned public action remains denied; an evaluator boolean is not acceptance.
4. Execute `global`, `created_by`, active-team, inactive-team, unrelated-team, and unrelated-member
   scope through representative real list/detail/mutation boundaries. Reuse the persisted scope
   model; do not patch the evaluator or infer global scope from role/permission provenance.
5. Exercise the three actorless calculation owners through their real entry points: staff
   eligibility derives the member from an object-authorised application; portal and borrower-limit
   routes derive it from the authenticated owned account/application. Query/body substitution of a
   different member must be rejected with no writes or identifier disclosure.
6. Keep `ActiveMemberStatusModule.calculate` actorless and internal unless a source-backed direct
   member calculation API exists. Do not restore `calculate_for_actor` or a filename/source-string
   caller whitelist. Retain only AST guards for dependency facts not observable through behavior.

## Test Cases

- Ten independently runnable public action rows, each with no-scope denial, exact unchanged ledger,
  matching-scope success, and a different-action denial.
- Real list/detail coverage for every persisted scope kind, including inactive and unrelated teams.
- Staff application, member portal, and borrower-limit cross-member substitution attempts.
- Omission checks that fail if a row invokes only `evaluate_member_authority` or skips the public
  response/write assertion.

## Evidence Required

Failing public-action rows before the correction, green independent rows and omission checks,
focused boundary inventory/coverage, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Every advertised member action earns authority evidence through its production interface.
- No permission-only evaluator result is presented as public object-access proof.

