# Slice 007C3: Approval-Case Source Read-Scope Closure

## Status
Complete

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007D

## Runtime Capabilities

none

## Goal

Restore the source-required read-only sanction-package access for the Credit Manager, Company
Secretary, and Auditor without regressing 007C2's rule that `approvals.case.read` alone never gives
global object scope.

## Source / Review References

- `docs/source/auth-permissions.md` §14.1, §19.1, §26.3, §27.1, §32.1, and §37.3
- `docs/source/codebase-design.md` §§26.1-26.3, §27.1, and §42.2
- `docs/slices/007C2-approval-case-read-scope-and-snapshot-contract-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_131622_architecture_review`

## Concrete Requirements

1. Persist an approval-case read-scope grant separate from action permission. The grant must name
   an active role and one bounded scope type: `legal_readonly`, `audit_readonly`, or
   `management_readonly`; role plus scope type is unique, inactive grants do not authorise reads,
   and the migration seeds only the source-named Company Secretary and Internal Auditor read-only
   grants. Do not infer scope from `approvals.case.read`, `management_readonly`, display text, or a
   caller query flag.
2. Seed `approvals.case.read` for Credit Manager, Company Secretary, and Internal Auditor as source
   §14.1/§26.3 require. Credit Manager object scope is limited to a case they submitted or the
   application/appraisal they own through the existing credit object boundary; it is not a global
   approval scope. Company Secretary and Auditor access requires their persisted read-scope grant.
3. Extend the single approval-owned `can_read_approval_case` boundary to return an attributable
   scope decision used before collection counts/pagination and detail serialization. Preserve
   immutable required-approver/acted-history access and the unassigned-Director/custom-permission
   denial from 007C2.
4. Read-only scope never enables approve/reject/return, never places a user in
   `assigned_to_me=true`, and never changes `available_actions`. Direct detail and ordinary list
   must agree on visibility; filtered counts must not disclose inaccessible cases.
5. Move the current Python-wide list scan behind an approval-owned selector that narrows by the
   actor's persisted scope before pagination. Any unavoidable JSON coherence check may run after
   the database filter, but the module must not materialize every approval case for each request.

## Test Cases

- Credit Manager sees their submitted sanction package but not an unrelated package.
- Persistently granted Company Secretary and Internal Auditor can list/retrieve routed cases
  read-only; removing/deactivating the grant immediately removes access.
- The same users never enter assigned queues and every action remains disabled/denied with the
  complete case/action/sanction/audit/workflow/notification ledger unchanged.
- Unassigned Director and arbitrary `approvals.case.read` holder remain empty-list/403 as 007C2
  requires; pagination counts are scoped before serialization.
- Query-count/selector regression proves list work is bounded by the actor scope rather than total
  repository case count.

## Evidence Required

Failing source-role reads before the correction, green role/scope/object matrix, selector/query
evidence, complete denial ledgers, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Every source-named read-only role can inspect exactly its persisted sanction-package scope.
- Action permission and read-only scope remain independent; no permission-only global read returns.
